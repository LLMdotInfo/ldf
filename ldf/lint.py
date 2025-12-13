"""LDF spec linting with configurable guardrail validation."""

import re
from pathlib import Path

from rich.table import Table

from ldf.utils.config import load_config, get_specs_dir
from ldf.utils.console import console
from ldf.utils.guardrail_loader import get_active_guardrails, Guardrail
from ldf.utils.spec_parser import (
    parse_spec,
    SpecInfo,
    extract_guardrail_matrix,
    extract_tasks,
)


def lint_specs(
    spec_name: str | None,
    lint_all: bool,
    fix: bool,
    output_format: str = "rich",
) -> int:
    """Lint spec files against guardrail requirements.

    Args:
        spec_name: Name of specific spec to lint (or None for all)
        lint_all: Whether to lint all specs
        fix: Whether to auto-fix issues
        output_format: Output format - "rich" for terminal, "ci" for GitHub Actions

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    project_root = Path.cwd()
    ci_mode = output_format == "ci"

    # Check if LDF is initialized
    ldf_dir = project_root / ".ldf"
    if not ldf_dir.exists():
        if ci_mode:
            print("✗ Error: init: .ldf/ not found. Run 'ldf init' first.")
        else:
            console.print("[red]Error: .ldf/ not found. Run 'ldf init' first.[/red]")
        return 1

    specs_dir = get_specs_dir(project_root)

    if not specs_dir.exists():
        if ci_mode:
            print("✅ Pass: No specs directory found.")
        else:
            console.print("[yellow]No specs directory found. Create specs with '/project:create-spec'.[/yellow]")
        return 0

    # Load configuration
    try:
        config = load_config(project_root)
        strict_mode = config.get("lint", {}).get("strict", False)
    except FileNotFoundError:
        strict_mode = False

    # Load active guardrails
    active_guardrails = get_active_guardrails(project_root)
    if not ci_mode:
        console.print(f"\n[dim]Active guardrails: {len(active_guardrails)}[/dim]")

    # Find specs to lint
    if spec_name:
        spec_path = specs_dir / spec_name
        if not spec_path.exists():
            if ci_mode:
                print(f"✗ Error: {spec_name}: Spec not found")
            else:
                console.print(f"[red]Error: Spec not found: {spec_name}[/red]")
            return 1
        specs = [spec_path]
    elif lint_all:
        specs = [d for d in specs_dir.iterdir() if d.is_dir()]
    else:
        if ci_mode:
            print("✗ Error: cli: Specify a spec name or use --all to lint all specs.")
        else:
            console.print("[red]Error: Specify a spec name or use --all to lint all specs.[/red]")
            console.print("[dim]Usage: ldf lint <spec-name> or ldf lint --all[/dim]")
        return 1

    if not specs:
        if ci_mode:
            print("✅ Pass: No specs found to lint.")
        else:
            console.print("[yellow]No specs found to lint.[/yellow]")
        return 0

    # Lint each spec
    total_errors = 0
    total_warnings = 0
    results = []

    for spec_path in specs:
        errors, warnings = _lint_spec(spec_path, active_guardrails, fix, strict_mode, ci_mode)
        total_errors += len(errors)
        total_warnings += len(warnings)
        results.append((spec_path.name, errors, warnings))

    # Print summary
    if ci_mode:
        _print_ci_summary(results, total_errors, total_warnings)
    else:
        _print_summary(results, total_errors, total_warnings)

    return 1 if total_errors > 0 else 0


def _lint_spec(
    spec_path: Path,
    guardrails: list[Guardrail],
    fix: bool,
    strict_mode: bool,
    ci_mode: bool = False,
) -> tuple[list[str], list[str]]:
    """Lint a single spec directory.

    Args:
        spec_path: Path to spec directory
        guardrails: List of active guardrails
        fix: Whether to auto-fix issues
        strict_mode: Treat warnings as errors
        ci_mode: Whether to use CI-friendly output

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    spec_name = spec_path.name

    if not ci_mode:
        console.print(f"\n[bold]Linting: {spec_name}[/bold]")

    # Parse the spec
    spec_info = parse_spec(spec_path)

    # Add parser errors/warnings
    errors.extend(spec_info.errors)
    warnings.extend(spec_info.warnings)

    # Check required files exist
    required_files = ["requirements.md", "design.md", "tasks.md"]
    for filename in required_files:
        filepath = spec_path / filename
        if not filepath.exists():
            errors.append(f"Missing file: {filename}")

    # Validate requirements.md
    requirements_path = spec_path / "requirements.md"
    if requirements_path.exists():
        req_errors, req_warnings = _check_requirements(requirements_path, guardrails)
        errors.extend(req_errors)
        warnings.extend(req_warnings)

    # Validate design.md
    design_path = spec_path / "design.md"
    if design_path.exists():
        design_errors, design_warnings = _check_design(design_path, guardrails)
        errors.extend(design_errors)
        warnings.extend(design_warnings)

    # Validate tasks.md
    tasks_path = spec_path / "tasks.md"
    if tasks_path.exists():
        tasks_errors, tasks_warnings = _check_tasks(tasks_path, guardrails)
        errors.extend(tasks_errors)
        warnings.extend(tasks_warnings)

    # Check answerpacks
    answerpacks_errors, answerpacks_warnings = _check_answerpacks(spec_path)
    errors.extend(answerpacks_errors)
    warnings.extend(answerpacks_warnings)

    # Output results
    if ci_mode:
        # CI-friendly emoji-prefixed output for GitHub Actions parsing
        for error in errors:
            print(f"✗ Error: {spec_name}: {error}")
        for warning in warnings:
            print(f"⚠ Warning: {spec_name}: {warning}")
        if not errors and not warnings:
            print(f"✅ Pass: {spec_name}")
    else:
        for error in errors:
            console.print(f"  [red]ERROR[/red] {error}")
        for warning in warnings:
            console.print(f"  [yellow]WARN[/yellow] {warning}")
        if not errors and not warnings:
            console.print(f"  [green]PASSED[/green]")

    # In strict mode, treat warnings as errors
    if strict_mode:
        errors.extend(warnings)
        warnings = []

    return errors, warnings


