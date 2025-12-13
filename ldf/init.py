"""LDF project initialization."""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ldf.utils.console import console

# Framework paths (relative to package)
FRAMEWORK_DIR = Path(__file__).parent.parent / "framework"

DEFAULT_QUESTION_PACKS = ["security", "testing", "api-design", "data-model"]
DOMAIN_QUESTION_PACKS = ["billing", "multi-tenancy", "provisioning", "webhooks"]
PRESETS = ["saas", "fintech", "healthcare", "api-only", "custom"]


def initialize_project(
    preset: str,
    question_packs: list[str],
    mcp_servers: list[str],
    non_interactive: bool = False,
    install_hooks: bool = False,
) -> None:
    """Initialize LDF in the current project directory.

    Args:
        preset: Guardrail preset (saas, fintech, healthcare, api-only, custom)
        question_packs: List of question packs to include
        mcp_servers: List of MCP servers to enable
        non_interactive: Skip prompts and use defaults
        install_hooks: Whether to install pre-commit hooks
    """
    project_root = Path.cwd()
    ldf_dir = project_root / ".ldf"

    # Check if already initialized
    if ldf_dir.exists() and not non_interactive:
        if not Confirm.ask("[yellow].ldf/ already exists. Overwrite?[/yellow]"):
            console.print("[red]Aborted[/red]")
            return

    console.print(Panel.fit(
        f"[bold blue]Initializing LDF in {project_root.name}[/bold blue]",
        title="LDF Setup",
    ))

    # Interactive configuration
    if not non_interactive:
        preset = _prompt_preset(preset)
        question_packs = _prompt_question_packs(question_packs)
        mcp_servers = _prompt_mcp_servers(mcp_servers)

    # Ensure defaults
    if not question_packs:
        question_packs = DEFAULT_QUESTION_PACKS
    if not mcp_servers:
        mcp_servers = ["spec-inspector", "coverage-reporter"]

    console.print()

    # Create directory structure
    _create_directories(ldf_dir)

    # Create configuration
    _create_config(ldf_dir, preset, question_packs, mcp_servers)

    # Create guardrails
    _create_guardrails(ldf_dir, preset)

    # Copy question packs
    _copy_question_packs(ldf_dir, question_packs)

    # Copy templates
    _copy_templates(ldf_dir)

    # Copy macros
    _copy_macros(ldf_dir)

    # Create CLAUDE.md
    _create_claude_md(project_root, preset, question_packs)

    # Create .claude directory for commands
    _create_claude_commands(project_root)

    # Install hooks if requested
    hooks_installed = False
    if install_hooks:
        from ldf.hooks import install_hooks as do_install_hooks
        console.print()
        hooks_installed = do_install_hooks(
            detect_linters=not non_interactive,
            non_interactive=non_interactive,
            project_root=project_root,
        )

    # Summary
    _print_summary(project_root, preset, question_packs, mcp_servers, hooks_installed)


def _prompt_preset(current: str) -> str:
    """Prompt user to select a guardrail preset."""
    if current and current != "custom":
        return current

    console.print("\n[bold]Select a guardrail preset:[/bold]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Preset", style="cyan")
    table.add_column("Description")
    table.add_column("Extra Guardrails")

    table.add_row("saas", "Multi-tenant SaaS applications", "+5 (RLS, tenancy, billing, audit, export)")
    table.add_row("fintech", "Financial applications", "+7 (ledger, precision, idempotency, audit, compliance)")
    table.add_row("healthcare", "HIPAA-compliant healthcare", "+6 (HIPAA, PHI, access logs, encryption, consent)")
    table.add_row("api-only", "Pure API services", "+4 (versioning, rate limits, webhooks, API keys)")
    table.add_row("custom", "Core guardrails only", "+0 (add your own)")

    console.print(table)

    return Prompt.ask(
        "\nChoose preset",
        choices=PRESETS,
        default="custom",
    )


def _prompt_question_packs(current: list[str]) -> list[str]:
    """Prompt user to select question packs."""
    if current:
        return current

    console.print("\n[bold]Select question packs to include:[/bold]")
    console.print("  Core packs (recommended):", ", ".join(DEFAULT_QUESTION_PACKS))
    console.print("  Domain packs (optional):", ", ".join(DOMAIN_QUESTION_PACKS))

    # Core packs
    include_core = Confirm.ask("\nInclude all core packs?", default=True)
    selected = list(DEFAULT_QUESTION_PACKS) if include_core else []

    # Domain packs
    for pack in DOMAIN_QUESTION_PACKS:
        if Confirm.ask(f"Include [cyan]{pack}[/cyan] pack?", default=False):
            selected.append(pack)

    return selected


