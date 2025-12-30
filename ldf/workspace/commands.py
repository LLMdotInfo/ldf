"""Workspace CLI commands for multi-project management.

This module provides the 'ldf workspace' command group for managing
multi-project workspaces with shared resources and cross-project references.
"""

import json
from pathlib import Path

import click
import yaml

from ldf.project_resolver import WORKSPACE_MANIFEST, find_workspace_root
from ldf.utils.console import console
from ldf.utils.logging import get_logger

logger = get_logger(__name__)


@click.group()
def workspace():
    """Manage multi-project workspaces.

    Workspaces allow you to manage multiple LDF projects together with
    shared guardrails, templates, and cross-project spec references.

    \b
    Getting Started:
      ldf workspace init          # Initialize a workspace
      ldf workspace list          # List projects in workspace
      ldf workspace add <path>    # Add a project to workspace

    \b
    Maintenance:
      ldf workspace sync          # Rebuild registry, validate refs
      ldf workspace report        # Generate aggregated report
      ldf workspace graph         # Show dependency graph
    """
    pass


@workspace.command()
@click.option(
    "--name",
    "-n",
    help="Workspace name (default: directory name)",
)
@click.option(
    "--discover",
    "-d",
    is_flag=True,
    help="Auto-discover LDF projects in subdirectories",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing workspace manifest",
)
@click.option(
    "--create-shared/--no-create-shared",
    default=True,
    help="Create .ldf-shared/ directory structure",
)
def init(name: str | None, discover: bool, force: bool, create_shared: bool):
    """Initialize a new workspace.

    Creates ldf-workspace.yaml and optionally .ldf-shared/ for organization
    guardrails and templates.

    \b
    Examples:
      ldf workspace init                    # Basic initialization
      ldf workspace init --name my-platform # With custom name
      ldf workspace init --discover         # Auto-find existing LDF projects
      ldf workspace init --force            # Overwrite existing workspace
    """
    workspace_root = Path.cwd()
    manifest_path = workspace_root / WORKSPACE_MANIFEST

    # Check for existing workspace
    if manifest_path.exists() and not force:
        console.print(f"[yellow]Workspace already exists at {manifest_path}[/yellow]")
        console.print("Use [cyan]--force[/cyan] to overwrite.")
        raise SystemExit(1)

    # Determine workspace name
    workspace_name = name or workspace_root.name

    # Discover existing LDF projects
    discovered_projects = []
    if discover:
        console.print("[dim]Discovering LDF projects...[/dim]")
        discovered_projects = _discover_ldf_projects(workspace_root)
        if discovered_projects:
            console.print(f"[green]Found {len(discovered_projects)} LDF project(s):[/green]")
            for proj in discovered_projects:
                console.print(f"  - {proj['alias']}: {proj['path']}")
        else:
            console.print("[dim]No LDF projects found.[/dim]")

    # Build manifest structure
    manifest_data = {
        "version": "1.0",
        "name": workspace_name,
        "projects": {
            "explicit": [{"path": p["path"], "alias": p["alias"]} for p in discovered_projects],
            "discovery": {
                "patterns": ["**/.ldf/config.yaml"],
                "exclude": ["node_modules", ".venv", "vendor", ".git"],
            },
        },
        "shared": {
            "path": ".ldf-shared/",
            "inherit": {
                "guardrails": True,
                "templates": True,
                "question_packs": True,
                "macros": True,
            },
        },
        "references": {
            "enabled": True,
        },
        "reporting": {
            "enabled": True,
            "output_dir": ".ldf-reports/",
        },
    }

    # Write manifest
    with open(manifest_path, "w") as f:
        yaml.safe_dump(manifest_data, f, default_flow_style=False, sort_keys=False)

    console.print(f"[green]✓[/green] Created {WORKSPACE_MANIFEST}")

    # Create .ldf-shared/ structure if requested
    if create_shared:
        shared_dir = workspace_root / ".ldf-shared"
        _create_shared_structure(shared_dir)

    # Create .ldf-workspace/ for registry cache
    workspace_state_dir = workspace_root / ".ldf-workspace"
    workspace_state_dir.mkdir(exist_ok=True)
    (workspace_state_dir / ".gitignore").write_text("*\n")

    console.print()
    console.print("[bold]Workspace initialized![/bold]")
    console.print()
    console.print("Next steps:")
    if not discovered_projects:
        console.print("  1. Add projects: [cyan]ldf workspace add ./path/to/project[/cyan]")
    console.print("  2. List projects: [cyan]ldf workspace list[/cyan]")
    console.print("  3. Run commands:  [cyan]ldf -p <alias> lint[/cyan]")


