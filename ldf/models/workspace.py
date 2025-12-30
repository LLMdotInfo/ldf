"""Workspace data models for multi-project support.

These dataclasses represent the structure of ldf-workspace.yaml and related
workspace configuration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ProjectEntry:
    """A project entry in the workspace manifest.

    Attributes:
        path: Relative path from workspace root to project directory
        alias: Short name for CLI targeting (e.g., 'auth' for --project auth)
    """

    path: str
    alias: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectEntry":
        """Create from dictionary (YAML parsing)."""
        path = data.get("path", "")
        # Auto-generate alias from path if not provided
        alias = data.get("alias") or Path(path).name
        return cls(path=path, alias=alias)


@dataclass
class DiscoveryConfig:
    """Configuration for automatic project discovery.

    Attributes:
        patterns: Glob patterns to find projects (e.g., ["**/.ldf/config.yaml"])
        exclude: Directories to exclude from discovery
    """

    patterns: list[str] = field(default_factory=lambda: ["**/.ldf/config.yaml"])
    exclude: list[str] = field(default_factory=lambda: ["node_modules", ".venv", "vendor", ".git"])

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "DiscoveryConfig":
        """Create from dictionary."""
        if not data:
            return cls()
        return cls(
            patterns=data.get("patterns", ["**/.ldf/config.yaml"]),
            exclude=data.get("exclude", ["node_modules", ".venv", "vendor", ".git"]),
        )


@dataclass
class WorkspaceProjects:
    """Project configuration in workspace manifest.

    Attributes:
        explicit: Explicitly listed projects with paths and aliases
        discovery: Configuration for auto-discovering projects
    """

    explicit: list[ProjectEntry] = field(default_factory=list)
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "WorkspaceProjects":
        """Create from dictionary."""
        if not data:
            return cls()
        explicit = [ProjectEntry.from_dict(p) for p in data.get("explicit", [])]
        discovery = DiscoveryConfig.from_dict(data.get("discovery"))
        return cls(explicit=explicit, discovery=discovery)


@dataclass
class SharedConfig:
    """Configuration for shared resources.

    Attributes:
        path: Path to shared resources directory (relative to workspace root)
        inherit: Which resource types projects should inherit
    """

    path: str = ".ldf-shared/"
    inherit_guardrails: bool = True
    inherit_templates: bool = True
    inherit_question_packs: bool = True
    inherit_macros: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SharedConfig":
        """Create from dictionary."""
        if not data:
            return cls()
        inherit = data.get("inherit", {})
        return cls(
            path=data.get("path", cls.path),
            inherit_guardrails=inherit.get("guardrails", True),
            inherit_templates=inherit.get("templates", True),
            inherit_question_packs=inherit.get("question_packs", True),
            inherit_macros=inherit.get("macros", True),
        )


@dataclass
class ReferencesConfig:
    """Configuration for cross-project references.

    Attributes:
        enabled: Whether cross-project references are allowed
    """

    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ReferencesConfig":
        """Create from dictionary."""
        if not data:
            return cls()
        return cls(enabled=data.get("enabled", True))


@dataclass
class ReportingConfig:
    """Configuration for aggregated reporting.

    Attributes:
        enabled: Whether workspace-level reporting is enabled
        output_dir: Directory for report output
    """

    enabled: bool = True
    output_dir: str = ".ldf-reports/"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ReportingConfig":
        """Create from dictionary."""
        if not data:
            return cls()
        return cls(
            enabled=data.get("enabled", True),
            output_dir=data.get("output_dir", cls.output_dir),
        )


@dataclass
class WorkspaceManifest:
    """Parsed ldf-workspace.yaml manifest.

    This is the main configuration file for multi-project workspaces.

    Attributes:
        version: Schema version (e.g., "1.0")
        name: Workspace name
        projects: Project configuration (explicit list and discovery)
        shared: Shared resources configuration
        references: Cross-project reference configuration
        reporting: Aggregated reporting configuration
    """

    version: str
    name: str
    projects: WorkspaceProjects = field(default_factory=WorkspaceProjects)
    shared: SharedConfig = field(default_factory=SharedConfig)
    references: ReferencesConfig = field(default_factory=ReferencesConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkspaceManifest":
        """Create from dictionary (parsed YAML)."""
        return cls(
            version=data.get("version", "1.0"),
            name=data.get("name", ""),
            projects=WorkspaceProjects.from_dict(data.get("projects")),
            shared=SharedConfig.from_dict(data.get("shared")),
            references=ReferencesConfig.from_dict(data.get("references")),
            reporting=ReportingConfig.from_dict(data.get("reporting")),
        )

    def get_all_project_entries(
        self, workspace_root: Path | None = None, warn_collisions: bool = True
    ) -> list[ProjectEntry]:
        """Get all project entries (explicit and discovered).

        Args:
            workspace_root: If provided, also discover projects using glob patterns.
                           If None, only returns explicitly defined projects.
            warn_collisions: If True, log warnings for alias collisions (default: True).

        Returns:
            List of all project entries (explicit + discovered, deduplicated by path).
            Note: When alias collisions occur, earlier entries take precedence.
        """
        import warnings

        entries = list(self.projects.explicit)
        alias_to_path: dict[str, str] = {e.alias: e.path for e in entries}

        if workspace_root and self.projects.discovery.patterns:
            discovered = self._discover_projects(workspace_root)
            explicit_paths = {e.path for e in entries}
            for entry in discovered:
                if entry.path not in explicit_paths:
                    # Check for alias collision
                    if entry.alias in alias_to_path:
                        if warn_collisions:
                            warnings.warn(
                                f"Alias collision: '{entry.alias}' used by both "
                                f"'{alias_to_path[entry.alias]}' and '{entry.path}'. "
                                f"Using '{alias_to_path[entry.alias]}'. "
                                f"Add explicit alias in ldf-workspace.yaml to resolve.",
                                UserWarning,
                                stacklevel=2,
                            )
                        continue  # Skip the duplicate alias
                    entries.append(entry)
                    alias_to_path[entry.alias] = entry.path

        return entries

    def _discover_projects(self, workspace_root: Path) -> list[ProjectEntry]:
        """Discover projects using glob patterns.

        Args:
            workspace_root: The workspace root directory to search from.

        Returns:
            List of discovered project entries.
        """
        discovered = []
        for pattern in self.projects.discovery.patterns:
            for match in workspace_root.glob(pattern):
                # Check against exclude list using path parts (not substring matching)
                # This prevents false positives like "my-node_modules-project"
                should_exclude = any(
                    excl in match.parts for excl in self.projects.discovery.exclude
                )
                if should_exclude:
                    continue

                # Extract project path (parent of .ldf directory)
                # Pattern matches .ldf/config.yaml, so parent.parent is project root
                project_path = match.parent.parent
                try:
                    rel_path = str(project_path.relative_to(workspace_root))
                    if rel_path == ".":
                        continue  # Skip workspace root itself
                    discovered.append(ProjectEntry(path=rel_path, alias=project_path.name))
                except ValueError:
                    # Path is not relative to workspace_root, skip
                    continue

        return discovered


@dataclass
class ProjectInfo:
    """Cached information about a project in the registry.

    This is stored in .ldf-workspace/.registry.yaml for fast lookups.

    Attributes:
        path: Relative path from workspace root
        alias: CLI alias
        name: Project name from config
        version: Project version from config
        ldf_version: LDF version from config
        specs: List of spec names in this project
        coverage: Coverage percentage (if calculated)
        last_lint: Timestamp of last lint run
    """

    path: str
    alias: str
    name: str = ""
    version: str = ""
    ldf_version: str = ""
    specs: list[str] = field(default_factory=list)
    coverage: float | None = None
    last_lint: datetime | None = None

    @classmethod
    def from_dict(cls, alias: str, data: dict[str, Any]) -> "ProjectInfo":
        """Create from dictionary."""
        last_lint = None
        if data.get("last_lint"):
            try:
                last_lint = datetime.fromisoformat(data["last_lint"])
            except (ValueError, TypeError):
                pass

        return cls(
            path=data.get("path", ""),
            alias=alias,
            name=data.get("name", ""),
            version=data.get("version", ""),
            ldf_version=data.get("ldf_version", ""),
            specs=data.get("specs", []),
            coverage=data.get("coverage"),
            last_lint=last_lint,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result: dict[str, Any] = {
            "path": self.path,
            "name": self.name,
            "version": self.version,
            "ldf_version": self.ldf_version,
            "specs": self.specs,
        }
        if self.coverage is not None:
            result["coverage"] = self.coverage
        if self.last_lint:
            result["last_lint"] = self.last_lint.isoformat()
        return result