def _check_requirements(filepath: Path, guardrails: list[Guardrail]) -> tuple[list[str], list[str]]:
    """Check requirements.md for required sections and guardrail coverage.

    Args:
        filepath: Path to requirements.md
        guardrails: List of active guardrails

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    content = filepath.read_text()

    # Required sections
    required_sections = [
        ("## Question-Pack Answers", "Question-Pack Answers section"),
        ("## Guardrail Coverage Matrix", "Guardrail Coverage Matrix"),
    ]

    for marker, name in required_sections:
        if marker not in content:
            errors.append(f"requirements.md: Missing {name}")

    # Check for user stories
    if "## User Stories" not in content and "### US-" not in content:
        warnings.append("requirements.md: No user stories found")

    # Validate guardrail coverage matrix
    if "## Guardrail Coverage Matrix" in content:
        matrix_errors, matrix_warnings = _validate_guardrail_matrix(content, guardrails)
        errors.extend(matrix_errors)
        warnings.extend(matrix_warnings)

    return errors, warnings


def _check_design(filepath: Path, guardrails: list[Guardrail]) -> tuple[list[str], list[str]]:
    """Check design.md for required sections.

    Args:
        filepath: Path to design.md
        guardrails: List of active guardrails

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    content = filepath.read_text()

    # Check for Guardrail Mapping section
    if "## Guardrail Mapping" not in content:
        warnings.append("design.md: Missing Guardrail Mapping section")

    # Check for architecture section
    if "## Architecture" not in content and "## Components" not in content:
        warnings.append("design.md: No Architecture or Components section")

    # Check for API endpoints or data model (at least one)
    # Flexible matching - look for API, Endpoint, Route in any header
    has_api = bool(re.search(r"##[#]?\s+.*\b(API|Endpoint|Route)", content, re.IGNORECASE))
    has_data = bool(re.search(r"##[#]?\s+.*\b(Data|Schema|Model|Database)", content, re.IGNORECASE))
    if not has_api and not has_data:
        warnings.append("design.md: No API or Data Model section found")

    return errors, warnings


def _check_tasks(filepath: Path, guardrails: list[Guardrail]) -> tuple[list[str], list[str]]:
    """Check tasks.md for required sections and per-task checklists.

    Args:
        filepath: Path to tasks.md
        guardrails: List of active guardrails

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    content = filepath.read_text()

    # Check for Per-Task Guardrail Checklist template
    if "## Per-Task Guardrail Checklist" not in content:
        errors.append("tasks.md: Missing Per-Task Guardrail Checklist")

    # Extract and validate tasks
    tasks = extract_tasks(content)

    if not tasks:
        warnings.append("tasks.md: No tasks found")
    else:
        # Check that each task section has checklist items
        for task in tasks:
            # Look for task section and check for checklist
            task_header = f"{task.id}"
            task_start = content.find(task_header)
            if task_start != -1:
                # Find next task or end
                next_task_pos = len(content)
                for other_task in tasks:
                    if other_task.id != task.id:
                        pos = content.find(other_task.id, task_start + 1)
                        if pos != -1 and pos < next_task_pos:
                            next_task_pos = pos

                task_section = content[task_start:next_task_pos]

                # Check for at least some checklist items
                if "- [ ]" not in task_section and "- [x]" not in task_section:
                    warnings.append(f"tasks.md: Task {task.id} has no checklist items")

    return errors, warnings


def _check_answerpacks(spec_path: Path) -> tuple[list[str], list[str]]:
    """Check answerpacks for the spec.

    Args:
        spec_path: Path to spec directory

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    # Check for answerpacks directory
    answerpacks_dir = spec_path.parent.parent / "answerpacks" / spec_path.name
    if not answerpacks_dir.exists():
        warnings.append(f"No answerpacks found at .ldf/answerpacks/{spec_path.name}/")
    else:
        # Check for any YAML files
        yaml_files = list(answerpacks_dir.glob("*.yaml")) + list(answerpacks_dir.glob("*.yml"))
        if not yaml_files:
            warnings.append("Answerpacks directory exists but contains no YAML files")
        else:
            # Check for template markers in answerpacks
            for yaml_file in yaml_files:
                content = yaml_file.read_text()
                if "[TODO" in content or "[PLACEHOLDER" in content or "YOUR_" in content:
                    errors.append(f"Answerpack {yaml_file.name} contains unfilled template markers")

    return errors, warnings