@workspace.command("list")
@click.option(
    "--format",
    type=click.Choice(["rich", "json", "text"]),
    default="rich",
    help="Output format",
)
def list_projects(format: str):
    """List all projects in the workspace.

    Shows project aliases, paths, LDF status, and coverage information.

    \b
    Examples:
      ldf workspace list              # Rich table output
      ldf workspace list --format json  # JSON for scripting
    """
    from ldf.detection import detect_workspace_state

    workspace_root = find_workspace_root()
    if not workspace_root:
        console.print("[red]Not in a workspace.[/red]")
        console.print("Run [cyan]ldf workspace init[/cyan] to create one.")
        raise SystemExit(1)

    state = detect_workspace_state(workspace_root)

    if state["status"] != "ok":
        console.print(f"[red]Error: {state.get('error', 'Unknown error')}[/red]")
        raise SystemExit(1)

    if format == "json":
        print(json.dumps(state, indent=2, default=str))
        return

    if format == "text":
        print(f"Workspace: {state['name']}")
        print(f"Root: {workspace_root}")
        print()
        for proj in state["projects"]:
            status = proj["state"].upper()
            print(f"{proj['alias']}: {proj['path']} ({status})")
        return

    # Rich output
    from rich.table import Table

    console.print()
    console.print(f"[bold]Workspace:[/bold] {state['name']}")
    console.print(f"[bold]Root:[/bold] {workspace_root}")
    console.print()

    table = Table(show_header=True)
    table.add_column("Alias", style="cyan")
    table.add_column("Path")
    table.add_column("State")
    table.add_column("Version")

    state_colors = {
        "current": "[green]current[/green]",
        "outdated": "[yellow]outdated[/yellow]",
        "legacy": "[yellow]legacy[/yellow]",
        "partial": "[yellow]partial[/yellow]",
        "corrupted": "[red]corrupted[/red]",
        "new": "[blue]new[/blue]",
        "missing": "[red]missing[/red]",
    }

    for proj in state["projects"]:
        state_display = state_colors.get(proj["state"], proj["state"])
        version = proj["version"] or "-"
        table.add_row(proj["alias"], proj["path"], state_display, version)

    console.print(table)

    # Show shared resources info
    if state["shared"]["exists"]:
        console.print()
        console.print("[bold]Shared Resources:[/bold]")
        console.print(f"  Path: {state['shared']['path']}")
        if state["shared"].get("has_guardrails"):
            console.print("  [green]✓[/green] Guardrails")
        if state["shared"].get("has_templates"):
            console.print("  [green]✓[/green] Templates")


@workspace.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option(
    "--alias",
    "-a",
    help="Custom alias for the project (default: directory name)",
)
def add(project_path: str, alias: str | None):
    """Add a project to the workspace.

    The project must be an existing directory. If it doesn't have
    LDF initialized, run 'ldf init' in that directory first.

    \b
    Examples:
      ldf workspace add ./services/auth        # Add with auto-generated alias
      ldf workspace add ./billing -a billing   # Add with custom alias
    """
    workspace_root = find_workspace_root()
    if not workspace_root:
        console.print("[red]Not in a workspace.[/red]")
        console.print("Run [cyan]ldf workspace init[/cyan] to create one.")
        raise SystemExit(1)

    project_abs = Path(project_path).resolve()

    # Calculate relative path from workspace root
    try:
        relative_path = project_abs.relative_to(workspace_root)
    except ValueError:
        console.print("[red]Project must be within the workspace directory.[/red]")
        raise SystemExit(1)

    # Determine alias
    project_alias = alias or project_abs.name

    # Load existing manifest
    manifest_path = workspace_root / WORKSPACE_MANIFEST
    with open(manifest_path) as f:
        manifest_data = yaml.safe_load(f) or {}

    # Ensure projects.explicit exists
    if "projects" not in manifest_data:
        manifest_data["projects"] = {}
    if "explicit" not in manifest_data["projects"]:
        manifest_data["projects"]["explicit"] = []

    # Check for duplicate alias
    existing_aliases = [p.get("alias") for p in manifest_data["projects"]["explicit"]]
    if project_alias in existing_aliases:
        console.print(f"[red]Alias '{project_alias}' already exists in workspace.[/red]")
        console.print("Use [cyan]--alias[/cyan] to specify a different alias.")
        raise SystemExit(1)

    # Check for duplicate path
    existing_paths = [p.get("path") for p in manifest_data["projects"]["explicit"]]
    if str(relative_path) in existing_paths:
        console.print(f"[yellow]Project '{relative_path}' is already in workspace.[/yellow]")
        return

    # Add the project
    manifest_data["projects"]["explicit"].append(
        {
            "path": str(relative_path),
            "alias": project_alias,
        }
    )

    # Write updated manifest
    with open(manifest_path, "w") as f:
        yaml.safe_dump(manifest_data, f, default_flow_style=False, sort_keys=False)

    # Check if project has LDF initialized
    has_ldf = (project_abs / ".ldf" / "config.yaml").exists()

    console.print(f"[green]✓[/green] Added project '{project_alias}' ({relative_path})")

    if not has_ldf:
        console.print()
        console.print("[yellow]Note: Project doesn't have LDF initialized.[/yellow]")
        console.print(f"Run [cyan]cd {project_path} && ldf init[/cyan] to initialize it.")


