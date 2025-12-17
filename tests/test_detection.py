"""Tests for ldf.detection module."""

import pytest
import yaml
from pathlib import Path

from ldf import __version__
from ldf.detection import (
    ProjectState,
    DetectionResult,
    detect_project_state,
    check_ldf_completeness,
    get_specs_summary,
    REQUIRED_FILES,
    REQUIRED_DIRS,
)


class TestProjectState:
    """Tests for ProjectState enum."""

    def test_state_values(self):
        """Test that all expected states exist."""
        assert ProjectState.NEW.value == "new"
        assert ProjectState.CURRENT.value == "current"
        assert ProjectState.OUTDATED.value == "outdated"
        assert ProjectState.LEGACY.value == "legacy"
        assert ProjectState.PARTIAL.value == "partial"
        assert ProjectState.CORRUPTED.value == "corrupted"


class TestDetectionResult:
    """Tests for DetectionResult dataclass."""

    def test_to_dict(self, tmp_path):
        """Test conversion to dictionary."""
        result = DetectionResult(
            state=ProjectState.NEW,
            project_root=tmp_path,
            installed_version="0.1.0",
            project_version=None,
            has_config=False,
            has_guardrails=False,
            has_specs_dir=False,
            has_answerpacks_dir=False,
            has_templates=False,
            has_macros=False,
            has_claude_md=False,
            has_claude_commands=False,
            missing_files=["config.yaml"],
            invalid_files=[],
            recommended_action="Run 'ldf init'",
            recommended_command="ldf init",
        )

        d = result.to_dict()
        assert d["state"] == "new"
        assert d["installed_version"] == "0.1.0"
        assert d["project_version"] is None
        assert d["completeness"]["config"] is False
        assert "config.yaml" in d["missing_files"]
        assert d["recommended_command"] == "ldf init"

    def test_to_json(self, tmp_path):
        """Test conversion to JSON string."""
        result = DetectionResult(
            state=ProjectState.CURRENT,
            project_root=tmp_path,
            installed_version="0.1.0",
            project_version="0.1.0",
            has_config=True,
            has_guardrails=True,
            has_specs_dir=True,
            has_answerpacks_dir=True,
            has_templates=True,
            has_macros=True,
            has_claude_md=True,
            has_claude_commands=True,
        )

        json_str = result.to_json()
        assert '"state": "current"' in json_str
        assert '"installed_version": "0.1.0"' in json_str


