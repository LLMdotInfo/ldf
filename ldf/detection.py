"""LDF project detection and analysis.

Detects the state of LDF projects and analyzes existing codebases for conversion.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from ldf import __version__
from ldf.utils.security import is_safe_directory_entry


class ProjectState(Enum):
    """Detected LDF project state."""

    NEW = "new"  # No .ldf/ directory
    CURRENT = "current"  # Up to date with installed LDF version
    OUTDATED = "outdated"  # ldf.version < installed version
    LEGACY = "legacy"  # Has .ldf/ but no ldf.version in config
    PARTIAL = "partial"  # Has some LDF files but incomplete setup
    CORRUPTED = "corrupted"  # Missing critical files or invalid config


@dataclass
class DetectionResult:
    """Result of project detection."""

    state: ProjectState
    project_root: Path
    installed_version: str
    project_version: str | None

    # Completeness info
    has_config: bool
    has_guardrails: bool
    has_specs_dir: bool
    has_answerpacks_dir: bool
    has_question_packs_dir: bool
    has_templates: bool
    has_macros: bool
    has_agent_md: bool
    has_agent_commands: bool

    # Workspace info (None if not in a workspace)
    workspace_root: Path | None = None
    is_workspace_member: bool = False
    project_alias: str | None = None
    shared_resources_path: Path | None = None

    # Missing/invalid items
    missing_files: list[str] = field(default_factory=list)
    invalid_files: list[str] = field(default_factory=list)

    # Recommendation
    recommended_action: str = ""
    recommended_command: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON output."""
        result: dict[str, Any] = {
            "state": self.state.value,
            "project_root": str(self.project_root),
            "installed_version": self.installed_version,
            "project_version": self.project_version,
            "completeness": {
                "config": self.has_config,
                "guardrails": self.has_guardrails,
                "specs_dir": self.has_specs_dir,
                "answerpacks_dir": self.has_answerpacks_dir,
                "question_packs_dir": self.has_question_packs_dir,
                "templates": self.has_templates,
                "macros": self.has_macros,
                "agent_md": self.has_agent_md,
                "agent_commands": self.has_agent_commands,
            },
            "missing_files": self.missing_files,
            "invalid_files": self.invalid_files,
            "recommended_action": self.recommended_action,
            "recommended_command": self.recommended_command,
        }

        # Add workspace info if in a workspace
        if self.is_workspace_member:
            result["workspace"] = {
                "workspace_root": str(self.workspace_root) if self.workspace_root else None,
                "is_workspace_member": self.is_workspace_member,
                "project_alias": self.project_alias,
                "shared_resources_path": str(self.shared_resources_path)
                if self.shared_resources_path
                else None,
            }

        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# Required files for a complete LDF setup
REQUIRED_FILES = [
    "config.yaml",
    "guardrails.yaml",
]

REQUIRED_DIRS = [
    "specs",
    "answerpacks",
    "templates",
    "question-packs",
]

REQUIRED_TEMPLATES = [
    "templates/requirements.md",
    "templates/design.md",
    "templates/tasks.md",
]

REQUIRED_MACROS = [
    "macros/clarify-first.md",
    "macros/coverage-gate.md",
    "macros/task-guardrails.md",
]


