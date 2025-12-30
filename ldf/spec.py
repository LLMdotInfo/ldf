"""LDF spec management."""

from pathlib import Path

from ldf.utils.config import get_answerpacks_dir, get_specs_dir
from ldf.utils.console import console
from ldf.utils.guardrail_loader import detect_shared_resources_path
from ldf.utils.logging import get_logger
from ldf.utils.security import (
    SecurityError,
    is_safe_directory_entry,
    validate_spec_name,
    validate_spec_path_safe,
)

logger = get_logger(__name__)


def _resolve_template(
    template_name: str,
    project_root: Path,
    shared_resources_path: Path | None = None,
) -> Path | None:
    """Resolve a template file using fallback chain.

    Resolution order:
    1. Project templates: {project}/.ldf/templates/{template_name}
    2. Shared templates: {workspace}/.ldf-shared/templates/{template_name}
    3. Framework templates (built-in fallback)

    Args:
        template_name: Name of the template file (e.g., "requirements.md")
        project_root: Project root directory
        shared_resources_path: Path to workspace .ldf-shared/ (optional)

    Returns:
        Path to the resolved template, or None if not found
    """
    # 1. Check project templates first
    project_template = project_root / ".ldf" / "templates" / template_name
    if project_template.exists():
        logger.debug(f"Using project template: {project_template}")
        return project_template

    # 2. Check shared workspace templates
    if shared_resources_path:
        shared_template = shared_resources_path / "templates" / template_name
        if shared_template.exists():
            logger.debug(f"Using shared template: {shared_template}")
            return shared_template

    # 3. Check framework templates (built-in)
    from ldf.init import FRAMEWORK_DIR

    framework_template = FRAMEWORK_DIR / "templates" / template_name
    if framework_template.exists():
        logger.debug(f"Using framework template: {framework_template}")
        return framework_template

    return None


def create_spec(name: str, project_root: Path | None = None) -> bool:
    """Create a new feature specification from templates.

    Creates the spec directory structure with template files:
    - .ldf/specs/{name}/requirements.md
    - .ldf/specs/{name}/design.md
    - .ldf/specs/{name}/tasks.md
    - .ldf/answerpacks/{name}/

    Templates are resolved using a fallback chain:
    1. Project templates ({project}/.ldf/templates/)
    2. Shared templates ({workspace}/.ldf-shared/templates/)
    3. Framework templates (built-in)

    Args:
        name: Name of the spec to create (e.g., "user-auth")
        project_root: Project root directory (defaults to cwd)

    Returns:
        True if successful, False otherwise
    """
    if project_root is None:
        project_root = Path.cwd()

    # Check LDF is initialized first (needed for validate_spec_name)
    ldf_dir = project_root / ".ldf"
    if not ldf_dir.exists():
        console.print("[red]Error: LDF not initialized.[/red]")
        console.print("[dim]Run 'ldf init' first to initialize the project.[/dim]")
        return False

    # Get directories
    specs_dir = get_specs_dir(project_root)
    answerpacks_dir = get_answerpacks_dir(project_root)

    # Validate spec name using the comprehensive security validator
    # (handles hidden dirs, symlinks, Windows paths, empty strings, etc.)
    try:
        validate_spec_name(name, specs_dir)
    except SecurityError as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

    # Detect shared resources path for template fallback
    shared_resources_path = detect_shared_resources_path(project_root)

    # Check if spec already exists
    spec_dir = specs_dir / name
    if spec_dir.exists():
        console.print(f"[red]Error: Spec '{name}' already exists.[/red]")
        console.print(f"[dim]Location: {spec_dir}[/dim]")
        return False

    # Create spec directory
    spec_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Created spec directory: .ldf/specs/{name}/")

    # Copy templates using fallback chain
    template_files = ["requirements.md", "design.md", "tasks.md"]
    for template_name in template_files:
        dest_path = spec_dir / template_name

        # Resolve template using fallback chain
        template_path = _resolve_template(template_name, project_root, shared_resources_path)

        if template_path:
            # Read template and replace placeholders
            content = template_path.read_text()
            content = content.replace("{feature-name}", name)
            content = content.replace("{feature}", name)
            content = content.replace("{Feature Name}", name)
            content = content.replace("{{feature-name}}", name)
            content = content.replace("{{feature}}", name)
            content = content.replace("{{Feature Name}}", name)
            dest_path.write_text(content)

            # Indicate source of template
            if ".ldf-shared" in str(template_path):
                console.print(f"[green]✓[/green] Created {template_name} [dim](from shared)[/dim]")
            elif "/_framework/" in str(template_path):
                console.print(
                    f"[green]✓[/green] Created {template_name} [dim](from framework)[/dim]"
                )
            else:
                console.print(f"[green]✓[/green] Created {template_name}")
        else:
            # Create minimal file if template doesn't exist anywhere
            section_title = template_name.replace(".md", "").title()
            dest_path.write_text(f"# {name} - {section_title}\n\nTODO: Fill in this section.\n")
            console.print(
                f"[yellow]![/yellow] Created minimal {template_name} (template not found)"
            )

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
    console.print("  3. Continue to design and tasks phases")
    console.print()

    return True


def list_specs(project_root: Path | None = None) -> list[str]:
    """List all specs in the project.

    Filters out symlinks that escape the specs directory and hidden directories
    to prevent security issues.

    Args:
        project_root: Project root directory

    Returns:
        List of spec names (safe entries only)
    """
    if project_root is None:
        project_root = Path.cwd()

    specs_dir = get_specs_dir(project_root)
    if not specs_dir.exists():
        return []

    # Use is_safe_directory_entry to filter symlinks escaping specs_dir and hidden dirs
    return [
        d.name for d in specs_dir.iterdir() if d.is_dir() and is_safe_directory_entry(d, specs_dir)
    ]


def get_spec_path(name: str, project_root: Path | None = None) -> Path | None:
    """Get the path to a spec directory.

    Validates that the spec path doesn't escape the specs directory via symlinks
    or path traversal.

    Args:
        name: Spec name
        project_root: Project root directory

    Returns:
        Path to spec directory, or None if not found or if path is unsafe
    """
    if project_root is None:
        project_root = Path.cwd()

    specs_dir = get_specs_dir(project_root)
    spec_path = specs_dir / name

    if spec_path.exists() and spec_path.is_dir():
        # Validate path doesn't escape specs_dir via symlinks
        try:
            validate_spec_path_safe(spec_path, specs_dir)
            return spec_path
        except SecurityError:
            return None
    return None
