"""LDF spec parsing utilities."""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SpecStatus(Enum):
    """Spec completion status."""

    NOT_STARTED = "not_started"
    REQUIREMENTS_DRAFT = "requirements_draft"
    REQUIREMENTS_APPROVED = "requirements_approved"
    DESIGN_DRAFT = "design_draft"
    DESIGN_APPROVED = "design_approved"
    TASKS_DRAFT = "tasks_draft"
    TASKS_APPROVED = "tasks_approved"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


@dataclass
class TaskItem:
    """Represents a single task from tasks.md."""

    id: str  # e.g., "1.1", "2.3"
    title: str
    status: str  # pending, in_progress, complete
    dependencies: list[str] = field(default_factory=list)
    checklist_complete: bool = False


@dataclass
class GuardrailMatrixRow:
    """Represents a row in the guardrail coverage matrix."""

    guardrail_id: int
    guardrail_name: str
    requirements_ref: str
    design_ref: str
    tasks_tests_ref: str
    owner: str
    status: str


@dataclass
class SpecInfo:
    """Parsed spec information."""

    name: str
    status: SpecStatus
    has_requirements: bool = False
    has_design: bool = False
    has_tasks: bool = False
    requirements_approved: bool = False
    design_approved: bool = False
    tasks_approved: bool = False
    guardrail_matrix: list[GuardrailMatrixRow] = field(default_factory=list)
    tasks: list[TaskItem] = field(default_factory=list)
    answerpacks_populated: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_spec(spec_path: Path) -> SpecInfo:
    """Parse a spec directory and extract information.

    Args:
        spec_path: Path to spec directory

    Returns:
        SpecInfo with parsed data
    """
    info = SpecInfo(name=spec_path.name, status=SpecStatus.NOT_STARTED)

    # Check which files exist
    requirements_path = spec_path / "requirements.md"
    design_path = spec_path / "design.md"
    tasks_path = spec_path / "tasks.md"

    info.has_requirements = requirements_path.exists()
    info.has_design = design_path.exists()
    info.has_tasks = tasks_path.exists()

    # Parse requirements
    if info.has_requirements:
        _parse_requirements(requirements_path, info)

    # Parse design
    if info.has_design:
        _parse_design(design_path, info)

    # Parse tasks
    if info.has_tasks:
        _parse_tasks(tasks_path, info)

    # Determine overall status
    info.status = _determine_status(info)

    return info


def get_spec_status(spec_path: Path) -> SpecStatus:
    """Get just the status of a spec.

    Args:
        spec_path: Path to spec directory

    Returns:
        SpecStatus enum value
    """
    return parse_spec(spec_path).status


def extract_guardrail_matrix(content: str) -> list[GuardrailMatrixRow]:
    """Extract the guardrail coverage matrix from markdown content.

    Args:
        content: Markdown content containing the matrix

    Returns:
        List of GuardrailMatrixRow objects
    """
    rows = []

    # Find the matrix section (allow empty lines after header)
    matrix_match = re.search(
        r"##\s*Guardrail Coverage Matrix.*?\n+(\|.+\|[\s\S]*?)(?=\n##|\n\n\n|\Z)",
        content,
        re.IGNORECASE,
    )

    if not matrix_match:
        return rows

    matrix_text = matrix_match.group(1)
    lines = matrix_text.strip().split("\n")

    # Skip header and separator rows
    data_lines = [
        line for line in lines
        if line.strip().startswith("|")
        and not re.match(r"^\|[-:\s|]+\|$", line)
        and "Guardrail" not in line
    ]

    for line in data_lines:
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) >= 6:
            # Extract guardrail ID from first cell (e.g., "1. Testing Coverage")
            first_cell = cells[0]
            id_match = re.match(r"(\d+)\.\s*(.+)", first_cell)
            if id_match:
                guardrail_id = int(id_match.group(1))
                guardrail_name = id_match.group(2).strip()
            else:
                guardrail_id = 0
                guardrail_name = first_cell

            rows.append(
                GuardrailMatrixRow(
                    guardrail_id=guardrail_id,
                    guardrail_name=guardrail_name,
                    requirements_ref=cells[1] if len(cells) > 1 else "",
                    design_ref=cells[2] if len(cells) > 2 else "",
                    tasks_tests_ref=cells[3] if len(cells) > 3 else "",
                    owner=cells[4] if len(cells) > 4 else "",
                    status=cells[5] if len(cells) > 5 else "",
                )
            )

    return rows


