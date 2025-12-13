"""LDF spec management."""

import shutil
from pathlib import Path

from ldf.utils.config import get_specs_dir, get_answerpacks_dir, get_templates_dir
from ldf.utils.console import console


def create_spec(name: str, project_root: Path | None = None) -> bool:
    """Create a new feature specification from templates.

    Creates the spec directory structure with template files:
    - .ldf/specs/{name}/requirements.md
    - .ldf/specs/{name}/design.md
    - .ldf/specs/{name}/tasks.md
    - .ldf/answerpacks/{name}/

    Args:
        name: Name of the spec to create (e.g., "user-auth")
        project_root: Project root directory (defaults to cwd)

    Returns:
        True if successful, False otherwise
    """
    if project_root is None:
        project_root = Path.cwd()

    # Check LDF is initialized
    ldf_dir = project_root / ".ldf"
    if not ldf_dir.exists():
        console.print("[red]Error: LDF not initialized.[/red]")
        console.print("[dim]Run 'ldf init' first to initialize the project.[/dim]")
        return False

    # Get directories
    specs_dir = get_specs_dir(project_root)
    answerpacks_dir = get_answerpacks_dir(project_root)
    templates_dir = get_templates_dir(project_root)

    # Check if spec already exists
    spec_dir = specs_dir / name
    if spec_dir.exists():
        console.print(f"[red]Error: Spec '{name}' already exists.[/red]")
        console.print(f"[dim]Location: {spec_dir}[/dim]")
        return False

    # Create spec directory
    spec_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Created spec directory: .ldf/specs/{name}/")

    # Copy templates
    template_files = ["requirements.md", "design.md", "tasks.md"]
    for template_name in template_files:
        template_path = templates_dir / template_name
        dest_path = spec_dir / template_name

        if template_path.exists():
            # Read template and replace placeholders
            content = template_path.read_text()
            content = content.replace("{feature-name}", name)
            content = content.replace("{feature}", name)
            content = content.replace("{{feature-name}}", name)
            content = content.replace("{{feature}}", name)
            dest_path.write_text(content)
            console.print(f"[green]✓[/green] Created {template_name}")
        else:
            # Create minimal file if template doesn't exist
            dest_path.write_text(f"# {name} - {template_name.replace('.md', '').title()}\n\nTODO: Fill in this section.\n")
            console.print(f"[yellow]![/yellow] Created minimal {template_name} (template not found)")

    # Create answerpacks directory
    answerpack_dir = answerpacks_dir / name
    answerpack_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Created answerpacks directory: .ldf/answerpacks/{name}/")

    # Print next steps
    console.print()
    console.print("[bold]Spec created successfully![/bold]")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. Edit [cyan].ldf/specs/{name}/requirements.md[/cyan]")
    console.print("     - Answer question-pack questions")
    console.print("     - Define user stories and acceptance criteria")
    console.print("     - Complete the guardrail coverage matrix")
    console.print()
    console.print(f"  2. Validate with: [cyan]ldf lint {name}[/cyan]")
    console.print()
    console.print(f"  3. Continue to design and tasks phases")
    console.print()

    return True


def list_specs(project_root: Path | None = None) -> list[str]:
    """List all specs in the project.

    Args:
        project_root: Project root directory

    Returns:
        List of spec names
    """
    if project_root is None:
        project_root = Path.cwd()

    specs_dir = get_specs_dir(project_root)
    if not specs_dir.exists():
        return []

    return [d.name for d in specs_dir.iterdir() if d.is_dir()]


def get_spec_path(name: str, project_root: Path | None = None) -> Path | None:
    """Get the path to a spec directory.

    Args:
        name: Spec name
        project_root: Project root directory

    Returns:
        Path to spec directory, or None if not found
    """
    if project_root is None:
        project_root = Path.cwd()

    specs_dir = get_specs_dir(project_root)
    spec_path = specs_dir / name

    if spec_path.exists() and spec_path.is_dir():
        return spec_path
    return None
