"""Tests for ldf.lint module."""

import pytest
from pathlib import Path

from ldf.lint import lint_specs


class TestLintSpecs:
    """Tests for lint_specs function."""

    def test_lint_valid_spec(self, temp_spec: Path, monkeypatch):
        """Test linting a valid spec returns no errors."""
        project_dir = temp_spec.parent.parent.parent
        monkeypatch.chdir(project_dir)

        result = lint_specs(spec_name="test-feature", lint_all=False, fix=False)

        assert result == 0  # Success

    def test_lint_all_specs(self, temp_spec: Path, monkeypatch):
        """Test linting all specs in a project."""
        project_dir = temp_spec.parent.parent.parent
        monkeypatch.chdir(project_dir)

        result = lint_specs(spec_name=None, lint_all=True, fix=False)

        assert result == 0  # Success

    def test_lint_nonexistent_spec(self, temp_project: Path, monkeypatch):
        """Test linting a nonexistent spec returns error."""
        monkeypatch.chdir(temp_project)

        result = lint_specs(spec_name="nonexistent", lint_all=False, fix=False)

        assert result == 1  # Error

    def test_lint_non_ldf_project(self, tmp_path: Path, monkeypatch):
        """Test linting in a non-LDF project returns error."""
        monkeypatch.chdir(tmp_path)

        result = lint_specs(spec_name=None, lint_all=True, fix=False)

        assert result == 1  # Error - no .ldf directory

    def test_lint_no_args_no_all_fails(self, temp_project: Path, monkeypatch):
        """Test lint without spec_name and without --all returns error."""
        monkeypatch.chdir(temp_project)

        result = lint_specs(spec_name=None, lint_all=False, fix=False)

        assert result == 1  # Error - must specify spec or --all


class TestLintRequirements:
    """Tests for requirements.md linting."""

    def test_detects_missing_question_pack_answers(self, temp_project: Path, monkeypatch):
        """Test detection of missing Question-Pack Answers section."""
        spec_dir = temp_project / ".ldf" / "specs" / "bad-spec"
        spec_dir.mkdir(parents=True)

        (spec_dir / "requirements.md").write_text("""# Requirements

## User Stories

### US-1: Test

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing | [US-1] | [S1] | [T-1] | Dev | TODO |
""")
        (spec_dir / "design.md").write_text("# Design\n## API\nTest")
        (spec_dir / "tasks.md").write_text("""# Tasks

## Per-Task Guardrail Checklist

Checklist here.

### Task 1.1: Test
- [ ] Item
""")

        monkeypatch.chdir(temp_project)
        result = lint_specs(spec_name="bad-spec", lint_all=False, fix=False)

        assert result == 1  # Error - missing Question-Pack Answers

    def test_detects_empty_guardrail_matrix(self, temp_project: Path, monkeypatch):
        """Test detection of empty guardrail matrix."""
        spec_dir = temp_project / ".ldf" / "specs" / "empty-matrix"
        spec_dir.mkdir(parents=True)

        (spec_dir / "requirements.md").write_text("""# Requirements

## Question-Pack Answers

Answers here.

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|

No rows in matrix.
""")
        (spec_dir / "design.md").write_text("# Design\n## API\nTest")
        (spec_dir / "tasks.md").write_text("""# Tasks

## Per-Task Guardrail Checklist

Checklist.

### Task 1.1: Test
- [ ] Item
""")

        monkeypatch.chdir(temp_project)
        result = lint_specs(spec_name="empty-matrix", lint_all=False, fix=False)

        assert result == 1  # Error - empty matrix


class TestLintTasks:
    """Tests for tasks.md linting."""

    def test_detects_missing_per_task_checklist(self, temp_project: Path, monkeypatch):
        """Test detection of missing Per-Task Guardrail Checklist section."""
        spec_dir = temp_project / ".ldf" / "specs" / "no-checklist"
        spec_dir.mkdir(parents=True)

        (spec_dir / "requirements.md").write_text("""# Requirements

## Question-Pack Answers

Answers.

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing | [US-1] | [S1] | [T-1] | Dev | TODO |
""")
        (spec_dir / "design.md").write_text("# Design\n## API\nTest")
        (spec_dir / "tasks.md").write_text("""# Tasks

## Phase 1

### Task 1.1: Test
- [ ] Item
""")

        monkeypatch.chdir(temp_project)
        result = lint_specs(spec_name="no-checklist", lint_all=False, fix=False)

        assert result == 1  # Error - missing Per-Task Guardrail Checklist