def extract_tasks(content: str) -> list[TaskItem]:
    """Extract task items from tasks.md content.

    Supported formats:

    1. Heading format (Task keyword optional, colon required):
       - ### Task 1.1: Title
       - ## Task 2.3: Title
       - # Task 1.1.1: Subtask title
       - ### 1.1: Title  (without Task keyword)

    2. Checklist format (Task keyword required, colon required):
       - - [ ] **Task 1.1:** Title  (with bold markers)
       - - [ ] Task 1.1: Title  (without bold markers)
       - - [x] **Task 1.1:** Completed task
       - - [X] Task 1.1.1: Subtask
       -   - [ ] Task 1.2: Indented task  (indentation allowed)

    Notes:
    - Heading format: "Task" keyword is OPTIONAL
    - Checklist format: "Task" keyword is REQUIRED
    - Task IDs support 2-level (1.1) or 3-level (1.1.1) numbering
    - Colon after task ID: REQUIRED for all formats
    - Inline references (e.g., "see task 1.1") are NOT matched

    Args:
        content: tasks.md content

    Returns:
        List of TaskItem objects
    """
    # For user-facing documentation on task formats, see: docs/task-format.md
    tasks = []

    # Pattern for task headers in two formats:
    # 1. Heading format: "### Task 1.1: Title" or "### 1.1: Title" (Task keyword optional)
    # 2. Checklist format: "- [ ] **Task 1.1:** Title" or "- [ ] Task 1.1: Title" (Task keyword required)
    # Supports subtasks: Task 1.1.1, Task 2.3.2, etc.
    # Requires heading markers or checkbox markers to avoid matching inline references
    # For checklist format, bold markers (**) are optional, and indentation is allowed
    task_pattern = re.compile(
        r"(?:#{1,3}\s*(?:Task\s+)?|^\s*-\s*\[\s*[xX\s]\s*\]\s*\*{0,2}Task\s+)(\d+\.\d+(?:\.\d+)?)[:]\s*(?:\*{0,2}\s*)?(.+?)(?=\n|$)",
        re.MULTILINE,
    )

    # Pattern for checkbox items
    checkbox_pattern = re.compile(r"- \[([ xX])\]")

    # Collect all task matches first to determine section boundaries
    all_matches = list(task_pattern.finditer(content))

    for i, match in enumerate(all_matches):
        task_id = match.group(1)
        title = match.group(2).strip()

        # Determine status based on surrounding content
        # Find the section for this task: from current task to next task (or end of content)
        start_pos = match.start()

        # Find the next task position
        if i + 1 < len(all_matches):
            end_pos = all_matches[i + 1].start()
        else:
            end_pos = len(content)

        task_section = content[start_pos:end_pos]

        # Check for status indicators
        status = "pending"
        if re.search(r"\[x\]|\[X\]|COMPLETE|DONE", task_section, re.IGNORECASE):
            # Check if all checkboxes are done
            checkboxes = checkbox_pattern.findall(task_section)
            if checkboxes:
                completed = sum(1 for c in checkboxes if c.lower() == "x")
                if completed == len(checkboxes):
                    status = "complete"
                elif completed > 0:
                    status = "in_progress"
            else:
                status = "complete"
        elif re.search(r"IN.?PROGRESS|STARTED", task_section, re.IGNORECASE):
            status = "in_progress"

        # Extract dependencies (supports both Task 1.1 and Task 1.1.1 formats)
        deps = []
        dep_match = re.search(r"Depends on:?\s*(.+?)(?=\n|$)", task_section, re.IGNORECASE)
        if dep_match:
            deps = [d.strip() for d in re.findall(r"(\d+\.\d+(?:\.\d+)?)", dep_match.group(1))]

        tasks.append(
            TaskItem(
                id=task_id,
                title=title,
                status=status,
                dependencies=deps,
            )
        )

    return tasks


