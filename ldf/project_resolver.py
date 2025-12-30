"""Project resolution for multi-project workspace support.

This module provides the ProjectResolver class which resolves project context
from CLI arguments, environment variables, and filesystem detection.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ldf.models.workspace import WorkspaceManifest


# Workspace manifest filename
WORKSPACE_MANIFEST = "ldf-workspace.yaml"


def find_workspace_root(start_path: Path | None = None) -> Path | None:
    """Find workspace root by walking up from a starting path.

    Args:
        start_path: Directory to start searching from. Defaults to cwd.

    Returns:
        Path to workspace root (containing ldf-workspace.yaml), or None if not found
    """
    current = (start_path or Path.cwd()).resolve()

    while current != current.parent:
        if (current / WORKSPACE_MANIFEST).exists():
            return current
        current = current.parent

    return None


@dataclass
class ProjectContext:
    """Resolved project context for command execution.

    This dataclass contains all the information needed to execute LDF commands
    in the context of a specific project, whether standalone or part of a workspace.

    Attributes:
        project_root: Absolute path to the project directory (contains .ldf/)
        workspace_root: Absolute path to workspace root (contains ldf-workspace.yaml),
                       None if not in a workspace
        project_alias: Short alias for the project (from workspace config),
                      None if not in a workspace
        is_workspace_member: True if this project is part of a workspace
        shared_resources_path: Path to .ldf-shared/ directory, None if not applicable
    """

    project_root: Path
    workspace_root: Path | None = None
    project_alias: str | None = None
    is_workspace_member: bool = False
    shared_resources_path: Path | None = None

    @property
    def ldf_dir(self) -> Path:
        """Path to the .ldf/ directory."""
        return self.project_root / ".ldf"

    @property
    def config_path(self) -> Path:
        """Path to the project's config.yaml."""
        return self.ldf_dir / "config.yaml"

    @property
    def specs_dir(self) -> Path:
        """Path to the specs directory."""
        return self.ldf_dir / "specs"


class ProjectNotFoundError(Exception):
    """Raised when a project cannot be found or resolved."""

    def __init__(self, message: str, available_projects: list[str] | None = None):
        super().__init__(message)
        self.available_projects = available_projects or []


class WorkspaceNotFoundError(Exception):
    """Raised when a workspace cannot be found."""

    pass