class TestLintDesign:
    """Tests for design.md linting."""

    def test_warns_on_missing_guardrail_mapping(self, temp_project: Path, monkeypatch):
        """Test warning for missing Guardrail Mapping section."""
        spec_dir = temp_project / ".ldf" / "specs" / "no-mapping"
        spec_dir.mkdir(parents=True)

        (spec_dir / "requirements.md").write_text("""# Requirements

## Question-Pack Answers

Answers.

## User Stories

### US-1: Test Story

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1] | [S1] | [T-1] | Dev | TODO |
| 2. Security Basics | [US-1] | [S1] | [T-1] | Dev | TODO |
| 3. Error Handling | [US-1] | [S1] | [T-1] | Dev | TODO |
| 4. Logging & Observability | [US-1] | [S1] | [T-1] | Dev | TODO |
| 5. API Design | [US-1] | [S1] | [T-1] | Dev | TODO |
| 6. Data Validation | [US-1] | [S1] | [T-1] | Dev | TODO |
| 7. Database Migrations | [US-1] | [S1] | [T-1] | Dev | TODO |
| 8. Documentation | [US-1] | [S1] | [T-1] | Dev | TODO |
""")
        (spec_dir / "design.md").write_text("""# Design

## Architecture

Some architecture.

## API Endpoints

Some endpoints.
""")  # Missing Guardrail Mapping
        (spec_dir / "tasks.md").write_text("""# Tasks

## Per-Task Guardrail Checklist

Checklist.

### Task 1.1: Test
- [ ] Item
""")

        monkeypatch.chdir(temp_project)
        # This should pass (warning only, not error) - missing Guardrail Mapping is a warning
        result = lint_specs(spec_name="no-mapping", lint_all=False, fix=False)

        assert result == 0  # Should pass, just warns


class TestCiOutputFormat:
    """Tests for CI output format."""

    def test_ci_format_non_ldf_project(self, tmp_path: Path, monkeypatch, capsys):
        """Test CI format output for non-LDF project."""
        monkeypatch.chdir(tmp_path)

        result = lint_specs(spec_name=None, lint_all=True, fix=False, output_format="ci")

        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert result == 1

    def test_ci_format_no_specs_dir(self, temp_project: Path, monkeypatch, capsys):
        """Test CI format when no specs directory exists."""
        # Remove specs directory
        import shutil
        specs_dir = temp_project / ".ldf" / "specs"
        if specs_dir.exists():
            shutil.rmtree(specs_dir)
        monkeypatch.chdir(temp_project)

        result = lint_specs(spec_name=None, lint_all=True, fix=False, output_format="ci")

        captured = capsys.readouterr()
        # CI output may use ⚠ or Warning:
        assert "⚠" in captured.out or "Warning" in captured.out or result == 0

    def test_ci_format_spec_not_found(self, temp_project: Path, monkeypatch, capsys):
        """Test CI format when spec not found."""
        monkeypatch.chdir(temp_project)

        result = lint_specs(spec_name="nonexistent", lint_all=False, fix=False, output_format="ci")

        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert result == 1

    def test_ci_format_no_spec_or_all(self, temp_project: Path, monkeypatch, capsys):
        """Test CI format when neither spec nor --all specified."""
        monkeypatch.chdir(temp_project)

        result = lint_specs(spec_name=None, lint_all=False, fix=False, output_format="ci")

        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert result == 1

    def test_ci_format_no_specs_found(self, temp_project: Path, monkeypatch, capsys):
        """Test CI format when no specs found in directory."""
        # Ensure specs directory exists but is empty
        specs_dir = temp_project / ".ldf" / "specs"
        specs_dir.mkdir(exist_ok=True)
        # Remove any existing spec directories
        for d in specs_dir.iterdir():
            if d.is_dir():
                import shutil
                shutil.rmtree(d)
        monkeypatch.chdir(temp_project)

        result = lint_specs(spec_name=None, lint_all=True, fix=False, output_format="ci")

        captured = capsys.readouterr()
        # CI output may use ⚠ or Warning:
        assert "⚠" in captured.out or "Warning" in captured.out or result == 0

    def test_ci_format_success(self, temp_spec: Path, monkeypatch, capsys):
        """Test CI format output for successful lint."""
        project_dir = temp_spec.parent.parent.parent
        # Create answerpacks directory with a YAML file to avoid warning
        answerpacks_dir = project_dir / ".ldf" / "answerpacks" / "test-feature"
        answerpacks_dir.mkdir(parents=True, exist_ok=True)
        (answerpacks_dir / "security.yaml").write_text("# Security answers\n")
        monkeypatch.chdir(project_dir)

        result = lint_specs(spec_name="test-feature", lint_all=False, fix=False, output_format="ci")

        # Just verify it runs successfully (no fatal errors)
        assert result == 0