class TestDetectProjectState:
    """Tests for detect_project_state function."""

    def test_new_project_no_ldf_dir(self, tmp_path):
        """Test detection of new project without .ldf directory."""
        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.NEW
        assert result.project_root == tmp_path
        assert result.installed_version == __version__
        assert result.project_version is None
        assert result.has_config is False
        assert result.recommended_command == "ldf init"

    def test_corrupted_ldf_is_file(self, tmp_path):
        """Test detection when .ldf exists as a file, not directory."""
        ldf_file = tmp_path / ".ldf"
        ldf_file.write_text("not a directory")

        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.CORRUPTED
        assert ".ldf (not a directory)" in result.invalid_files
        assert "force" in result.recommended_command

    def test_current_project_matching_version(self, tmp_path):
        """Test detection of up-to-date project."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create required structure
        (ldf_dir / "config.yaml").write_text(f"framework_version: '{__version__}'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "specs").mkdir()
        (ldf_dir / "answerpacks").mkdir()
        (ldf_dir / "templates").mkdir()
        (ldf_dir / "question-packs").mkdir()
        (ldf_dir / "macros").mkdir()
        (ldf_dir / "templates" / "requirements.md").write_text("# Requirements")
        (ldf_dir / "templates" / "design.md").write_text("# Design")
        (ldf_dir / "templates" / "tasks.md").write_text("# Tasks")
        (ldf_dir / "macros" / "clarify-first.md").write_text("# Clarify")
        (ldf_dir / "macros" / "coverage-gate.md").write_text("# Coverage")
        (ldf_dir / "macros" / "task-guardrails.md").write_text("# Task")
        (ldf_dir / "question-packs" / "core.yaml").write_text("pack: core")

        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.CURRENT
        assert result.project_version == __version__
        assert result.has_config is True
        assert result.has_guardrails is True
        assert result.recommended_command is None

    def test_outdated_project_older_version(self, tmp_path):
        """Test detection of project with older framework version."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create structure with old version
        (ldf_dir / "config.yaml").write_text("framework_version: '0.0.1'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "specs").mkdir()
        (ldf_dir / "answerpacks").mkdir()
        (ldf_dir / "templates").mkdir()
        (ldf_dir / "question-packs").mkdir()
        (ldf_dir / "macros").mkdir()
        (ldf_dir / "templates" / "requirements.md").write_text("# Requirements")
        (ldf_dir / "templates" / "design.md").write_text("# Design")
        (ldf_dir / "templates" / "tasks.md").write_text("# Tasks")
        (ldf_dir / "macros" / "clarify-first.md").write_text("# Clarify")
        (ldf_dir / "macros" / "coverage-gate.md").write_text("# Coverage")
        (ldf_dir / "macros" / "task-guardrails.md").write_text("# Task")
        (ldf_dir / "question-packs" / "core.yaml").write_text("pack: core")

        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.OUTDATED
        assert result.project_version == "0.0.1"
        assert "update" in result.recommended_command

    def test_legacy_project_no_version(self, tmp_path):
        """Test detection of legacy project without framework_version."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create config without framework_version
        (ldf_dir / "config.yaml").write_text("project_name: test")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "specs").mkdir()
        (ldf_dir / "answerpacks").mkdir()
        (ldf_dir / "templates").mkdir()
        (ldf_dir / "question-packs").mkdir()
        (ldf_dir / "macros").mkdir()
        (ldf_dir / "templates" / "requirements.md").write_text("# Requirements")
        (ldf_dir / "templates" / "design.md").write_text("# Design")
        (ldf_dir / "templates" / "tasks.md").write_text("# Tasks")
        (ldf_dir / "macros" / "clarify-first.md").write_text("# Clarify")
        (ldf_dir / "macros" / "coverage-gate.md").write_text("# Coverage")
        (ldf_dir / "macros" / "task-guardrails.md").write_text("# Task")
        (ldf_dir / "question-packs" / "core.yaml").write_text("pack: core")

        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.LEGACY
        assert result.project_version is None
        assert "update" in result.recommended_command

    def test_partial_project_missing_templates(self, tmp_path):
        """Test detection of project missing some required files."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create minimal structure
        (ldf_dir / "config.yaml").write_text(f"framework_version: '{__version__}'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "specs").mkdir()
        (ldf_dir / "answerpacks").mkdir()
        (ldf_dir / "templates").mkdir()
        (ldf_dir / "question-packs").mkdir()
        (ldf_dir / "question-packs" / "core.yaml").write_text("pack: core")
        # Missing template files and macros

        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.PARTIAL
        assert len(result.missing_files) > 0
        assert "repair" in result.recommended_command

    def test_corrupted_project_invalid_yaml(self, tmp_path):
        """Test detection of project with invalid YAML config."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create invalid YAML
        (ldf_dir / "config.yaml").write_text("invalid: yaml: content: [")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "specs").mkdir()
        (ldf_dir / "answerpacks").mkdir()

        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.CORRUPTED
        assert len(result.invalid_files) > 0
        assert "force" in result.recommended_command

    def test_corrupted_project_empty_config(self, tmp_path):
        """Test detection of project with empty config file."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create empty config
        (ldf_dir / "config.yaml").write_text("")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "specs").mkdir()
        (ldf_dir / "answerpacks").mkdir()

        result = detect_project_state(tmp_path)

        assert result.state == ProjectState.CORRUPTED
        assert any("empty" in f for f in result.invalid_files)

    def test_detection_uses_cwd_when_no_path(self, tmp_path, monkeypatch):
        """Test that detection uses current directory when no path given."""
        monkeypatch.chdir(tmp_path)
        result = detect_project_state()
        assert result.project_root == tmp_path

    def test_detection_with_claude_md(self, tmp_path):
        """Test detection recognizes CLAUDE.md."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (tmp_path / "CLAUDE.md").write_text("# Claude Instructions")
        (ldf_dir / "config.yaml").write_text(f"framework_version: '{__version__}'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        for d in ["specs", "answerpacks", "templates", "question-packs", "macros"]:
            (ldf_dir / d).mkdir()
        (ldf_dir / "templates" / "requirements.md").write_text("#")
        (ldf_dir / "templates" / "design.md").write_text("#")
        (ldf_dir / "templates" / "tasks.md").write_text("#")
        (ldf_dir / "macros" / "clarify-first.md").write_text("#")
        (ldf_dir / "macros" / "coverage-gate.md").write_text("#")
        (ldf_dir / "macros" / "task-guardrails.md").write_text("#")
        (ldf_dir / "question-packs" / "core.yaml").write_text("pack: core")

        result = detect_project_state(tmp_path)
        assert result.has_claude_md is True

    def test_detection_with_claude_commands(self, tmp_path):
        """Test detection recognizes .claude/commands directory."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        claude_commands = tmp_path / ".claude" / "commands"
        claude_commands.mkdir(parents=True)
        (ldf_dir / "config.yaml").write_text(f"framework_version: '{__version__}'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        for d in ["specs", "answerpacks", "templates", "question-packs", "macros"]:
            (ldf_dir / d).mkdir()
        (ldf_dir / "templates" / "requirements.md").write_text("#")
        (ldf_dir / "templates" / "design.md").write_text("#")
        (ldf_dir / "templates" / "tasks.md").write_text("#")
        (ldf_dir / "macros" / "clarify-first.md").write_text("#")
        (ldf_dir / "macros" / "coverage-gate.md").write_text("#")
        (ldf_dir / "macros" / "task-guardrails.md").write_text("#")
        (ldf_dir / "question-packs" / "core.yaml").write_text("pack: core")

        result = detect_project_state(tmp_path)
        assert result.has_claude_commands is True


class TestCheckLdfCompleteness:
    """Tests for check_ldf_completeness function."""

    def test_empty_ldf_dir(self, tmp_path):
        """Test completeness check on empty .ldf directory."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        missing, invalid = check_ldf_completeness(ldf_dir)

        # Should be missing required files and dirs
        assert "config.yaml" in missing
        assert "guardrails.yaml" in missing
        assert any("specs" in m for m in missing)

    def test_complete_ldf_dir(self, tmp_path):
        """Test completeness check on complete .ldf directory."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create all required files
        (ldf_dir / "config.yaml").write_text("framework_version: '0.1.0'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        for d in REQUIRED_DIRS:
            (ldf_dir / d).mkdir()
        (ldf_dir / "macros").mkdir()  # macros not in REQUIRED_DIRS but needed for completeness
        (ldf_dir / "templates" / "requirements.md").write_text("#")
        (ldf_dir / "templates" / "design.md").write_text("#")
        (ldf_dir / "templates" / "tasks.md").write_text("#")
        (ldf_dir / "macros" / "clarify-first.md").write_text("#")
        (ldf_dir / "macros" / "coverage-gate.md").write_text("#")
        (ldf_dir / "macros" / "task-guardrails.md").write_text("#")
        (ldf_dir / "question-packs" / "core.yaml").write_text("pack: core")

        missing, invalid = check_ldf_completeness(ldf_dir)

        assert len(missing) == 0
        assert len(invalid) == 0

    def test_directory_is_file(self, tmp_path):
        """Test detection of file where directory expected."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        # Create 'specs' as a file instead of directory
        (ldf_dir / "config.yaml").write_text("framework_version: '0.1.0'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "specs").write_text("not a directory")

        missing, invalid = check_ldf_completeness(ldf_dir)

        assert "specs (not a directory)" in invalid


class TestGetSpecsSummary:
    """Tests for get_specs_summary function."""

    def test_no_specs_dir(self, tmp_path):
        """Test summary when specs directory doesn't exist."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        summary = get_specs_summary(ldf_dir)
        assert summary == []

    def test_empty_specs_dir(self, tmp_path):
        """Test summary when specs directory is empty."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "specs").mkdir()

        summary = get_specs_summary(ldf_dir)
        assert summary == []

    def test_specs_with_various_states(self, tmp_path):
        """Test summary with specs in various states."""
        ldf_dir = tmp_path / ".ldf"
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir(parents=True)

        # Spec with only requirements
        (specs_dir / "auth").mkdir()
        (specs_dir / "auth" / "requirements.md").write_text("# Auth Requirements")

        # Spec with requirements and design
        (specs_dir / "billing").mkdir()
        (specs_dir / "billing" / "requirements.md").write_text("# Billing Requirements")
        (specs_dir / "billing" / "design.md").write_text("# Billing Design")

        # Spec with all three
        (specs_dir / "complete").mkdir()
        (specs_dir / "complete" / "requirements.md").write_text("# Complete Requirements")
        (specs_dir / "complete" / "design.md").write_text("# Complete Design")
        (specs_dir / "complete" / "tasks.md").write_text("# Complete Tasks")

        # Empty spec
        (specs_dir / "empty").mkdir()

        summary = get_specs_summary(ldf_dir)

        # Should be sorted by name
        assert len(summary) == 4
        assert summary[0]["name"] == "auth"
        assert summary[0]["status"] == "requirements"

        assert summary[1]["name"] == "billing"
        assert summary[1]["status"] == "design"

        assert summary[2]["name"] == "complete"
        assert summary[2]["status"] == "tasks"

        assert summary[3]["name"] == "empty"
        assert summary[3]["status"] == "empty"

    def test_skips_non_directories(self, tmp_path):
        """Test that non-directory items in specs are skipped."""
        ldf_dir = tmp_path / ".ldf"
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir(parents=True)

        (specs_dir / "valid-spec").mkdir()
        (specs_dir / "valid-spec" / "requirements.md").write_text("# Valid")
        (specs_dir / "not-a-spec.txt").write_text("just a file")

        summary = get_specs_summary(ldf_dir)

        assert len(summary) == 1
        assert summary[0]["name"] == "valid-spec"
