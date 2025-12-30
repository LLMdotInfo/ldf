"""Cross-project reference parsing and resolution.

This module provides utilities for parsing and validating cross-project
spec references using the @project:spec syntax.

Reference Syntax:
    @{project-alias}:{spec-name}           - Reference a spec
    @{project-alias}:{spec-name}#{section} - Reference a specific section
    @shared:{resource-name}                - Reference a shared resource

Examples:
    @auth:user-session
    @billing:payment-processing#api-design
    @shared:common-types
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ldf.utils.logging import get_logger

if TYPE_CHECKING:
    from ldf.models.workspace import WorkspaceManifest

logger = get_logger(__name__)


# Regex patterns for reference parsing
# Matches: @project:spec or @project:spec#section
# Note: Allows dots in names to support specs like "api.v2" or "user.auth"
REFERENCE_PATTERN = re.compile(
    r"@(?P<project>[a-zA-Z0-9_.-]+):(?P<spec>[a-zA-Z0-9_.-]+)(?:#(?P<section>[a-zA-Z0-9_.-]+))?"
)

# Matches shared resource references: @shared:resource
SHARED_REFERENCE_PATTERN = re.compile(r"@shared:(?P<resource>[a-zA-Z0-9_.-]+)")


@dataclass
class SpecReference:
    """A parsed cross-project spec reference.

    Attributes:
        project: Project alias (e.g., "auth")
        spec: Spec name (e.g., "user-session")
        section: Optional section anchor (e.g., "api-design")
        raw: Original raw reference string
        line_number: Line number where reference was found (if known)
    """

    project: str
    spec: str
    section: str | None = None
    raw: str = ""
    line_number: int | None = None

    @property
    def is_shared(self) -> bool:
        """Check if this is a shared resource reference."""
        return self.project == "shared"

    def __str__(self) -> str:
        """String representation of the reference."""
        if self.section:
            return f"@{self.project}:{self.spec}#{self.section}"
        return f"@{self.project}:{self.spec}"


@dataclass
class ResolvedReference:
    """A resolved cross-project reference with path information.

    Attributes:
        reference: The original SpecReference
        resolved_path: Absolute path to the referenced spec/resource
        exists: Whether the referenced path exists
        error: Error message if resolution failed
    """

    reference: SpecReference
    resolved_path: Path | None = None
    exists: bool = False
    error: str | None = None


def parse_references(content: str, deduplicate: bool = True) -> list[SpecReference]:
    """Parse all cross-project references from content.

    Args:
        content: Markdown content to parse
        deduplicate: Whether to deduplicate references (default True).
                    When True, each unique reference (project:spec#section)
                    is returned only once, with the first line number found.

    Returns:
        List of parsed SpecReference objects
    """
    references = []
    seen: set[tuple[str, str, str | None]] = set()  # Track seen references for deduplication

    for line_num, line in enumerate(content.split("\n"), start=1):
        # Find all references in this line
        for match in REFERENCE_PATTERN.finditer(line):
            # Create a unique key for this reference
            key = (match.group("project"), match.group("spec"), match.group("section"))

            if deduplicate and key in seen:
                continue  # Skip duplicate references
            seen.add(key)

            ref = SpecReference(
                project=match.group("project"),
                spec=match.group("spec"),
                section=match.group("section"),
                raw=match.group(0),
                line_number=line_num,
            )
            references.append(ref)

        # Also check for shared resource references
        for match in SHARED_REFERENCE_PATTERN.finditer(line):
            # Create a unique key for shared reference
            key = ("shared", match.group("resource"), None)

            if deduplicate and key in seen:
                continue  # Skip duplicate references
            seen.add(key)

            ref = SpecReference(
                project="shared",
                spec=match.group("resource"),
                section=None,
                raw=match.group(0),
                line_number=line_num,
            )
            references.append(ref)

    return references


def parse_references_from_file(file_path: Path, deduplicate: bool = True) -> list[SpecReference]:
    """Parse all cross-project references from a file.

    Args:
        file_path: Path to the file to parse
        deduplicate: Whether to deduplicate references (default True)

    Returns:
        List of parsed SpecReference objects
    """
    if not file_path.exists():
        return []

    try:
        content = file_path.read_text()
        return parse_references(content, deduplicate=deduplicate)
    except Exception as e:
        logger.warning(f"Failed to parse references from {file_path}: {e}")
        return []


def resolve_reference(
    reference: SpecReference,
    workspace_root: Path,
    manifest: "WorkspaceManifest",
    shared_resources_path: Path | None = None,
) -> ResolvedReference:
    """Resolve a cross-project reference to a path.

    Args:
        reference: The reference to resolve
        workspace_root: Workspace root directory
        manifest: Parsed workspace manifest
        shared_resources_path: Path to .ldf-shared/ (optional)

    Returns:
        ResolvedReference with resolution status
    """
    # Handle shared resource references
    if reference.is_shared:
        if not shared_resources_path:
            return ResolvedReference(
                reference=reference,
                exists=False,
                error="No shared resources directory found",
            )

        # Look for shared resource in various locations
        possible_paths = [
            shared_resources_path / reference.spec,
            shared_resources_path / f"{reference.spec}.yaml",
            shared_resources_path / f"{reference.spec}.md",
        ]

        for path in possible_paths:
            if path.exists():
                return ResolvedReference(
                    reference=reference,
                    resolved_path=path,
                    exists=True,
                )

        return ResolvedReference(
            reference=reference,
            exists=False,
            error=f"Shared resource '{reference.spec}' not found in {shared_resources_path}",
        )

    # Resolve project alias to path
    project_path = None
    for entry in manifest.get_all_project_entries(workspace_root):
        if entry.alias == reference.project:
            project_path = (workspace_root / entry.path).resolve()
            break

    if project_path is None:
        available = [e.alias for e in manifest.get_all_project_entries(workspace_root)]
        return ResolvedReference(
            reference=reference,
            exists=False,
            error=f"Project '{reference.project}' not found. Available: {', '.join(available)}",
        )

    # Check if spec exists in target project
    spec_path = project_path / ".ldf" / "specs" / reference.spec

    if not spec_path.exists():
        return ResolvedReference(
            reference=reference,
            exists=False,
            error=f"Spec '{reference.spec}' not found in project '{reference.project}'",
        )

    # If section specified, check for section header in spec.md
    if reference.section:
        spec_md = spec_path / "spec.md"
        if spec_md.exists():
            content = spec_md.read_text()
            # Match section header (case-insensitive, any heading level)
            section_pattern = rf"^#+\s*{re.escape(reference.section)}\s*$"
            if not re.search(section_pattern, content, re.MULTILINE | re.IGNORECASE):
                return ResolvedReference(
                    reference=reference,
                    exists=False,
                    error=(
                        f"Section '{reference.section}' not found in "
                        f"'{reference.project}:{reference.spec}'"
                    ),
                )

    return ResolvedReference(
        reference=reference,
        resolved_path=spec_path,
        exists=True,
    )


def validate_references_in_spec(
    spec_path: Path,
    workspace_root: Path,
    manifest: "WorkspaceManifest",
    shared_resources_path: Path | None = None,
) -> list[ResolvedReference]:
    """Validate all cross-project references in a spec.

    Args:
        spec_path: Path to the spec directory
        workspace_root: Workspace root directory
        manifest: Parsed workspace manifest
        shared_resources_path: Path to .ldf-shared/

    Returns:
        List of ResolvedReference objects (includes both valid and invalid)
    """
    results = []

    # Check all markdown files in the spec
    for md_file in spec_path.glob("*.md"):
        references = parse_references_from_file(md_file)

        for ref in references:
            resolved = resolve_reference(ref, workspace_root, manifest, shared_resources_path)
            results.append(resolved)

    return results


def validate_all_workspace_references(
    workspace_root: Path,
) -> dict[str, list[ResolvedReference]]:
    """Validate all cross-project references across the workspace.

    Args:
        workspace_root: Workspace root directory

    Returns:
        Dictionary mapping project alias to list of reference validation results
    """
    import yaml

    from ldf.models.workspace import WorkspaceManifest
    from ldf.project_resolver import WORKSPACE_MANIFEST

    manifest_path = workspace_root / WORKSPACE_MANIFEST
    if not manifest_path.exists():
        return {}

    try:
        with open(manifest_path) as f:
            data = yaml.safe_load(f) or {}
        manifest = WorkspaceManifest.from_dict(data)
    except Exception as e:
        logger.error(f"Failed to load workspace manifest: {e}")
        return {}

    # Determine shared resources path
    _shared_path = workspace_root / manifest.shared.path
    shared_path: Path | None = _shared_path if _shared_path.exists() else None

    results: dict[str, list[ResolvedReference]] = {}

    # Import here to avoid circular imports
    from ldf.utils.security import is_safe_directory_entry

    for entry in manifest.get_all_project_entries(workspace_root):
        project_path = (workspace_root / entry.path).resolve()
        specs_dir = project_path / ".ldf" / "specs"

        if not specs_dir.exists():
            continue

        project_refs = []
        for spec_dir in specs_dir.iterdir():
            # Security: Check for symlink escape attacks
            if spec_dir.is_dir() and is_safe_directory_entry(spec_dir, specs_dir):
                spec_refs = validate_references_in_spec(
                    spec_dir, workspace_root, manifest, shared_path
                )
                project_refs.extend(spec_refs)

        if project_refs:
            results[entry.alias] = project_refs

    return results


def build_dependency_graph(
    workspace_root: Path,
) -> dict[str, set[str]]:
    """Build a dependency graph of cross-project references.

    Args:
        workspace_root: Workspace root directory

    Returns:
        Dictionary mapping project alias to set of referenced project aliases
    """
    all_refs = validate_all_workspace_references(workspace_root)

    graph: dict[str, set[str]] = {}

    for project, refs in all_refs.items():
        dependencies = set()
        for ref in refs:
            if ref.reference.project != "shared" and ref.exists:
                dependencies.add(ref.reference.project)

        if dependencies:
            graph[project] = dependencies

    return graph


def detect_circular_dependencies(graph: dict[str, set[str]]) -> list[list[str]]:
    """Detect circular dependencies in the reference graph.

    Args:
        graph: Dependency graph from build_dependency_graph()

    Returns:
        List of cycles found (each cycle is a list of project aliases)
    """
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor, path.copy())
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node, [])

    return cycles
