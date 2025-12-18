"""LDF CLI - Command line interface for the LLM Development Framework."""

from pathlib import Path

import click

from ldf import __version__
from ldf.utils.console import console
from ldf.utils.logging import configure_logging


@click.group()
@click.version_option(version=__version__, prog_name="ldf")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def main(ctx, verbose):
    """LDF - LLM Development Framework.

    Spec-driven development for AI-assisted software engineering.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        configure_logging(verbose=True)


@main.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    help="Project directory path (created if doesn't exist)",
)
@click.option(
    "--preset",
    type=click.Choice(["saas", "fintech", "healthcare", "api-only", "custom"]),
    default=None,
    help="Guardrail preset to use",
)
@click.option(
    "--question-packs",
    "-q",
    multiple=True,
    help="Question packs to include (e.g., security, testing)",
)
@click.option(
    "--mcp-servers",
    "-m",
    multiple=True,
    help="MCP servers to enable",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Non-interactive mode, accept defaults",
)
@click.option(
    "--hooks/--no-hooks",
    default=None,
    help="Install pre-commit hooks for spec validation",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force initialization, overwriting existing LDF setup",
)
@click.option(
    "--repair",
    is_flag=True,
    help="Repair incomplete LDF setup without overwriting user files",
)
def init(
    path: str | None,
    preset: str | None,
    question_packs: tuple,
    mcp_servers: tuple,
    yes: bool,
    hooks: bool | None,
    force: bool,
    repair: bool,
):
    """Initialize LDF in a project directory.

    Creates .ldf/ directory with configuration, guardrails, and templates.
    Also generates CLAUDE.md for AI assistant integration.

    \b
    Smart Detection:
    - If LDF is already initialized and up to date, suggests no action needed
    - If LDF is outdated, suggests 'ldf update' instead
    - If LDF is incomplete, suggests 'ldf init --repair'

    \b
    Flags:
    --force   Override detection and reinitialize from scratch
    --repair  Fix missing files without overwriting existing ones

    Examples:
        ldf init                            # Interactive setup
        ldf init --path ./my-project        # Create project at path
        ldf init --preset saas              # Use SaaS preset
        ldf init -y                         # Non-interactive with defaults
        ldf init --hooks                    # Also install pre-commit hooks
        ldf init --force                    # Reinitialize existing project
        ldf init --repair                   # Fix missing files only
    """
    from pathlib import Path as PathLib

    from ldf.detection import ProjectState, detect_project_state
    from ldf.init import initialize_project, repair_project

    project_path = PathLib(path).resolve() if path else Path.cwd()

    # Smart detection (unless --force is used)
    if not force:
        detection = detect_project_state(project_path)

        if detection.state == ProjectState.CURRENT:
            console.print("[green]LDF is already initialized and up to date.[/green]")
            console.print("Run [cyan]ldf status[/cyan] for details.")
            console.print("Run [cyan]ldf init --force[/cyan] to reinitialize from scratch.")
            return

        elif detection.state == ProjectState.OUTDATED:
            console.print("[yellow]LDF is already initialized but outdated.[/yellow]")
            console.print(f"  Project version: {detection.project_version}")
            console.print(f"  Latest version:  {detection.installed_version}")
            console.print()
            console.print("Run [cyan]ldf update[/cyan] to update framework files.")
            console.print("Run [cyan]ldf init --force[/cyan] to reinitialize from scratch.")
            return

        elif detection.state == ProjectState.LEGACY:
            console.print("[yellow]Legacy LDF detected (no version tracking).[/yellow]")
            console.print()
            console.print("Run [cyan]ldf update[/cyan] to upgrade to the latest format.")
            console.print("Run [cyan]ldf init --force[/cyan] to reinitialize from scratch.")
            return

        elif detection.state == ProjectState.PARTIAL:
            if repair:
                # Run repair mode
                console.print("[yellow]Incomplete LDF setup detected. Repairing...[/yellow]")
                repair_project(project_path)
                return
            else:
                console.print("[yellow]Incomplete LDF setup detected.[/yellow]")
                if detection.missing_files:
                    console.print(f"  Missing: {', '.join(detection.missing_files[:3])}")
                console.print()
                console.print("Run [cyan]ldf init --repair[/cyan] to fix missing files.")
                console.print("Run [cyan]ldf init --force[/cyan] to reinitialize from scratch.")
                return

        elif detection.state == ProjectState.CORRUPTED:
            console.print("[red]Corrupted LDF setup detected.[/red]")
            if detection.invalid_files:
                console.print(f"  Invalid: {', '.join(detection.invalid_files)}")
            console.print()
            console.print("Run [cyan]ldf init --force[/cyan] to reinitialize.")
            return

    # Handle --repair flag for partial setups
    if repair:
        detection = detect_project_state(project_path)
        if detection.state == ProjectState.NEW:
            console.print("[yellow]No existing LDF setup to repair. Running full initialization.[/yellow]")
        elif detection.state in (ProjectState.PARTIAL, ProjectState.LEGACY):
            console.print("[yellow]Repairing LDF setup...[/yellow]")
            repair_project(project_path)
            return
        else:
            console.print("[green]LDF setup is complete. No repair needed.[/green]")
            return

    # Proceed with normal initialization
    initialize_project(
        project_path=project_path if path else None,
        preset=preset,
        question_packs=list(question_packs) if question_packs else None,
        mcp_servers=list(mcp_servers) if mcp_servers else None,
        non_interactive=yes,
        install_hooks=hooks if hooks is not None else False,
    )


@main.command()
@click.argument("spec_name", required=False)
@click.option("--all", "-a", "lint_all", is_flag=True, help="Lint all specs")
@click.option("--fix", "-f", is_flag=True, help="Auto-fix issues where possible")
@click.option(
    "--format",
    "-F",
    "output_format",
    type=click.Choice(["rich", "ci"]),
    default="rich",
    help="Output format: rich (default) for terminal, ci for GitHub Actions",
)
def lint(spec_name: str | None, lint_all: bool, fix: bool, output_format: str):
    """Validate spec files against guardrail requirements.

    Examples:
        ldf lint --all              # Lint all specs
        ldf lint user-auth          # Lint single spec
        ldf lint user-auth --fix    # Lint and auto-fix issues
        ldf lint --all --format ci  # CI-friendly output for GitHub Actions
    """
    from ldf.lint import lint_specs

    exit_code = lint_specs(spec_name, lint_all, fix, output_format=output_format)
    raise SystemExit(exit_code)


@main.command("create-spec")
@click.argument("name")
def create_spec(name: str):
    """Create a new feature specification from templates.

    Creates the spec directory structure with template files:

    \b
    - .ldf/specs/{name}/requirements.md
    - .ldf/specs/{name}/design.md
    - .ldf/specs/{name}/tasks.md
    - .ldf/answerpacks/{name}/

    Examples:
        ldf create-spec user-auth
        ldf create-spec payment-processing
    """
    from ldf.spec import create_spec as do_create_spec

    success = do_create_spec(name)
    if not success:
        raise SystemExit(1)


@main.command()
@click.option(
    "--type",
    "-t",
    "audit_type",
    type=click.Choice([
        "spec-review", "code-audit", "security", "security-check", "pre-launch",
        "gap-analysis", "edge-cases", "architecture", "full"
    ]),
    help="Type of audit request to generate",
)
@click.option(
    "--spec",
    "-s",
    "spec_name",
    help="Audit a specific spec only",
)
@click.option(
    "--import",
    "-i",
    "import_file",
    type=click.Path(exists=True),
    help="Import audit feedback from file",
)
@click.option("--api", is_flag=True, help="Use API automation (requires config)")
@click.option(
    "--agent",
    type=click.Choice(["chatgpt", "gemini"]),
    help="AI provider for API audit (requires --api)",
)
@click.option(
    "--auto-import",
    is_flag=True,
    help="Automatically import API audit response",
)
@click.option(
    "--include-secrets",
    is_flag=True,
    help="Include potentially sensitive content (API keys, tokens) in export",
)
@click.option(
    "-y", "--yes",
    is_flag=True,
    help="Skip confirmation prompts",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format (json for CI/scripting)",
)
def audit(
    audit_type: str | None,
    spec_name: str | None,
    import_file: str | None,
    api: bool,
    agent: str | None,
    auto_import: bool,
    include_secrets: bool,
    yes: bool,
    output: str,
):
    """Generate audit requests or import feedback from other AI agents.

    By default, potentially sensitive content is redacted from exports.
    Use --include-secrets to include all content.

    Audit types:

    \b
    - spec-review:    Completeness, clarity, edge cases
    - code-audit:     Code quality, security, test coverage
    - security:       Authentication, OWASP Top 10, data exposure
    - security-check: Alias for security
    - pre-launch:     Production readiness, monitoring, rollback
    - gap-analysis:   Missing requirements, coverage gaps
    - edge-cases:     Boundary conditions, error handling
    - architecture:   Component coupling, scalability, API design
    - full:           Run all audit types (API mode only)

    API automation:

    Configure API keys in .ldf/config.yaml under audit_api.chatgpt or
    audit_api.gemini, then use --api --agent to run automated audits.

    Redacted patterns include:

    \b
    - API keys (api_key=..., sk-*, pk-*, api_*)
    - Bearer tokens and JWTs
    - Passwords and secrets in key=value format
    - AWS access keys and secret keys
    - Long alphanumeric strings (40+ chars)
    - Secret environment variables ($SECRET_*, $TOKEN, etc.)

    Note: Redaction uses heuristic patterns. Unusual secrets may not be
    caught, and some normal text may be redacted. Review output if needed.

    Examples:
        ldf audit --type spec-review                    # Review all specs
        ldf audit --type security --spec auth           # Security audit on auth spec
        ldf audit --type gap-analysis                   # Find coverage gaps
        ldf audit --import feedback.md                  # Import audit feedback
        ldf audit --type security --api --agent chatgpt # API-based audit
        ldf audit --type full --api --agent gemini --auto-import  # Full auto audit
    """
    from ldf.audit import run_audit

    # Normalize security-check to security
    if audit_type == "security-check":
        audit_type = "security"

    run_audit(
        audit_type=audit_type,
        import_file=import_file,
        use_api=api,
        agent=agent,
        auto_import=auto_import,
        include_secrets=include_secrets,
        skip_confirm=yes,
        spec_name=spec_name,
        output_format=output,
    )


@main.command("mcp-config")
@click.option(
    "--root",
    "-r",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Project root directory (defaults to current directory)",
)
@click.option(
    "--server",
    "-s",
    multiple=True,
    help="Include specific MCP server(s) (can be used multiple times)",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["claude", "json"]),
    default="claude",
    help="Output format: claude (mcpServers wrapper) or json (raw)",
)
def mcp_config(root: Path | None, server: tuple, output_format: str):
    """Generate MCP server configuration for AI assistants.

    Outputs JSON configuration pointing to LDF's MCP servers with paths
    configured for the specified project directory.

    The 'claude' format (default) outputs JSON suitable for .claude/mcp.json:

    \\b
    {
      "mcpServers": {
        "spec-inspector": { ... },
        "coverage-reporter": { ... }
      }
    }

    The 'json' format outputs just the server configurations without wrapper.

    Examples:
        ldf mcp-config                    # Config for current directory
        ldf mcp-config -r ./my-project    # Config for specific project
        ldf mcp-config -s spec-inspector  # Only spec-inspector server
        ldf mcp-config --format json      # Raw JSON output

    To create .claude/mcp.json:
        mkdir -p .claude && ldf mcp-config > .claude/mcp.json
    """
    from ldf.mcp_config import print_mcp_config

    servers = list(server) if server else None
    print_mcp_config(root, servers, output_format)


@main.command()
@click.option("--service", "-s", help="Service name for service-specific coverage")
@click.option("--guardrail", "-g", type=int, help="Guardrail ID for guardrail-specific coverage")
@click.option("--validate", is_flag=True, help="Exit with error code if coverage below threshold (for CI)")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed per-file coverage breakdown")
def coverage(service: str | None, guardrail: int | None, validate: bool, verbose: bool):
    """Check test coverage against guardrail requirements.

    Examples:
        ldf coverage                 # Overall coverage
        ldf coverage --service auth  # Service-specific
        ldf coverage --guardrail 1   # Guardrail-specific (Testing Coverage)
        ldf coverage --validate      # CI mode - exit 1 if below threshold
        ldf coverage --verbose       # Show all files, not just lowest 10
    """
    from ldf.coverage import report_coverage

    report = report_coverage(
        service=service,
        guardrail_id=guardrail,
        validate=validate,
        verbose=verbose,
    )
    if validate and report.get("status") in ("FAIL", "ERROR"):
        raise SystemExit(1)


@main.command()
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output as JSON for scripting",
)
def status(json_output: bool):
    """Show LDF project status and recommendations.

    Detects the current project state and provides actionable recommendations.

    \b
    States:
    - new:       No LDF setup found. Run 'ldf init' to get started.
    - current:   LDF is up to date. No action needed.
    - outdated:  Newer LDF version available. Run 'ldf update'.
    - legacy:    Old LDF format without version. Run 'ldf update'.
    - partial:   Incomplete LDF setup. Run 'ldf init --repair'.
    - corrupted: Invalid LDF files found. Run 'ldf init --force'.

    Examples:
        ldf status              # Human-readable status
        ldf status --json       # JSON output for CI/scripts
    """
    from ldf.detection import ProjectState, detect_project_state, get_specs_summary

    result = detect_project_state(Path.cwd())

    if json_output:
        # Add specs to JSON output
        data = result.to_dict()
        if result.state != ProjectState.NEW:
            ldf_dir = result.project_root / ".ldf"
            data["specs"] = get_specs_summary(ldf_dir)
        console.print(result.to_json())
        return

    # Human-readable output
    console.print()
    console.print("[bold]LDF Project Status[/bold]")
    console.print("=" * 40)
    console.print()

    # State with color
    state_colors = {
        ProjectState.NEW: "blue",
        ProjectState.CURRENT: "green",
        ProjectState.OUTDATED: "yellow",
        ProjectState.LEGACY: "yellow",
        ProjectState.PARTIAL: "yellow",
        ProjectState.CORRUPTED: "red",
    }
    color = state_colors.get(result.state, "white")
    console.print(f"[bold]State:[/bold] [{color}]{result.state.value.upper()}[/{color}]")
    console.print()

    # Project info
    console.print(f"[bold]Project:[/bold] {result.project_root.name}")
    console.print(f"[bold]Location:[/bold] {result.project_root}")
    console.print()

    # Version info
    if result.state != ProjectState.NEW:
        console.print("[bold]Version:[/bold]")
        console.print(f"  Installed LDF: {result.installed_version}")
        if result.project_version:
            console.print(f"  Project LDF:   {result.project_version}")
        else:
            console.print("  Project LDF:   [dim](not tracked)[/dim]")
        console.print()

    # Completeness (if not new)
    if result.state != ProjectState.NEW:
        console.print("[bold]Setup Completeness:[/bold]")
        _print_check("config.yaml", result.has_config)
        _print_check("guardrails.yaml", result.has_guardrails)
        _print_check("specs/", result.has_specs_dir)
        _print_check("templates/", result.has_templates)
        _print_check("question-packs/", result.has_question_packs_dir)
        _print_check("answerpacks/", result.has_answerpacks_dir)
        _print_check("macros/", result.has_macros)
        _print_check("CLAUDE.md", result.has_claude_md)
        _print_check(".claude/commands/", result.has_claude_commands)

        if result.missing_files:
            console.print()
            console.print("[bold]Missing:[/bold]")
            for f in result.missing_files[:5]:
                console.print(f"  [red]-[/red] {f}")
            if len(result.missing_files) > 5:
                console.print(f"  [dim]... and {len(result.missing_files) - 5} more[/dim]")

        if result.invalid_files:
            console.print()
            console.print("[bold]Invalid:[/bold]")
            for f in result.invalid_files:
                console.print(f"  [red]![/red] {f}")

        # Show specs if available
        ldf_dir = result.project_root / ".ldf"
        specs = get_specs_summary(ldf_dir)
        if specs:
            console.print()
            console.print(f"[bold]Specs:[/bold] {len(specs)} found")
            for spec in specs[:5]:
                status_icon = {"tasks": "[green]tasks[/green]", "design": "[yellow]design[/yellow]", "requirements": "[blue]req[/blue]", "empty": "[dim]empty[/dim]"}.get(spec["status"], spec["status"])
                console.print(f"  - {spec['name']} ({status_icon})")
            if len(specs) > 5:
                console.print(f"  [dim]... and {len(specs) - 5} more[/dim]")

        console.print()

    # Recommendation
    console.print(f"[bold]Recommendation:[/bold] {result.recommended_action}")
    if result.recommended_command:
        console.print(f"[bold]Run:[/bold] [cyan]{result.recommended_command}[/cyan]")
    console.print()


def _print_check(label: str, present: bool) -> None:
    """Print a completeness check line."""
    if present:
        console.print(f"  [green][X][/green] {label}")
    else:
        console.print(f"  [red][ ][/red] {label}")


@main.group()
def hooks():
    """Manage Git hooks for LDF validation.

    Pre-commit hooks validate specs (and optionally code) before commits.
    """
    pass


@hooks.command("install")
@click.option(
    "--detect/--no-detect",
    default=True,
    help="Auto-detect and suggest language linters",
)
@click.option(
    "-y", "--yes",
    is_flag=True,
    help="Non-interactive mode, use detected defaults",
)
def hooks_install(detect: bool, yes: bool):
    """Install LDF pre-commit hook.

    By default, auto-detects project languages (Python, TypeScript, Go)
    and prompts to enable linting for each.

    Examples:
        ldf hooks install              # Interactive, auto-detects linters
        ldf hooks install --no-detect  # Skip detection, spec lint only
        ldf hooks install -y           # Non-interactive, enable detected linters
    """
    from ldf.hooks import install_hooks

    success = install_hooks(detect_linters=detect, non_interactive=yes)
    if not success:
        raise SystemExit(1)


@hooks.command("uninstall")
def hooks_uninstall():
    """Remove LDF pre-commit hook.

    Removes the hook from .git/hooks/pre-commit.
    Configuration in .ldf/config.yaml is preserved.
    """
    from ldf.hooks import uninstall_hooks

    success = uninstall_hooks()
    if not success:
        raise SystemExit(1)


@hooks.command("status")
def hooks_status():
    """Show hook installation status and configuration.

    Displays whether the hook is installed and what checks are enabled.
    """
    from ldf.hooks import print_hooks_status

    print_hooks_status()


@main.command()
@click.option(
    "--check",
    is_flag=True,
    help="Check for available updates without applying",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without applying",
)
@click.option(
    "--only",
    multiple=True,
    type=click.Choice(["templates", "macros", "question-packs"]),
    help="Update specific components only (can be used multiple times)",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Skip confirmation prompts",
)
def update(check: bool, dry_run: bool, only: tuple, yes: bool):
    """Update framework files from LDF source.

    Pulls latest templates, macros, and question-packs while preserving
    your customizations. User specs and answerpacks are never modified.

    \b
    Update strategies:
    - templates/: Always replaced with latest framework versions
    - macros/: Always replaced with latest framework versions
    - question-packs/: Replaced if unmodified; prompts if you've made changes
    - specs/, answerpacks/: Never touched

    Examples:
        ldf update --check            # Check for available updates
        ldf update --dry-run          # Preview changes without applying
        ldf update                    # Apply updates interactively
        ldf update --only templates   # Update templates only
        ldf update -y                 # Apply all updates without prompts
    """
    from ldf.update import (
        apply_updates,
        check_for_updates,
        get_update_diff,
        print_update_check,
        print_update_diff,
        print_update_result,
    )

    project_root = Path.cwd()
    ldf_dir = project_root / ".ldf"

    if not ldf_dir.exists():
        console.print("[red]Error: No .ldf directory found.[/red]")
        console.print("Run [cyan]ldf init[/cyan] to initialize a project first.")
        raise SystemExit(1)

    components = list(only) if only else None

    # --check mode: just show version comparison
    if check:
        info = check_for_updates(project_root)
        print_update_check(info)
        return

    # Get the diff
    diff = get_update_diff(project_root, components)

    # --dry-run mode: show what would change
    if dry_run:
        print_update_diff(diff, dry_run=True)
        if diff.files_to_add or diff.files_to_update or diff.conflicts:
            console.print()
            console.print("Run [cyan]ldf update[/cyan] to apply these changes.")
        return

    # Check if there's anything to do
    if not diff.files_to_add and not diff.files_to_update and not diff.conflicts:
        console.print("[green]Your project is up to date![/green]")
        return

    # Show what will change
    print_update_diff(diff, dry_run=False)

    # Handle conflicts interactively
    conflict_resolutions: dict[str, str] = {}
    if diff.conflicts and not yes:
        console.print()
        console.print("[bold]Resolve conflicts:[/bold]")
        for conflict in diff.conflicts:
            console.print(f"\n[yellow]{conflict.file_path}[/yellow] has local changes.")
            console.print("  Options:")
            console.print("    [1] Keep local version")
            console.print("    [2] Use framework version (overwrites your changes)")
            console.print("    [3] Skip this file")

            while True:
                choice = console.input("  Choice [1/2/3]: ").strip()
                if choice == "1":
                    conflict_resolutions[conflict.file_path] = "keep_local"
                    break
                elif choice == "2":
                    conflict_resolutions[conflict.file_path] = "use_framework"
                    break
                elif choice == "3":
                    conflict_resolutions[conflict.file_path] = "skip"
                    break
                else:
                    console.print("  [red]Invalid choice. Enter 1, 2, or 3.[/red]")
    elif diff.conflicts and yes:
        # With -y flag, skip all conflicts
        for conflict in diff.conflicts:
            conflict_resolutions[conflict.file_path] = "skip"

    # Confirm before applying (unless -y)
    if not yes:
        console.print()
        if not click.confirm("Apply these updates?"):
            console.print("[yellow]Aborted.[/yellow]")
            return

    # Apply updates
    result = apply_updates(
        project_root,
        components=components,
        dry_run=False,
        conflict_resolutions=conflict_resolutions,
    )

    print_update_result(result)

    if not result.success:
        raise SystemExit(1)


@main.group()
def convert():
    """Convert existing codebases to LDF.

    Provides tools for adding LDF to projects that already have code,
    including AI-assisted "backwards fill" to generate specs from existing code.

    \b
    Workflow:
    1. Run 'ldf convert analyze' to scan your codebase
    2. Copy the generated prompt to an AI assistant
    3. Save the AI's response to a file
    4. Run 'ldf convert import <file>' to create specs and answerpacks
    """
    pass


@convert.command("analyze")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for the analysis prompt (default: stdout)",
)
def convert_analyze(output: str | None):
    """Analyze existing codebase and generate backwards fill prompt.

    Scans the project for:
    - Programming languages and frameworks
    - Existing tests and documentation
    - API definitions
    - Configuration patterns

    Generates a prompt you can give to an AI assistant to create
    LDF specs and answerpacks based on the existing code.

    Examples:
        ldf convert analyze                    # Print prompt to stdout
        ldf convert analyze -o prompt.md       # Save to file
        ldf convert analyze | pbcopy           # Copy to clipboard (macOS)
    """
    from ldf.convert import (
        analyze_existing_codebase,
        generate_backwards_fill_prompt,
        print_conversion_context,
    )

    project_root = Path.cwd()

    # Analyze the codebase
    console.print("[dim]Analyzing codebase...[/dim]")
    ctx = analyze_existing_codebase(project_root)

    # Show analysis summary (to stderr so it doesn't interfere with prompt output)
    print_conversion_context(ctx)

    # Generate the prompt
    prompt = generate_backwards_fill_prompt(ctx)

    if output:
        # Write to file
        output_path = Path(output)
        output_path.write_text(prompt)
        console.print(f"[green]Prompt saved to:[/green] {output_path}")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print(f"  1. Open {output_path} and copy the contents")
        console.print("  2. Paste into an AI assistant (Claude, ChatGPT, etc.)")
        console.print("  3. Save the AI's response to a file (e.g., response.md)")
        console.print("  4. Run: [cyan]ldf convert import response.md[/cyan]")
    else:
        # Print to stdout
        console.print("[bold]Generated Prompt:[/bold]")
        console.print("-" * 40)
        print(prompt)
        console.print("-" * 40)
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Copy the prompt above")
        console.print("  2. Paste into an AI assistant (Claude, ChatGPT, etc.)")
        console.print("  3. Save the AI's response to a file (e.g., response.md)")
        console.print("  4. Run: [cyan]ldf convert import response.md[/cyan]")


@convert.command("import")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--spec-name",
    "-n",
    default="existing-system",
    help="Name for the spec (default: existing-system)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview without creating files",
)
def convert_import(file: str, spec_name: str, dry_run: bool):
    """Import AI-generated specs and answerpacks.

    Takes the AI response from the backwards fill prompt and creates
    the appropriate files in .ldf/specs/ and .ldf/answerpacks/.

    The input file should contain the AI's response in the format
    specified by 'ldf convert analyze' (with section markers like
    '# === ANSWERPACK: security.yaml ===' and '# === SPEC: requirements.md ===').

    Examples:
        ldf convert import response.md
        ldf convert import response.md --spec-name user-auth
        ldf convert import response.md --dry-run
    """
    from ldf.convert import import_backwards_fill, print_import_result
    from ldf.detection import ProjectState, detect_project_state

    project_root = Path.cwd()

    # Check that LDF is initialized
    detection = detect_project_state(project_root)
    if detection.state == ProjectState.NEW:
        console.print("[red]Error: LDF not initialized.[/red]")
        console.print("Run [cyan]ldf init[/cyan] first to initialize the project.")
        raise SystemExit(1)

    # Read the input file
    input_path = Path(file)
    content = input_path.read_text()

    if dry_run:
        console.print("[dim]Dry run - no files will be created[/dim]")

    # Import the content
    console.print(f"[dim]Importing from {input_path}...[/dim]")
    result = import_backwards_fill(
        content=content,
        project_root=project_root,
        spec_name=spec_name,
        dry_run=dry_run,
    )

    print_import_result(result)

    if not result.success:
        raise SystemExit(1)

    if not dry_run and result.success:
        console.print("[bold]Next steps:[/bold]")
        console.print(f"  1. Review the generated files in .ldf/specs/{spec_name}/")
        console.print(f"  2. Review answerpacks in .ldf/answerpacks/{spec_name}/")
        console.print("  3. Run [cyan]ldf lint[/cyan] to validate the specs")
        console.print("  4. Refine the specs as needed")


if __name__ == "__main__":
    main()