@workspace.command()
@click.option(
    "--rebuild-registry/--no-rebuild-registry",
    default=True,
    help="Rebuild project registry cache",
)
@click.option(
    "--validate-refs/--no-validate-refs",
    default=True,
    help="Validate cross-project references",
)
def sync(rebuild_registry: bool, validate_refs: bool):
    """Synchronize workspace state.

    Rebuilds the project registry cache and validates cross-project
    references. Run this after adding or removing projects.

    \b
    Examples:
      ldf workspace sync              # Full sync
      ldf workspace sync --no-validate-refs  # Skip reference validation
    """
    from ldf.detection import detect_workspace_state

    workspace_root = find_workspace_root()
    if not workspace_root:
        console.print("[red]Not in a workspace.[/red]")
        console.print("Run [cyan]ldf workspace init[/cyan] to create one.")
        raise SystemExit(1)

    console.print("[dim]Syncing workspace...[/dim]")
    console.print()

    # Detect workspace state (this validates manifest and projects)
    state = detect_workspace_state(workspace_root)

    if state["status"] != "ok":
        console.print(f"[red]Error: {state.get('error', 'Unknown error')}[/red]")
        raise SystemExit(1)

    # Rebuild registry
    if rebuild_registry:
        console.print("[bold]Rebuilding registry...[/bold]")
        _rebuild_registry(workspace_root, state)
        console.print("[green]✓[/green] Registry updated")

    # Validate references
    if validate_refs:
        from ldf.lint import lint_workspace_references

        console.print()
        console.print("[bold]Validating references...[/bold]")
        ref_exit_code = lint_workspace_references(workspace_root, "rich")
        if ref_exit_code != 0:
            console.print()
            console.print("[yellow]⚠[/yellow] Reference validation found issues (see above)")

    console.print()
    console.print("[green]Sync complete![/green]")


def _discover_ldf_projects(workspace_root: Path) -> list[dict]:
    """Discover LDF projects in subdirectories.

    Args:
        workspace_root: Workspace root directory

    Returns:
        List of dicts with 'path' and 'alias' keys
    """
    projects = []
    exclude_dirs = {"node_modules", ".venv", "vendor", ".git", ".ldf-shared", ".ldf-workspace"}

    for config_path in workspace_root.rglob(".ldf/config.yaml"):
        # Check if any parent is in exclude list
        parts = config_path.relative_to(workspace_root).parts
        if any(part in exclude_dirs for part in parts):
            continue

        # Get project directory (parent of .ldf)
        project_dir = config_path.parent.parent
        relative_path = project_dir.relative_to(workspace_root)

        # Skip if project is at workspace root
        if relative_path == Path("."):
            continue

        projects.append(
            {
                "path": str(relative_path),
                "alias": project_dir.name,
            }
        )

    return sorted(projects, key=lambda x: x["path"])