def _validate_guardrail_matrix(content: str, guardrails: list[Guardrail]) -> tuple[list[str], list[str]]:
    """Validate the guardrail coverage matrix against active guardrails.

    Args:
        content: Markdown content containing the matrix
        guardrails: List of active guardrails

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    matrix = extract_guardrail_matrix(content)

    if not matrix:
        errors.append("Guardrail coverage matrix is empty")
        return errors, warnings

    # Check that all active guardrails have entries
    matrix_ids = {row.guardrail_id for row in matrix}
    for guardrail in guardrails:
        if guardrail.id not in matrix_ids:
            # Try matching by name
            name_match = any(
                guardrail.name.lower() in row.guardrail_name.lower()
                for row in matrix
            )
            if not name_match:
                errors.append(f"Guardrail #{guardrail.id} ({guardrail.name}) not in coverage matrix")

    # Validate each matrix row
    for row in matrix:
        # Check for empty cells
        if not row.requirements_ref and row.status not in ["N/A", "n/a"]:
            warnings.append(f"Guardrail {row.guardrail_id}: Missing requirements reference")

        if not row.design_ref and row.status not in ["N/A", "n/a"]:
            warnings.append(f"Guardrail {row.guardrail_id}: Missing design reference")

        # Check N/A has justification
        if row.status.upper().startswith("N/A") and "-" not in row.status:
            # N/A without justification
            warnings.append(f"Guardrail {row.guardrail_id}: N/A status needs justification")

        # Check owner for non-N/A rows
        if row.status.upper() not in ["N/A"] and not row.owner:
            warnings.append(f"Guardrail {row.guardrail_id}: Missing owner")

    return errors, warnings


def _print_summary(
    results: list[tuple[str, list[str], list[str]]],
    total_errors: int,
    total_warnings: int,
) -> None:
    """Print linting summary.

    Args:
        results: List of (spec_name, errors, warnings) tuples
        total_errors: Total error count
        total_warnings: Total warning count
    """
    console.print()

    # Summary table
    table = Table(title="Lint Results", show_header=True, header_style="bold")
    table.add_column("Spec", style="cyan")
    table.add_column("Errors", justify="right")
    table.add_column("Warnings", justify="right")
    table.add_column("Status")

    for spec_name, errors, warnings in results:
        error_count = len(errors)
        warning_count = len(warnings)

        if error_count > 0:
            status = "[red]FAILED[/red]"
        elif warning_count > 0:
            status = "[yellow]WARNINGS[/yellow]"
        else:
            status = "[green]PASSED[/green]"

        table.add_row(
            spec_name,
            str(error_count) if error_count > 0 else "-",
            str(warning_count) if warning_count > 0 else "-",
            status,
        )

    console.print(table)

    # Overall status
    console.print()
    if total_errors == 0 and total_warnings == 0:
        console.print("[bold green]All specs passed validation![/bold green]")
    else:
        if total_errors > 0:
            console.print(f"[bold red]Total errors: {total_errors}[/bold red]")
        if total_warnings > 0:
            console.print(f"[bold yellow]Total warnings: {total_warnings}[/bold yellow]")


def _print_ci_summary(
    results: list[tuple[str, list[str], list[str]]],
    total_errors: int,
    total_warnings: int,
) -> None:
    """Print CI-friendly linting summary.

    Args:
        results: List of (spec_name, errors, warnings) tuples
        total_errors: Total error count
        total_warnings: Total warning count
    """
    print()
    print("=" * 50)
    print("LINT SUMMARY")
    print("=" * 50)

    for spec_name, errors, warnings in results:
        error_count = len(errors)
        warning_count = len(warnings)

        if error_count > 0:
            print(f"❌ {spec_name}: {error_count} error(s), {warning_count} warning(s)")
        elif warning_count > 0:
            print(f"⚠️  {spec_name}: {warning_count} warning(s)")
        else:
            print(f"✅ {spec_name}: PASSED")

    print("=" * 50)
    if total_errors == 0 and total_warnings == 0:
        print("✅ All specs passed validation!")
    else:
        if total_errors > 0:
            print(f"❌ Total errors: {total_errors}")
        if total_warnings > 0:
            print(f"⚠️  Total warnings: {total_warnings}")
