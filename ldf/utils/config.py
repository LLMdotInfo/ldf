"""LDF configuration utilities."""

from pathlib import Path
from typing import Any

import yaml


def load_config(project_root: Path | None = None) -> dict[str, Any]:
    """Load LDF configuration from .ldf/config.yaml.

    Args:
        project_root: Project root directory (defaults to cwd)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    if project_root is None:
        project_root = Path.cwd()

    config_path = project_root / ".ldf" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"LDF config not found: {config_path}\n"
            "Run 'ldf init' to initialize the project."
        )

    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def get_config_value(key: str, default: Any = None, project_root: Path | None = None) -> Any:
    """Get a specific configuration value using dot notation.

    Args:
        key: Configuration key (e.g., "guardrails.preset")
        default: Default value if key not found
        project_root: Project root directory

    Returns:
        Configuration value or default
    """
    try:
        config = load_config(project_root)
    except FileNotFoundError:
        return default

    parts = key.split(".")
    value = config

    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return default

    return value


def get_specs_dir(project_root: Path | None = None) -> Path:
    """Get the specs directory path.

    Args:
        project_root: Project root directory

    Returns:
        Path to specs directory
    """
    if project_root is None:
        project_root = Path.cwd()

    specs_dir = get_config_value("project.specs_dir", ".ldf/specs", project_root)
    return project_root / str(specs_dir)


def get_answerpacks_dir(project_root: Path | None = None) -> Path:
    """Get the answerpacks directory path.

    Args:
        project_root: Project root directory

    Returns:
        Path to answerpacks directory
    """
    if project_root is None:
        project_root = Path.cwd()

    return project_root / ".ldf" / "answerpacks"


def get_templates_dir(project_root: Path | None = None) -> Path:
    """Get the templates directory path.

    Args:
        project_root: Project root directory

    Returns:
        Path to templates directory
    """
    if project_root is None:
        project_root = Path.cwd()

    return project_root / ".ldf" / "templates"


def get_default_config() -> dict[str, Any]:
    """Get default LDF configuration."""
    return {
        "version": "1.0",
        "project": {
            "name": "unnamed",
            "specs_dir": ".ldf/specs",
        },
        "guardrails": {
            "preset": "custom",
            "overrides": {},
        },
        "question_packs": ["security", "testing", "api-design", "data-model"],
        "mcp_servers": ["spec-inspector", "coverage-reporter"],
        "lint": {
            "strict": False,
            "auto_fix": False,
        },
        "hooks": {
            "enabled": False,
            "pre_commit": {
                "run_on_all_commits": True,
                "strict": False,
                "spec_lint": True,
                "python": {
                    "enabled": False,
                    "tools": ["ruff"],
                },
                "typescript": {
                    "enabled": False,
                    "tools": ["eslint"],
                },
                "go": {
                    "enabled": False,
                    "tools": ["golangci-lint"],
                },
            },
        },
    }


def save_config(config: dict[str, Any], project_root: Path | None = None) -> None:
    """Save LDF configuration to .ldf/config.yaml.

    Args:
        config: Configuration dictionary
        project_root: Project root directory (defaults to cwd)
    """
    if project_root is None:
        project_root = Path.cwd()

    config_path = project_root / ".ldf" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