def _prompt_mcp_servers(current: list[str]) -> list[str]:
    """Prompt user to select MCP servers."""
    if current:
        return list(current)

    console.print("\n[bold]MCP servers for real-time validation:[/bold]")

    servers = []
    if Confirm.ask("Enable [cyan]spec-inspector[/cyan] (spec validation)?", default=True):
        servers.append("spec-inspector")
    if Confirm.ask("Enable [cyan]coverage-reporter[/cyan] (test coverage)?", default=True):
        servers.append("coverage-reporter")

    return servers


def _create_directories(ldf_dir: Path) -> None:
    """Create the .ldf directory structure."""
    dirs = [
        ldf_dir,
        ldf_dir / "specs",
        ldf_dir / "question-packs",
        ldf_dir / "answerpacks",
        ldf_dir / "templates",
        ldf_dir / "audit-history",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    console.print(f"  [green]✓[/green] Created .ldf/ directory structure")


def _create_config(
    ldf_dir: Path,
    preset: str,
    question_packs: list[str],
    mcp_servers: list[str],
) -> None:
    """Create the LDF configuration file."""
    config = {
        "version": "1.0",
        "project": {
            "name": ldf_dir.parent.name,
            "specs_dir": ".ldf/specs",
        },
        "guardrails": {
            "preset": preset,
            "overrides": {},
        },
        "question_packs": question_packs,
        "mcp_servers": mcp_servers,
        "lint": {
            "strict": False,
            "auto_fix": False,
        },
    }

    config_path = ldf_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
    console.print(f"  [green]✓[/green] Created config.yaml")


def _create_guardrails(ldf_dir: Path, preset: str) -> None:
    """Create the guardrails configuration file."""
    guardrails = {
        "extends": "core",
        "preset": preset if preset != "custom" else None,
        "overrides": {},
        "disabled": [],
        "custom": [],
    }

    # Remove None values
    guardrails = {k: v for k, v in guardrails.items() if v is not None}

    guardrails_path = ldf_dir / "guardrails.yaml"
    with open(guardrails_path, "w") as f:
        yaml.safe_dump(guardrails, f, default_flow_style=False, sort_keys=False)
    console.print(f"  [green]✓[/green] Created guardrails.yaml (preset: {preset})")


def _copy_question_packs(ldf_dir: Path, packs: list[str]) -> None:
    """Copy selected question packs to the project."""
    source_dir = FRAMEWORK_DIR / "question-packs"
    dest_dir = ldf_dir / "question-packs"

    copied = 0
    for pack in packs:
        # Check core packs
        source = source_dir / "core" / f"{pack}.yaml"
        if not source.exists():
            # Check domain packs
            source = source_dir / "domain" / f"{pack}.yaml"

        if source.exists():
            shutil.copy(source, dest_dir / f"{pack}.yaml")
            copied += 1
        else:
            # Create placeholder for domain packs
            placeholder = dest_dir / f"{pack}.yaml"
            placeholder.write_text(f"# {pack} question pack\n# TODO: Add questions\n")
            copied += 1

    console.print(f"  [green]✓[/green] Copied {copied} question packs")


def _copy_templates(ldf_dir: Path) -> None:
    """Copy spec templates to the project."""
    source_dir = FRAMEWORK_DIR / "templates"
    dest_dir = ldf_dir / "templates"

    templates = ["requirements.md", "design.md", "tasks.md"]
    for template in templates:
        source = source_dir / template
        if source.exists():
            shutil.copy(source, dest_dir / template)

    console.print(f"  [green]✓[/green] Copied spec templates")


def _copy_macros(ldf_dir: Path) -> None:
    """Copy macros to the project."""
    source_dir = FRAMEWORK_DIR / "macros"
    dest_dir = ldf_dir / "macros"
    dest_dir.mkdir(exist_ok=True)

    macros = ["clarify-first.md", "coverage-gate.md", "task-guardrails.md"]
    for macro in macros:
        source = source_dir / macro
        if source.exists():
            shutil.copy(source, dest_dir / macro)

    console.print(f"  [green]✓[/green] Copied enforcement macros")


def _create_claude_md(project_root: Path, preset: str, question_packs: list[str]) -> None:
    """Create CLAUDE.md file for AI assistant integration."""
    coverage_threshold = "90%" if preset == "fintech" else "80%"

    content = f'''# Project Instructions for Claude Code

## Project Overview
**Name:** {project_root.name}
**Framework:** LDF (LLM Development Framework)
**Preset:** {preset}
**Initialized:** {datetime.now().strftime("%Y-%m-%d")}

---

## Development Methodology

This project uses **LDF** - a spec-driven development approach with three phases:

### Phase 1: Requirements
- **Location:** `.ldf/specs/{{feature}}/requirements.md`
- **Template:** `.ldf/templates/requirements.md`
- **Command:** `/project:create-spec {{feature-name}}`

### Phase 2: Design
- **Location:** `.ldf/specs/{{feature}}/design.md`
- **Template:** `.ldf/templates/design.md`

### Phase 3: Tasks
- **Location:** `.ldf/specs/{{feature}}/tasks.md`
- **Template:** `.ldf/templates/tasks.md`

**CRITICAL RULE:** Do NOT write code until all three phases are approved.

---

## Guardrails

This project enforces the following guardrails (see `.ldf/guardrails.yaml`):

### Core Guardrails (Always Active)
1. **Testing Coverage** - Minimum {coverage_threshold} coverage
2. **Security Basics** - OWASP Top 10 prevention
3. **Error Handling** - Consistent error responses
4. **Logging & Observability** - Structured logging, correlation IDs
5. **API Design** - Versioning, pagination, error format
6. **Data Validation** - Input validation at boundaries
7. **Database Migrations** - Reversible, separate from backfills
8. **Documentation** - API docs, inline comments

### Preset Guardrails ({preset})
See `.ldf/guardrails.yaml` for additional guardrails from the {preset} preset.

---

## Question Packs

Before writing requirements, answer questions from these packs:
{chr(10).join(f"- `{pack}`" for pack in question_packs)}

Answers are captured in `.ldf/answerpacks/{{feature}}/`.

---

## Custom Commands

### `/project:create-spec {{feature-name}}`
Create a new feature specification:
1. Load relevant question-packs
2. Ask clarifying questions (clarify-first macro)
3. Generate requirements.md
4. Wait for approval
5. Generate design.md
6. Wait for approval
7. Generate tasks.md
8. Ready for implementation

### `/project:implement-task {{spec-name}} {{task-number}}`
Implement a specific task:
1. Load spec context
2. Check dependencies
3. Run task-guardrails macro
4. Implement code + tests
5. Update task status

### `/project:review-spec {{spec-name}}`
Review spec for completeness:
1. Run coverage-gate macro
2. Validate guardrail coverage matrix
3. Check answerpacks populated
4. Report issues

---

## Validation

```bash
ldf lint                  # Validate all specs
ldf lint {{spec-name}}    # Validate single spec
ldf audit --type spec-review  # Generate audit for other AI
```

---

## Notes for Claude

- **Read specs first:** Always check `.ldf/specs/` before coding
- **Respect phases:** Don't skip requirements → design → tasks
- **Use macros:** Run clarify-first, coverage-gate, task-guardrails
- **Test after changes:** Verify coverage meets thresholds
- **Commit incrementally:** Commit after each completed task
- **Update progress:** Mark tasks complete in tasks.md

**Development Flow:** Plan → Design → Task → Implement → Test → Commit
'''

    claude_md_path = project_root / "CLAUDE.md"

    # Don't overwrite if exists (unless it's a LDF-generated one)
    if claude_md_path.exists():
        existing = claude_md_path.read_text()
        if "LDF" not in existing and "LLM Development Framework" not in existing:
            # Backup existing
            backup_path = project_root / "CLAUDE.md.backup"
            shutil.copy(claude_md_path, backup_path)
            console.print(f"  [yellow]![/yellow] Backed up existing CLAUDE.md to CLAUDE.md.backup")

    claude_md_path.write_text(content)
    console.print(f"  [green]✓[/green] Created CLAUDE.md")


def _create_claude_commands(project_root: Path) -> None:
    """Create .claude/commands directory with slash commands."""
    commands_dir = project_root / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Create spec command
    create_spec_cmd = '''# Create a new feature specification

## Arguments
- `feature-name`: Name of the feature to create (required)

## Process

1. **Load Question Packs**
   - Read `.ldf/config.yaml` for configured packs
   - Load pack files from `.ldf/question-packs/`

2. **Run Clarify-First Macro**
   - Ask all critical questions from loaded packs
   - Capture answers in `.ldf/answerpacks/{feature}/`
   - Block if critical questions unanswered

3. **Create Spec Directory**
   - Create `.ldf/specs/{feature}/`

4. **Generate requirements.md**
   - Use template from `.ldf/templates/requirements.md`
   - Include question-pack answers summary
   - Include guardrail coverage matrix
   - Add user stories based on answers

5. **Wait for Approval**
   - Present requirements to user
   - Run `ldf lint {feature}` to validate
   - Get explicit approval before continuing

6. **Generate design.md**
   - Use template from `.ldf/templates/design.md`
   - Map guardrails to design components
   - Include architecture diagrams
   - Define API endpoints and data models

7. **Wait for Approval**
   - Present design to user
   - Validate guardrail mapping complete
   - Get explicit approval before continuing

8. **Generate tasks.md**
   - Use template from `.ldf/templates/tasks.md`
   - Break work into <4 hour tasks
   - Include per-task guardrail checklist
   - Add dependencies and test requirements

9. **Final Validation**
   - Run `ldf lint {feature}`
   - Confirm all sections complete
   - Ready for implementation
'''

    (commands_dir / "create-spec.md").write_text(create_spec_cmd)

    # Create implement-task command
    implement_task_cmd = '''# Implement a specific task from a spec

## Arguments
- `spec-name`: Name of the spec (required)
- `task-number`: Task number to implement (e.g., "2.1") (required)

## Process

1. **Load Spec Context**
   - Read `.ldf/specs/{spec}/requirements.md`
   - Read `.ldf/specs/{spec}/design.md`
   - Read `.ldf/specs/{spec}/tasks.md`
   - Find the specific task

2. **Check Dependencies**
   - Verify dependent tasks are complete
   - Block if dependencies not met

3. **Run Task-Guardrails Macro**
   - Load active guardrails from `.ldf/guardrails.yaml`
   - Present checklist for this task
   - Verify each applicable guardrail addressed
   - Block if critical guardrails not addressed

4. **Implement Code**
   - Follow the design from design.md
   - Implement the task description
   - Add proper error handling
   - Follow project coding patterns

5. **Write Tests**
   - Unit tests for business logic
   - Integration tests for APIs
   - Meet coverage threshold

6. **Update Task Status**
   - Mark task as complete in tasks.md
   - Add commit reference

7. **Commit**
   - Stage changes
   - Commit with reference to spec and task
'''

    (commands_dir / "implement-task.md").write_text(implement_task_cmd)

    # Create review-spec command
    review_spec_cmd = '''# Review a spec for completeness

## Arguments
- `spec-name`: Name of the spec to review (required)

## Process

1. **Load Spec Files**
   - Check requirements.md exists
   - Check design.md exists
   - Check tasks.md exists

2. **Run Coverage-Gate Macro**
   - Validate guardrail coverage matrix
   - Check all active guardrails have entries
   - Verify no empty cells (or N/A with justification)

3. **Validate Answerpacks**
   - Check `.ldf/answerpacks/{spec}/` exists
   - Verify critical questions answered
   - Flag any template markers remaining

4. **Run Linter**
   - Execute `ldf lint {spec}`
   - Report errors and warnings

5. **Generate Report**
   - Summary of spec status
   - List of issues found
   - Recommendations for fixes
'''

    (commands_dir / "review-spec.md").write_text(review_spec_cmd)

    console.print(f"  [green]✓[/green] Created .claude/commands/")


def _print_summary(
    project_root: Path,
    preset: str,
    question_packs: list[str],
    mcp_servers: list[str],
    hooks_installed: bool = False,
) -> None:
    """Print initialization summary."""
    console.print()
    console.print(Panel.fit(
        "[bold green]LDF initialized successfully![/bold green]",
        title="Complete",
    ))

    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Preset: [cyan]{preset}[/cyan]")
    console.print(f"  Question packs: [cyan]{', '.join(question_packs)}[/cyan]")
    console.print(f"  MCP servers: [cyan]{', '.join(mcp_servers)}[/cyan]")
    if hooks_installed:
        console.print(f"  Pre-commit hooks: [green]installed[/green]")

    console.print("\n[bold]Created files:[/bold]")
    console.print("  .ldf/")
    console.print("  ├── config.yaml")
    console.print("  ├── guardrails.yaml")
    console.print("  ├── specs/")
    console.print("  ├── templates/")
    console.print("  ├── question-packs/")
    console.print("  ├── answerpacks/")
    console.print("  └── macros/")
    console.print("  .claude/commands/")
    console.print("  CLAUDE.md")
    if hooks_installed:
        console.print("  .git/hooks/pre-commit")

    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Review [cyan].ldf/config.yaml[/cyan] and customize as needed")
    console.print("  2. Review [cyan]CLAUDE.md[/cyan] and update project-specific sections")
    console.print("  3. Run [cyan]/project:create-spec <feature-name>[/cyan] to create your first spec")
    if not hooks_installed:
        console.print("  4. (Optional) Run [cyan]ldf hooks install[/cyan] to add pre-commit validation")
    console.print()