def _create_shared_structure(shared_dir: Path) -> None:
    """Create the .ldf-shared/ directory structure."""
    shared_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (shared_dir / "guardrails").mkdir(exist_ok=True)
    (shared_dir / "templates").mkdir(exist_ok=True)
    (shared_dir / "question-packs").mkdir(exist_ok=True)
    (shared_dir / "macros").mkdir(exist_ok=True)

    # Create placeholder README
    readme = shared_dir / "README.md"
    if not readme.exists():
        readme.write_text("""# Shared LDF Resources

This directory contains organization-wide LDF resources that are
inherited by all projects in the workspace.

## Directory Structure

- `guardrails/` - Shared guardrail definitions (merged with project guardrails)
- `templates/` - Shared spec templates (used as fallback)
- `question-packs/` - Shared question packs
- `macros/` - Shared macro definitions

## Usage

Projects inherit these resources based on their `workspace.inherit_shared`
setting in `.ldf/config.yaml`. Project-level resources take precedence
over shared resources when there are conflicts.
""")

    console.print("[green]✓[/green] Created .ldf-shared/ structure")


@workspace.command()
@click.option(
    "--format",
    type=click.Choice(["rich", "json", "html"]),
    default="rich",
    help="Output format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (default: stdout for json, .ldf-reports/ for html)",
)
def report(format: str, output: str | None):
    """Generate aggregated workspace report.

    Aggregates coverage, lint status, and spec counts across all
    projects in the workspace.

    \b
    Examples:
      ldf workspace report              # Rich terminal output
      ldf workspace report --format json  # JSON for automation
      ldf workspace report --format html -o report.html  # HTML dashboard
    """
    from ldf.detection import detect_project_state

    workspace_root = find_workspace_root()
    if not workspace_root:
        console.print("[red]Not in a workspace.[/red]")
        console.print("Run [cyan]ldf workspace init[/cyan] to create one.")
        raise SystemExit(1)

    # Load workspace manifest
    manifest_path = workspace_root / WORKSPACE_MANIFEST
    with open(manifest_path) as f:
        data = yaml.safe_load(f) or {}

    from ldf.models.workspace import WorkspaceManifest

    manifest = WorkspaceManifest.from_dict(data)

    # Gather project data
    projects_data = []
    total_specs = 0
    total_coverage = 0
    coverage_count = 0

    for entry in manifest.get_all_project_entries(workspace_root):
        project_path = (workspace_root / entry.path).resolve()
        project_info = {
            "alias": entry.alias,
            "path": entry.path,
            "exists": project_path.exists(),
            "has_ldf": (project_path / ".ldf" / "config.yaml").exists(),
            "specs": [],
            "spec_count": 0,
            "state": "unknown",
            "coverage": None,
        }

        if project_info["has_ldf"]:
            # Get project state
            detection = detect_project_state(project_path)
            project_info["state"] = detection.state.value

            # Count specs
            specs_dir = project_path / ".ldf" / "specs"
            if specs_dir.exists():
                spec_names = [d.name for d in specs_dir.iterdir() if d.is_dir()]
                project_info["specs"] = spec_names
                project_info["spec_count"] = len(spec_names)
                total_specs += len(spec_names)

            # Try to get coverage (from registry or calculate)
            registry_path = workspace_root / ".ldf-workspace" / ".registry.yaml"
            if registry_path.exists():
                try:
                    with open(registry_path) as f:
                        registry = yaml.safe_load(f) or {}
                    if entry.alias in registry.get("projects", {}):
                        proj_data = registry["projects"][entry.alias]
                        if "coverage" in proj_data:
                            project_info["coverage"] = proj_data["coverage"]
                            total_coverage += proj_data["coverage"]
                            coverage_count += 1
                except (OSError, yaml.YAMLError, AttributeError, TypeError, KeyError) as e:
                    logger.debug(f"Registry not available for {entry.alias}: {e}")

        projects_data.append(project_info)

    # Calculate averages
    avg_coverage = total_coverage / coverage_count if coverage_count > 0 else None

    report_data = {
        "workspace": manifest.name,
        "workspace_root": str(workspace_root),
        "summary": {
            "total_projects": len(projects_data),
            "total_specs": total_specs,
            "average_coverage": avg_coverage,
            "projects_with_ldf": sum(1 for p in projects_data if p["has_ldf"]),
        },
        "projects": projects_data,
    }

    if format == "json":
        output_content = json.dumps(report_data, indent=2, default=str)
        if output:
            Path(output).write_text(output_content)
            console.print(f"[green]✓[/green] Report written to {output}")
        else:
            print(output_content)
    elif format == "html":
        html_content = _generate_html_report(report_data)
        output_path = output or (workspace_root / ".ldf-reports" / "workspace-report.html")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html_content)
        console.print(f"[green]✓[/green] HTML report written to {output_path}")
    else:
        # Rich output
        _print_rich_report(report_data)