class ProjectResolver:
    """Resolves project context from CLI args, environment, and filesystem.

    The resolver follows this precedence order:
    1. Explicit --project argument (resolves alias to path via workspace)
    2. Explicit --workspace argument (then looks for project in cwd)
    3. LDF_PROJECT environment variable
    4. Find ldf-workspace.yaml walking up from cwd, then resolve cwd project
    5. Find .ldf/config.yaml in cwd (single-project mode)
    6. Error: no project found

    Usage:
        resolver = ProjectResolver()
        context = resolver.resolve(project="auth")  # By alias
        context = resolver.resolve()  # Auto-detect from cwd
    """

    def __init__(self, cwd: Path | None = None):
        """Initialize the resolver.

        Args:
            cwd: Current working directory override (defaults to Path.cwd())
        """
        self._cwd = cwd or Path.cwd()
        self._workspace_cache: tuple[Path, WorkspaceManifest] | None = None

    def resolve(
        self,
        project: str | None = None,
        workspace: str | Path | None = None,
    ) -> ProjectContext:
        """Resolve project context.

        Args:
            project: Project alias or path to target
            workspace: Explicit workspace root path

        Returns:
            ProjectContext with resolved paths and metadata

        Raises:
            ProjectNotFoundError: If project cannot be found
            WorkspaceNotFoundError: If workspace is specified but not found
        """
        import os

        # 1. Check environment variable if no explicit args
        if project is None and workspace is None:
            env_project = os.environ.get("LDF_PROJECT")
            if env_project:
                project = env_project

        # 2. If explicit workspace specified, use it
        workspace_root: Path | None = None
        manifest: WorkspaceManifest | None = None

        if workspace:
            workspace_root = Path(workspace).resolve()
            manifest = self._load_workspace_manifest(workspace_root)
            if manifest is None:
                raise WorkspaceNotFoundError(f"No ldf-workspace.yaml found at {workspace_root}")

        # 3. If project specified, we need workspace context to resolve alias
        if project:
            if workspace_root is None:
                # Try to find workspace by walking up
                workspace_root = self._find_workspace_root(self._cwd)
                if workspace_root:
                    manifest = self._load_workspace_manifest(workspace_root)

            if manifest and workspace_root:
                # Resolve project alias to path
                return self._resolve_project_in_workspace(project, workspace_root, manifest)
            else:
                # No workspace - treat project as a path
                project_path = Path(project).resolve()
                if self._is_ldf_project(project_path):
                    return ProjectContext(project_root=project_path)
                raise ProjectNotFoundError(f"'{project}' is not a valid project path or alias")

        # 4. No explicit project - try to detect from cwd
        if workspace_root is None:
            workspace_root = self._find_workspace_root(self._cwd)
            if workspace_root:
                manifest = self._load_workspace_manifest(workspace_root)

        # 5. If in workspace, find which project cwd is in
        if workspace_root and manifest:
            context = self._resolve_cwd_in_workspace(workspace_root, manifest)
            if context:
                return context

        # 6. Fall back to single-project mode
        if self._is_ldf_project(self._cwd):
            return ProjectContext(project_root=self._cwd)

        # 7. No project found
        raise ProjectNotFoundError(
            f"No LDF project found at {self._cwd}. "
            "Run 'ldf init' to create one, or use --project to specify a project."
        )

    def _find_workspace_root(self, start_path: Path) -> Path | None:
        """Walk up from start_path looking for ldf-workspace.yaml.

        Args:
            start_path: Directory to start searching from

        Returns:
            Path to workspace root, or None if not found
        """
        current = start_path.resolve()

        while current != current.parent:
            manifest_path = current / WORKSPACE_MANIFEST
            if manifest_path.exists():
                return current
            current = current.parent

        return None

    def _load_workspace_manifest(self, workspace_root: Path) -> "WorkspaceManifest | None":
        """Load and parse workspace manifest.

        Args:
            workspace_root: Path containing ldf-workspace.yaml

        Returns:
            Parsed WorkspaceManifest, or None if not found/invalid
        """
        from ldf.models.workspace import WorkspaceManifest

        manifest_path = workspace_root / WORKSPACE_MANIFEST
        if not manifest_path.exists():
            return None

        try:
            import yaml

            with open(manifest_path) as f:
                data = yaml.safe_load(f) or {}
            return WorkspaceManifest.from_dict(data)
        except yaml.YAMLError as e:
            # Surface YAML parsing errors - these indicate a broken config
            logger.warning(f"Failed to parse workspace manifest {manifest_path}: {e}")
            raise WorkspaceNotFoundError(f"Invalid workspace manifest at {manifest_path}: {e}")
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            # Surface validation errors from WorkspaceManifest.from_dict
            # AttributeError catches cases like passing a string where dict expected
            logger.warning(f"Invalid workspace manifest structure {manifest_path}: {e}")
            raise WorkspaceNotFoundError(
                f"Invalid workspace manifest structure at {manifest_path}: {e}"
            )
        except Exception as e:
            # Log unexpected errors but don't raise to allow fallback
            logger.warning(f"Unexpected error loading workspace manifest: {e}")
            return None

    def _is_ldf_project(self, path: Path) -> bool:
        """Check if a directory is an LDF project.

        Args:
            path: Directory to check

        Returns:
            True if path contains .ldf/config.yaml
        """
        config_path = path / ".ldf" / "config.yaml"
        return config_path.exists()

    def _resolve_project_in_workspace(
        self,
        project: str,
        workspace_root: Path,
        manifest: "WorkspaceManifest",
    ) -> ProjectContext:
        """Resolve a project alias to a ProjectContext within a workspace.

        Args:
            project: Project alias or relative path
            workspace_root: Workspace root directory
            manifest: Parsed workspace manifest

        Returns:
            Resolved ProjectContext

        Raises:
            ProjectNotFoundError: If alias/path not found in workspace
        """
        # Get all project entries (including discovered projects)
        entries = manifest.get_all_project_entries(workspace_root)
        available = [e.alias for e in entries]

        # Try to find by alias
        for entry in entries:
            if entry.alias == project:
                project_path = (workspace_root / entry.path).resolve()
                if self._is_ldf_project(project_path):
                    return self._build_workspace_context(
                        project_path, entry.alias, workspace_root, manifest
                    )
                raise ProjectNotFoundError(
                    f"Project '{project}' found in workspace but {project_path} "
                    "is not a valid LDF project (missing .ldf/config.yaml)",
                    available_projects=available,
                )

        # Try to find by path
        for entry in entries:
            if entry.path == project:
                project_path = (workspace_root / entry.path).resolve()
                if self._is_ldf_project(project_path):
                    return self._build_workspace_context(
                        project_path, entry.alias, workspace_root, manifest
                    )

        raise ProjectNotFoundError(
            f"Project '{project}' not found in workspace. "
            f"Available projects: {', '.join(available)}",
            available_projects=available,
        )

    def _resolve_cwd_in_workspace(
        self,
        workspace_root: Path,
        manifest: "WorkspaceManifest",
    ) -> ProjectContext | None:
        """Find which project the current directory is in.

        Args:
            workspace_root: Workspace root directory
            manifest: Parsed workspace manifest

        Returns:
            ProjectContext if cwd is within a workspace project, None otherwise
        """
        cwd = self._cwd.resolve()

        for entry in manifest.get_all_project_entries(workspace_root):
            project_path = (workspace_root / entry.path).resolve()

            # Check if cwd is within this project
            try:
                cwd.relative_to(project_path)
                if self._is_ldf_project(project_path):
                    return self._build_workspace_context(
                        project_path, entry.alias, workspace_root, manifest
                    )
            except ValueError:
                continue

        return None

    def _build_workspace_context(
        self,
        project_path: Path,
        alias: str,
        workspace_root: Path,
        manifest: "WorkspaceManifest",
    ) -> ProjectContext:
        """Build a ProjectContext for a workspace member.

        Args:
            project_path: Absolute path to project
            alias: Project alias
            workspace_root: Workspace root
            manifest: Workspace manifest

        Returns:
            Fully populated ProjectContext
        """
        shared_path = None
        if manifest.shared.inherit_guardrails or manifest.shared.inherit_templates:
            shared_path = workspace_root / manifest.shared.path
            if not shared_path.exists():
                shared_path = None

        return ProjectContext(
            project_root=project_path,
            workspace_root=workspace_root,
            project_alias=alias,
            is_workspace_member=True,
            shared_resources_path=shared_path,
        )