def detect_project_state(project_root: Path | None = None) -> DetectionResult:
    """Detect the LDF state of a project.

    Args:
        project_root: Project directory (defaults to cwd)

    Returns:
        DetectionResult with full state information
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root).resolve()

    ldf_dir = project_root / ".ldf"

    # Check if .ldf directory exists
    if not ldf_dir.exists():
        return DetectionResult(
            state=ProjectState.NEW,
            project_root=project_root,
            installed_version=__version__,
            project_version=None,
            has_config=False,
            has_guardrails=False,
            has_specs_dir=False,
            has_answerpacks_dir=False,
            has_question_packs_dir=False,
            has_templates=False,
            has_macros=False,
            has_agent_md=False,
            has_agent_commands=False,
            recommended_action="Run 'ldf init' to initialize LDF in this project.",
            recommended_command="ldf init",
        )

    # Check if .ldf is actually a directory
    if not ldf_dir.is_dir():
        return DetectionResult(
            state=ProjectState.CORRUPTED,
            project_root=project_root,
            installed_version=__version__,
            project_version=None,
            has_config=False,
            has_guardrails=False,
            has_specs_dir=False,
            has_answerpacks_dir=False,
            has_question_packs_dir=False,
            has_templates=False,
            has_macros=False,
            has_agent_md=False,
            has_agent_commands=False,
            invalid_files=[".ldf (not a directory)"],
            recommended_action="Remove .ldf file and run 'ldf init --force'.",
            recommended_command="ldf init --force",
        )

    # Check completeness
    missing_files, invalid_files = check_ldf_completeness(ldf_dir)

    # Check individual components
    has_config = (ldf_dir / "config.yaml").exists()
    has_guardrails = (ldf_dir / "guardrails.yaml").exists()
    has_specs_dir = (ldf_dir / "specs").is_dir()
    has_answerpacks_dir = (ldf_dir / "answerpacks").is_dir()
    has_question_packs_dir = (ldf_dir / "question-packs").is_dir()
    template_files = ["templates/requirements.md", "templates/design.md", "templates/tasks.md"]
    has_templates = all((ldf_dir / t).exists() for t in template_files)
    has_macros = (ldf_dir / "macros").is_dir() and any((ldf_dir / "macros").iterdir())
    has_agent_md = (project_root / "AGENT.md").exists()
    has_agent_commands = (project_root / ".agent" / "commands").is_dir()

    # Load config to check version
    project_version = None
    config_valid = False

    if has_config:
        try:
            with open(ldf_dir / "config.yaml") as f:
                config = yaml.safe_load(f)
                if config is None:
                    invalid_files.append("config.yaml (empty)")
                elif not isinstance(config, dict):
                    invalid_files.append("config.yaml (invalid format)")
                else:
                    config_valid = True
                    # Read version from v1.1 schema (ldf.version)
                    if "ldf" in config and isinstance(config["ldf"], dict):
                        project_version = config["ldf"].get("version")
        except yaml.YAMLError as e:
            invalid_files.append(f"config.yaml (parse error: {e})")
        except Exception as e:
            invalid_files.append(f"config.yaml (read error: {e})")

    # Determine state based on findings
    if invalid_files:
        state = ProjectState.CORRUPTED
        recommended_action = "Config is corrupted. Run 'ldf init --force' to reinitialize."
        recommended_command = "ldf init --force"
    elif not config_valid:
        state = ProjectState.CORRUPTED
        recommended_action = "Missing or invalid config. Run 'ldf init --force' to reinitialize."
        recommended_command = "ldf init --force"
    elif project_version is None:
        state = ProjectState.LEGACY
        recommended_action = "Legacy LDF format detected. Run 'ldf update' to upgrade."
        recommended_command = "ldf update"
    elif missing_files:
        state = ProjectState.PARTIAL
        files_preview = ", ".join(missing_files[:3])
        recommended_action = f"Missing files: {files_preview}. Run 'ldf init --repair'."
        recommended_command = "ldf init --repair"
    elif project_version == __version__:
        state = ProjectState.CURRENT
        recommended_action = "LDF is up to date. No action needed."
        recommended_command = None
    else:
        # Compare versions
        try:
            from packaging.version import Version

            if Version(project_version) < Version(__version__):
                state = ProjectState.OUTDATED
                recommended_action = (
                    f"Update available ({project_version} → {__version__}). Run 'ldf update'."
                )
                recommended_command = "ldf update"
            else:
                # Project is newer than installed (edge case)
                state = ProjectState.CURRENT
                recommended_action = (
                    f"Project uses newer LDF ({project_version}). Consider upgrading LDF CLI."
                )
                recommended_command = None
        except Exception:
            # Fall back to string comparison if packaging not available
            if project_version != __version__:
                state = ProjectState.OUTDATED
                recommended_action = (
                    f"Version mismatch ({project_version} → {__version__}). Run 'ldf update'."
                )
                recommended_command = "ldf update"
            else:
                state = ProjectState.CURRENT
                recommended_action = "LDF is up to date. No action needed."
                recommended_command = None

    # Detect workspace context
    workspace_root, is_workspace_member, project_alias, shared_resources_path = (
        _detect_workspace_context(project_root)
    )

    return DetectionResult(
        state=state,
        project_root=project_root,
        installed_version=__version__,
        project_version=project_version,
        has_config=has_config,
        has_guardrails=has_guardrails,
        has_specs_dir=has_specs_dir,
        has_answerpacks_dir=has_answerpacks_dir,
        has_question_packs_dir=has_question_packs_dir,
        has_templates=has_templates,
        has_macros=has_macros,
        has_agent_md=has_agent_md,
        has_agent_commands=has_agent_commands,
        workspace_root=workspace_root,
        is_workspace_member=is_workspace_member,
        project_alias=project_alias,
        shared_resources_path=shared_resources_path,
        missing_files=missing_files,
        invalid_files=invalid_files,
        recommended_action=recommended_action,
        recommended_command=recommended_command,
    )


def check_ldf_completeness(ldf_dir: Path) -> tuple[list[str], list[str]]:
    """Check completeness of LDF setup.

    Args:
        ldf_dir: Path to .ldf directory

    Returns:
        Tuple of (missing_files, invalid_files)
    """
    missing = []
    invalid = []

    # Check required files
    for file in REQUIRED_FILES:
        path = ldf_dir / file
        if not path.exists():
            missing.append(file)

    # Check required directories
    for dir_name in REQUIRED_DIRS:
        path = ldf_dir / dir_name
        if not path.exists():
            missing.append(f"{dir_name}/")
        elif not path.is_dir():
            invalid.append(f"{dir_name} (not a directory)")

    # Check templates
    for template in REQUIRED_TEMPLATES:
        path = ldf_dir / template
        if not path.exists():
            missing.append(template)

    # Check macros (optional but recommended)
    macros_dir = ldf_dir / "macros"
    if macros_dir.exists() and macros_dir.is_dir():
        for macro in REQUIRED_MACROS:
            path = ldf_dir / macro
            if not path.exists():
                missing.append(macro)

    # Check question-packs is non-empty (check both root and subdirectories)
    qp_dir = ldf_dir / "question-packs"
    if qp_dir.exists() and qp_dir.is_dir():
        has_packs = any(qp_dir.glob("*.yaml"))  # Legacy flat structure
        if not has_packs:
            # Check new core/optional subdirectories
            core_packs = any((qp_dir / "core").glob("*.yaml"))
            optional_packs = any((qp_dir / "optional").glob("*.yaml"))
            has_packs = core_packs or optional_packs
        if not has_packs:
            missing.append("question-packs/*.yaml (no packs found)")

    return missing, invalid


def get_specs_summary(ldf_dir: Path) -> list[dict]:
    """Get summary of specs in the project.

    Args:
        ldf_dir: Path to .ldf directory

    Returns:
        List of spec info dicts with name and status
    """
    specs: list[dict[str, str | bool]] = []
    specs_dir = ldf_dir / "specs"

    if not specs_dir.exists():
        return specs

    for spec_dir in specs_dir.iterdir():
        # Filter out symlinks escaping specs_dir and hidden directories
        if not spec_dir.is_dir() or not is_safe_directory_entry(spec_dir, specs_dir):
            continue

        spec_info: dict[str, str | bool] = {
            "name": spec_dir.name,
            "has_requirements": (spec_dir / "requirements.md").exists(),
            "has_design": (spec_dir / "design.md").exists(),
            "has_tasks": (spec_dir / "tasks.md").exists(),
        }

        # Determine status
        if spec_info["has_tasks"]:
            spec_info["status"] = "tasks"
        elif spec_info["has_design"]:
            spec_info["status"] = "design"
        elif spec_info["has_requirements"]:
            spec_info["status"] = "requirements"
        else:
            spec_info["status"] = "empty"

        specs.append(spec_info)

    return sorted(specs, key=lambda x: x["name"])


def _detect_workspace_context(
    project_root: Path,
) -> tuple[Path | None, bool, str | None, Path | None]:
    """Detect workspace context for a project.

    Walks up from project_root looking for ldf-workspace.yaml and determines
    if the project is part of a workspace.

    Args:
        project_root: Path to the project directory

    Returns:
        Tuple of (workspace_root, is_workspace_member, project_alias, shared_resources_path)
        All values are None/False if not in a workspace.
    """
    from ldf.project_resolver import WORKSPACE_MANIFEST

    # Walk up looking for workspace manifest
    current = project_root.resolve()

    while current != current.parent:
        manifest_path = current / WORKSPACE_MANIFEST
        if manifest_path.exists():
            # Found a workspace, try to load it
            try:
                from ldf.models.workspace import WorkspaceManifest

                with open(manifest_path) as f:
                    data = yaml.safe_load(f) or {}
                manifest = WorkspaceManifest.from_dict(data)

                # Check if this project is in the workspace
                for entry in manifest.get_all_project_entries(current):
                    entry_path = (current / entry.path).resolve()
                    try:
                        # Check if project_root is within or equal to entry_path
                        project_root.resolve().relative_to(entry_path)
                        # Found our project in the workspace
                        shared_path = None
                        if manifest.shared.inherit_guardrails or manifest.shared.inherit_templates:
                            potential_shared = current / manifest.shared.path
                            if potential_shared.exists():
                                shared_path = potential_shared

                        return current, True, entry.alias, shared_path
                    except ValueError:
                        continue

                # Workspace exists but project not registered in it
                # Still return workspace_root for context but is_workspace_member=False
                return current, False, None, None

            except Exception:
                # Failed to parse workspace - continue without workspace context
                return None, False, None, None

        current = current.parent

    # No workspace found
    return None, False, None, None


def detect_workspace_state(workspace_root: Path) -> dict:
    """Detect the state of a workspace.

    Args:
        workspace_root: Path to workspace root (containing ldf-workspace.yaml)

    Returns:
        Dictionary with workspace state information including:
        - name: Workspace name
        - projects: List of project info dicts
        - shared: Shared resources info
        - status: Overall workspace health status
    """
    from ldf.project_resolver import WORKSPACE_MANIFEST

    manifest_path = workspace_root / WORKSPACE_MANIFEST

    if not manifest_path.exists():
        return {
            "status": "not_found",
            "error": f"No {WORKSPACE_MANIFEST} found at {workspace_root}",
        }

    try:
        from ldf.models.workspace import WorkspaceManifest

        with open(manifest_path) as f:
            data = yaml.safe_load(f) or {}
        manifest = WorkspaceManifest.from_dict(data)

        # Gather project info
        projects = []
        for entry in manifest.get_all_project_entries(workspace_root):
            project_path = (workspace_root / entry.path).resolve()
            project_info = {
                "alias": entry.alias,
                "path": entry.path,
                "exists": project_path.exists(),
                "has_ldf": (project_path / ".ldf" / "config.yaml").exists(),
            }

            # Get basic detection if project exists
            if project_info["has_ldf"]:
                detection = detect_project_state(project_path)
                project_info["state"] = detection.state.value
                project_info["version"] = detection.project_version
            else:
                project_info["state"] = "new" if project_info["exists"] else "missing"
                project_info["version"] = None

            projects.append(project_info)

        # Check shared resources
        shared_path = workspace_root / manifest.shared.path
        shared_info = {
            "path": manifest.shared.path,
            "exists": shared_path.exists(),
            "inherit_guardrails": manifest.shared.inherit_guardrails,
            "inherit_templates": manifest.shared.inherit_templates,
        }

        if shared_path.exists():
            shared_info["has_guardrails"] = (shared_path / "guardrails").is_dir()
            shared_info["has_templates"] = (shared_path / "templates").is_dir()

        return {
            "status": "ok",
            "name": manifest.name,
            "version": manifest.version,
            "projects": projects,
            "shared": shared_info,
            "references_enabled": manifest.references.enabled,
            "reporting_enabled": manifest.reporting.enabled,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to parse workspace manifest: {e}",
        }