def _parse_requirements(filepath: Path, info: SpecInfo) -> None:
    """Parse requirements.md and update SpecInfo."""
    content = filepath.read_text()

    # Check for Question-Pack Answers section
    if "## Question-Pack Answers" not in content:
        info.errors.append("requirements.md: Missing Question-Pack Answers section")

    # Check for Guardrail Coverage Matrix
    if "## Guardrail Coverage Matrix" not in content:
        info.errors.append("requirements.md: Missing Guardrail Coverage Matrix")
    else:
        info.guardrail_matrix = extract_guardrail_matrix(content)
        if not info.guardrail_matrix:
            info.warnings.append("requirements.md: Guardrail matrix found but empty")

    # Check for user stories
    if "## User Stories" not in content and "### US-" not in content:
        info.warnings.append("requirements.md: No user stories found")

    # Check for approval status
    if re.search(r"Status:\s*Approved", content, re.IGNORECASE):
        info.requirements_approved = True
    elif re.search(r"\[x\]\s*Requirements approved", content, re.IGNORECASE):
        info.requirements_approved = True


def _parse_design(filepath: Path, info: SpecInfo) -> None:
    """Parse design.md and update SpecInfo."""
    content = filepath.read_text()

    # Check for Guardrail Mapping section
    if "## Guardrail Mapping" not in content:
        info.warnings.append("design.md: Missing Guardrail Mapping section")

    # Check for approval status
    if re.search(r"Status:\s*Approved", content, re.IGNORECASE):
        info.design_approved = True
    elif re.search(r"\[x\]\s*Design approved", content, re.IGNORECASE):
        info.design_approved = True


def _parse_tasks(filepath: Path, info: SpecInfo) -> None:
    """Parse tasks.md and update SpecInfo."""
    content = filepath.read_text()

    # Check for Per-Task Guardrail Checklist
    if "## Per-Task Guardrail Checklist" not in content:
        info.errors.append("tasks.md: Missing Per-Task Guardrail Checklist")

    # Extract tasks
    info.tasks = extract_tasks(content)

    if not info.tasks:
        info.warnings.append("tasks.md: No tasks found")

    # Check for approval status
    if re.search(r"Status:\s*Approved", content, re.IGNORECASE):
        info.tasks_approved = True
    elif re.search(r"\[x\]\s*Tasks approved", content, re.IGNORECASE):
        info.tasks_approved = True


def _determine_status(info: SpecInfo) -> SpecStatus:
    """Determine overall spec status based on parsed info."""
    if not info.has_requirements:
        return SpecStatus.NOT_STARTED

    if not info.requirements_approved:
        return SpecStatus.REQUIREMENTS_DRAFT

    if not info.has_design:
        return SpecStatus.REQUIREMENTS_APPROVED

    if not info.design_approved:
        return SpecStatus.DESIGN_DRAFT

    if not info.has_tasks:
        return SpecStatus.DESIGN_APPROVED

    if not info.tasks_approved:
        return SpecStatus.TASKS_DRAFT

    # Check task completion
    if info.tasks:
        completed = sum(1 for t in info.tasks if t.status == "complete")
        if completed == len(info.tasks):
            return SpecStatus.COMPLETE
        elif completed > 0:
            return SpecStatus.IN_PROGRESS

    return SpecStatus.TASKS_APPROVED