@workspace.command()
@click.option(
    "--format",
    type=click.Choice(["mermaid", "dot", "json"]),
    default="mermaid",
    help="Output format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (default: stdout)",
)
def graph(format: str, output: str | None):
    """Generate project dependency graph.

    Shows cross-project spec references as a dependency graph.

    \b
    Examples:
      ldf workspace graph                # Mermaid diagram (terminal)
      ldf workspace graph --format dot   # Graphviz DOT format
      ldf workspace graph --format json  # JSON for tooling
      ldf workspace graph -o deps.md     # Write to file
    """
    from ldf.utils.references import build_dependency_graph

    workspace_root = find_workspace_root()
    if not workspace_root:
        console.print("[red]Not in a workspace.[/red]")
        console.print("Run [cyan]ldf workspace init[/cyan] to create one.")
        raise SystemExit(1)

    graph_data = build_dependency_graph(workspace_root)

    if format == "json":
        # Convert sets to lists for JSON
        json_graph = {k: list(v) for k, v in graph_data.items()}
        output_content = json.dumps(json_graph, indent=2)
    elif format == "dot":
        output_content = _generate_dot_graph(graph_data, workspace_root)
    else:  # mermaid
        output_content = _generate_mermaid_graph(graph_data, workspace_root)

    if output:
        Path(output).write_text(output_content)
        console.print(f"[green]✓[/green] Graph written to {output}")
    else:
        print(output_content)


def _print_rich_report(report_data: dict) -> None:
    """Print a rich formatted workspace report."""
    from rich.panel import Panel
    from rich.table import Table

    console.print()
    console.print(Panel(f"[bold]{report_data['workspace']}[/bold] Workspace Report"))
    console.print()

    # Summary
    summary = report_data["summary"]
    console.print("[bold]Summary[/bold]")
    total = summary["total_projects"]
    with_ldf = summary["projects_with_ldf"]
    console.print(f"  Projects: {total} ({with_ldf} with LDF)")
    console.print(f"  Total Specs: {summary['total_specs']}")
    if summary["average_coverage"]:
        console.print(f"  Average Coverage: {summary['average_coverage']:.1f}%")
    console.print()

    # Projects table
    table = Table(show_header=True)
    table.add_column("Project", style="cyan")
    table.add_column("Path")
    table.add_column("State")
    table.add_column("Specs", justify="right")
    table.add_column("Coverage", justify="right")

    state_colors = {
        "current": "[green]current[/green]",
        "outdated": "[yellow]outdated[/yellow]",
        "legacy": "[yellow]legacy[/yellow]",
        "new": "[blue]new[/blue]",
        "missing": "[red]missing[/red]",
    }

    for proj in report_data["projects"]:
        state_display = state_colors.get(proj["state"], proj["state"])
        coverage = f"{proj['coverage']:.0f}%" if proj["coverage"] else "-"
        table.add_row(
            proj["alias"],
            proj["path"],
            state_display,
            str(proj["spec_count"]),
            coverage,
        )

    console.print(table)