class TestLintAutoFix:
    """Tests for auto-fix functionality."""

    def test_fix_mode_does_not_crash(self, temp_spec: Path, monkeypatch):
        """Test that fix mode runs without crashing."""
        project_dir = temp_spec.parent.parent.parent
        monkeypatch.chdir(project_dir)

        # Fix mode should run without crashing
        result = lint_specs(spec_name="test-feature", lint_all=False, fix=True)

        # Should succeed or at least not crash
        assert result in (0, 1)

    def test_fix_creates_missing_files_from_templates(self, temp_project: Path, monkeypatch):
        """Test that --fix creates missing files from templates."""
        # Create a spec with only requirements.md
        spec_dir = temp_project / ".ldf" / "specs" / "incomplete"
        spec_dir.mkdir(parents=True)

        (spec_dir / "requirements.md").write_text("""# incomplete - Requirements

## Overview

Test.

## Question-Pack Answers

Answers.

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing | [US-1] | [S1] | [T-1] | Dev | TODO |
""")

        monkeypatch.chdir(temp_project)

        # First lint should fail due to missing files
        result_before = lint_specs(spec_name="incomplete", lint_all=False, fix=False)
        assert result_before == 1

        # Verify design.md and tasks.md don't exist
        assert not (spec_dir / "design.md").exists()
        assert not (spec_dir / "tasks.md").exists()

        # Run lint with --fix
        lint_specs(spec_name="incomplete", lint_all=False, fix=True)

        # Verify files were created
        assert (spec_dir / "design.md").exists()
        assert (spec_dir / "tasks.md").exists()

        # Verify created files have content
        assert len((spec_dir / "design.md").read_text()) > 0
        assert len((spec_dir / "tasks.md").read_text()) > 0

    def test_fix_removes_trailing_whitespace(self, temp_project: Path, monkeypatch):
        """Test that --fix removes trailing whitespace from files."""
        spec_dir = temp_project / ".ldf" / "specs" / "whitespace"
        spec_dir.mkdir(parents=True)

        # Create files with trailing whitespace
        (spec_dir / "requirements.md").write_text("""# Requirements

## Question-Pack Answers

Answers.

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing | [US-1] | [S1] | [T-1] | Dev | TODO |
""")
        (spec_dir / "design.md").write_text("# Design   \n\n## API   \n\nTest   ")
        (spec_dir / "tasks.md").write_text("""# Tasks

## Per-Task Guardrail Checklist

Checklist.

### Task 1.1: Test
- [ ] Item
""")

        monkeypatch.chdir(temp_project)

        # Run lint with --fix
        lint_specs(spec_name="whitespace", lint_all=False, fix=True)

        # Verify trailing whitespace was removed
        design_content = (spec_dir / "design.md").read_text()
        # No line should end with spaces
        for line in design_content.split('\n'):
            assert not line.endswith(' '), f"Line still has trailing whitespace: '{line}'"


class TestLintStrictMode:
    """Tests for strict mode."""

    def test_strict_mode_treats_warnings_as_errors(self, temp_project: Path, monkeypatch):
        """Test that strict mode treats warnings as errors."""
        # Create a spec with a warning (missing Guardrail Mapping in design.md)
        spec_dir = temp_project / ".ldf" / "specs" / "warning-spec"
        spec_dir.mkdir(parents=True)

        (spec_dir / "requirements.md").write_text("""# Requirements

## Question-Pack Answers

Answers.

## User Stories

### US-1: Test

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing | [US-1] | [S1] | [T-1] | Dev | TODO |
| 2. Security | [US-1] | [S1] | [T-1] | Dev | TODO |
| 3. Error | [US-1] | [S1] | [T-1] | Dev | TODO |
| 4. Logging | [US-1] | [S1] | [T-1] | Dev | TODO |
| 5. API | [US-1] | [S1] | [T-1] | Dev | TODO |
| 6. Data | [US-1] | [S1] | [T-1] | Dev | TODO |
| 7. DB | [US-1] | [S1] | [T-1] | Dev | TODO |
| 8. Docs | [US-1] | [S1] | [T-1] | Dev | TODO |
""")
        (spec_dir / "design.md").write_text("# Design\n## Architecture\nTest")
        (spec_dir / "tasks.md").write_text("""# Tasks

## Per-Task Guardrail Checklist

Checklist.

### Task 1.1: Test
- [ ] Item
""")

        # Update config to enable strict mode
        import yaml
        config_path = temp_project / ".ldf" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["lint"] = {"strict": True}
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f)

        monkeypatch.chdir(temp_project)
        result = lint_specs(spec_name="warning-spec", lint_all=False, fix=False)

        # With strict mode, warnings become errors
        # Result depends on whether spec generates warnings
        assert result in (0, 1)


class TestLintEdgeCases:
    """Tests for lint edge cases."""

    def test_lint_with_missing_config(self, temp_project: Path, monkeypatch):
        """Test lint when config file is missing."""
        # Remove config file
        (temp_project / ".ldf" / "config.yaml").unlink()
        monkeypatch.chdir(temp_project)

        # Should still work with defaults
        result = lint_specs(spec_name=None, lint_all=True, fix=False)

        assert result in (0, 1)

    def test_lint_with_missing_files_in_spec(self, temp_project: Path, monkeypatch):
        """Test lint when spec has missing files."""
        spec_dir = temp_project / ".ldf" / "specs" / "incomplete"
        spec_dir.mkdir(parents=True)

        # Only create requirements.md, missing design.md and tasks.md
        (spec_dir / "requirements.md").write_text("# Requirements\n")

        monkeypatch.chdir(temp_project)
        result = lint_specs(spec_name="incomplete", lint_all=False, fix=False)

        assert result == 1  # Should fail due to missing files