def _generate_html_report(report_data: dict) -> str:
    """Generate an HTML workspace report."""
    summary = report_data["summary"]
    projects_html = ""

    for proj in report_data["projects"]:
        state_class = "success" if proj["state"] == "current" else "warning"
        coverage = f"{proj['coverage']:.0f}%" if proj["coverage"] else "-"
        projects_html += f"""
        <tr>
            <td><strong>{proj["alias"]}</strong></td>
            <td>{proj["path"]}</td>
            <td><span class="{state_class}">{proj["state"]}</span></td>
            <td>{proj["spec_count"]}</td>
            <td>{coverage}</td>
        </tr>
        """

    avg_coverage = f"{summary['average_coverage']:.1f}%" if summary["average_coverage"] else "N/A"

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{report_data["workspace"]} - Workspace Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 40px;
        }}
        h1 {{ color: #333; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .card {{ background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; }}
        .card h3 {{ margin: 0; font-size: 2em; color: #333; }}
        .card p {{ margin: 5px 0 0; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
    </style>
</head>
<body>
    <h1>{report_data["workspace"]} Workspace Report</h1>

    <div class="summary">
        <div class="card">
            <h3>{summary["total_projects"]}</h3>
            <p>Projects</p>
        </div>
        <div class="card">
            <h3>{summary["total_specs"]}</h3>
            <p>Specs</p>
        </div>
        <div class="card">
            <h3>{avg_coverage}</h3>
            <p>Avg Coverage</p>
        </div>
    </div>

    <h2>Projects</h2>
    <table>
        <thead>
            <tr>
                <th>Project</th>
                <th>Path</th>
                <th>State</th>
                <th>Specs</th>
                <th>Coverage</th>
            </tr>
        </thead>
        <tbody>
            {projects_html}
        </tbody>
    </table>

    <p style="color: #999; margin-top: 40px;">Generated by LDF</p>
</body>
</html>
"""


def _generate_mermaid_graph(graph_data: dict[str, set[str]], workspace_root: Path) -> str:
    """Generate a Mermaid diagram of the dependency graph."""
    lines = ["graph LR"]

    if not graph_data:
        lines.append("    NoRefs[No cross-project references]")
        return "\n".join(lines)

    # Collect all nodes
    all_nodes = set(graph_data.keys())
    for deps in graph_data.values():
        all_nodes.update(deps)

    # Add nodes
    for node in sorted(all_nodes):
        lines.append(f"    {node}[{node}]")

    # Add edges
    for source, targets in sorted(graph_data.items()):
        for target in sorted(targets):
            lines.append(f"    {source} --> {target}")

    return "\n".join(lines)


def _generate_dot_graph(graph_data: dict[str, set[str]], workspace_root: Path) -> str:
    """Generate a Graphviz DOT diagram of the dependency graph."""
    lines = ["digraph workspace {", "    rankdir=LR;", "    node [shape=box];"]

    if not graph_data:
        lines.append('    "No cross-project references";')
    else:
        for source, targets in sorted(graph_data.items()):
            for target in sorted(targets):
                lines.append(f'    "{source}" -> "{target}";')

    lines.append("}")
    return "\n".join(lines)


@workspace.command("validate-refs")
@click.option(
    "--format",
    type=click.Choice(["rich", "json", "text"]),
    default="rich",
    help="Output format",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed reference information",
)
def validate_refs(format: str, verbose: bool):
    """Validate all cross-project references.

    Checks that all @project:spec references in the workspace
    point to valid specs and detects circular dependencies.

    \b
    Examples:
      ldf workspace validate-refs              # Rich output
      ldf workspace validate-refs --format json  # JSON for scripting
      ldf workspace validate-refs --verbose    # Show deduplication info
    """
    from ldf.lint import lint_workspace_references

    workspace_root = find_workspace_root()
    if not workspace_root:
        console.print("[red]Not in a workspace.[/red]")
        console.print("Run [cyan]ldf workspace init[/cyan] to create one.")
        raise SystemExit(1)

    exit_code = lint_workspace_references(workspace_root, format, verbose=verbose)
    raise SystemExit(exit_code)


def _rebuild_registry(workspace_root: Path, state: dict) -> None:
    """Rebuild the workspace registry cache.

    Args:
        workspace_root: Workspace root directory
        state: Workspace state from detect_workspace_state
    """
    from datetime import datetime

    registry_dir = workspace_root / ".ldf-workspace"
    registry_dir.mkdir(exist_ok=True)

    registry = {
        "generated": datetime.now().isoformat(),
        "workspace": state["name"],
        "projects": {},
    }

    for proj in state["projects"]:
        # Get spec list if project has LDF
        specs = []
        if proj["has_ldf"]:
            project_path = workspace_root / proj["path"]
            specs_dir = project_path / ".ldf" / "specs"
            if specs_dir.exists():
                specs = [d.name for d in specs_dir.iterdir() if d.is_dir()]

        registry["projects"][proj["alias"]] = {
            "path": proj["path"],
            "state": proj["state"],
            "version": proj["version"],
            "specs": specs,
        }

    # Write registry
    registry_path = registry_dir / ".registry.yaml"
    with open(registry_path, "w") as f:
        yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)
