"""Tests for ldf.doctor module."""

from pathlib import Path

import pytest
import yaml

from ldf.doctor import (
    CheckResult,
    CheckStatus,
    DoctorReport,
    check_config,
    check_git_hooks,
    check_guardrails,
    check_mcp_deps,
    check_mcp_json,
    check_mcp_servers,
    check_project_structure,
    check_question_packs,
    check_required_deps,
    print_report,
    run_doctor,
)


class TestCheckProjectStructure:
    """Tests for check_project_structure function."""

    def test_passes_with_valid_structure(self, temp_project: Path):
        """Test passing when .ldf/ exists with required dirs."""
        # Create required directories
        ldf_dir = temp_project / ".ldf"
        for d in ["specs", "question-packs", "templates", "macros"]:
            (ldf_dir / d).mkdir(exist_ok=True)

        result = check_project_structure(temp_project)

        assert result.status == CheckStatus.PASS
        assert ".ldf/ exists" in result.message

    def test_fails_without_ldf_dir(self, tmp_path: Path):
        """Test failure when .ldf/ doesn't exist."""
        result = check_project_structure(tmp_path)

        assert result.status == CheckStatus.FAIL
        assert ".ldf/ directory not found" in result.message
        assert result.fix_hint is not None

    def test_warns_on_missing_subdirs(self, temp_project: Path):
        """Test warning when subdirectories are missing."""
        # Remove a required directory
        specs_dir = temp_project / ".ldf" / "specs"
        if specs_dir.exists():
            specs_dir.rmdir()

        result = check_project_structure(temp_project)

        assert result.status == CheckStatus.WARN
        assert "Missing directories" in result.message


class TestCheckConfig:
    """Tests for check_config function."""

    def test_passes_with_valid_config(self, temp_project: Path):
        """Test passing with valid config.yaml."""
        result = check_config(temp_project)

        assert result.status == CheckStatus.PASS
        assert "config.yaml valid" in result.message

    def test_fails_without_config(self, tmp_path: Path):
        """Test failure when config.yaml doesn't exist."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        result = check_config(tmp_path)

        assert result.status == CheckStatus.FAIL
        assert "not found" in result.message

    def test_fails_with_invalid_yaml(self, temp_project: Path):
        """Test failure with invalid YAML."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("invalid: yaml: [[[")

        result = check_config(temp_project)

        assert result.status == CheckStatus.FAIL
        assert "YAML parse error" in result.message

    def test_fails_with_non_mapping(self, temp_project: Path):
        """Test failure when config is not a mapping."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("- just\n- a\n- list")

        result = check_config(temp_project)

        assert result.status == CheckStatus.FAIL
        assert "not a valid YAML mapping" in result.message

    def test_warns_on_missing_version(self, temp_project: Path):
        """Test warning when version key is missing."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("project:\n  name: test")

        result = check_config(temp_project)

        assert result.status == CheckStatus.WARN
        assert "Missing keys" in result.message


class TestCheckGuardrails:
    """Tests for check_guardrails function."""

    def test_passes_with_valid_guardrails(self, temp_project: Path):
        """Test passing with valid guardrails.yaml."""
        result = check_guardrails(temp_project)

        assert result.status == CheckStatus.PASS
        assert "guardrails.yaml valid" in result.message

    def test_fails_without_guardrails(self, temp_project: Path):
        """Test failure when guardrails.yaml doesn't exist."""
        guardrails_path = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_path.unlink()

        result = check_guardrails(temp_project)

        assert result.status == CheckStatus.FAIL
        assert "not found" in result.message

    def test_fails_with_invalid_yaml(self, temp_project: Path):
        """Test failure with invalid YAML."""
        guardrails_path = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_path.write_text("invalid: yaml: [[[")

        result = check_guardrails(temp_project)

        assert result.status == CheckStatus.FAIL
        assert "YAML parse error" in result.message

    def test_fails_with_non_mapping(self, temp_project: Path):
        """Test failure when guardrails is not a mapping."""
        guardrails_path = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_path.write_text("- just\n- a\n- list")

        result = check_guardrails(temp_project)

        assert result.status == CheckStatus.FAIL
        assert "not a valid YAML mapping" in result.message


class TestCheckQuestionPacks:
    """Tests for check_question_packs function."""

    def test_warns_without_config(self, temp_project: Path):
        """Test warning when config.yaml is missing."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.unlink()

        result = check_question_packs(temp_project)

        assert result.status == CheckStatus.WARN
        assert "config.yaml missing" in result.message

    def test_passes_with_no_packs_configured(self, temp_project: Path):
        """Test passing when no packs are configured."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nquestion_packs: []")

        result = check_question_packs(temp_project)

        assert result.status == CheckStatus.PASS
        assert "No question packs configured" in result.message

    def test_passes_with_all_packs_present(self, temp_project: Path):
        """Test passing when all configured packs exist."""
        # Update config with a pack
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nquestion_packs:\n  - test-pack")

        # Create the pack file
        packs_dir = temp_project / ".ldf" / "question-packs"
        packs_dir.mkdir(exist_ok=True)
        (packs_dir / "test-pack.yaml").write_text("name: test-pack")

        result = check_question_packs(temp_project)

        assert result.status == CheckStatus.PASS
        assert "1/1 packs found" in result.message

    def test_warns_with_missing_packs(self, temp_project: Path):
        """Test warning when configured packs don't exist."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nquestion_packs:\n  - missing-pack")

        packs_dir = temp_project / ".ldf" / "question-packs"
        packs_dir.mkdir(exist_ok=True)

        result = check_question_packs(temp_project)

        assert result.status == CheckStatus.WARN
        assert "missing-pack" in result.message

    def test_fails_without_packs_dir(self, temp_project: Path):
        """Test failure when question-packs dir doesn't exist."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nquestion_packs:\n  - test-pack")

        # Remove packs dir if it exists
        packs_dir = temp_project / ".ldf" / "question-packs"
        if packs_dir.exists():
            packs_dir.rmdir()

        result = check_question_packs(temp_project)

        assert result.status == CheckStatus.FAIL

    def test_warns_with_invalid_config_yaml(self, temp_project: Path):
        """Test warning when config.yaml is invalid YAML."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("invalid: yaml: [[[")

        result = check_question_packs(temp_project)

        assert result.status == CheckStatus.WARN
        assert "config.yaml invalid" in result.message


class TestCheckMcpServers:
    """Tests for check_mcp_servers function."""

    def test_warns_without_config(self, tmp_path: Path):
        """Test warning when config.yaml is missing."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        result = check_mcp_servers(tmp_path)

        assert result.status == CheckStatus.WARN

    def test_passes_with_no_servers(self, temp_project: Path):
        """Test passing when no MCP servers are configured."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nmcp_servers: []")

        result = check_mcp_servers(temp_project)

        assert result.status == CheckStatus.PASS
        assert "No MCP servers configured" in result.message

    def test_passes_with_valid_servers(self, temp_project: Path):
        """Test passing when configured servers exist."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nmcp_servers:\n  - spec-inspector")

        result = check_mcp_servers(temp_project)

        assert result.status == CheckStatus.PASS
        assert "servers available" in result.message

    def test_warns_with_invalid_yaml(self, temp_project: Path):
        """Test warning when config.yaml is invalid YAML."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("invalid: yaml: [[[")

        result = check_mcp_servers(temp_project)

        assert result.status == CheckStatus.WARN


class TestCheckRequiredDeps:
    """Tests for check_required_deps function."""

    def test_passes_with_all_deps(self):
        """Test passing when all required deps are installed."""
        result = check_required_deps()

        assert result.status == CheckStatus.PASS
        assert "All required packages installed" in result.message


class TestCheckMcpDeps:
    """Tests for check_mcp_deps function."""

    def test_passes_without_config(self, tmp_path: Path):
        """Test passing when config.yaml doesn't exist."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        result = check_mcp_deps(tmp_path)

        assert result.status == CheckStatus.PASS
        assert "No MCP servers configured" in result.message

    def test_passes_without_mcp_servers(self, temp_project: Path):
        """Test passing when no MCP servers are configured."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nmcp_servers: []")

        result = check_mcp_deps(temp_project)

        assert result.status == CheckStatus.PASS

    def test_warns_with_invalid_yaml(self, temp_project: Path):
        """Test warning when config.yaml is invalid YAML."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("invalid: yaml: [[[")

        result = check_mcp_deps(temp_project)

        assert result.status == CheckStatus.WARN


class TestCheckGitHooks:
    """Tests for check_git_hooks function."""

    def test_passes_without_git(self, temp_project: Path):
        """Test passing when not a git repository."""
        result = check_git_hooks(temp_project)

        assert result.status == CheckStatus.PASS
        assert "Not a git repository" in result.message

    def test_passes_without_pre_commit(self, temp_project: Path):
        """Test passing when no pre-commit hook exists."""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "hooks").mkdir()

        result = check_git_hooks(temp_project)

        assert result.status == CheckStatus.PASS
        assert "No pre-commit hook installed" in result.message

    def test_passes_with_ldf_hook(self, temp_project: Path):
        """Test passing when LDF pre-commit hook is installed."""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir()
        pre_commit = hooks_dir / "pre-commit"
        pre_commit.write_text("#!/bin/sh\nldf lint\n")

        result = check_git_hooks(temp_project)

        assert result.status == CheckStatus.PASS
        assert "LDF pre-commit hook installed" in result.message

    def test_passes_with_non_ldf_hook(self, temp_project: Path):
        """Test passing when non-LDF pre-commit hook is installed."""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir()
        pre_commit = hooks_dir / "pre-commit"
        pre_commit.write_text("#!/bin/sh\necho 'hello'\n")

        result = check_git_hooks(temp_project)

        assert result.status == CheckStatus.PASS
        assert "Non-LDF pre-commit hook" in result.message


class TestCheckMcpJson:
    """Tests for check_mcp_json function."""

    def test_passes_without_mcp_json(self, temp_project: Path):
        """Test passing when .claude/mcp.json doesn't exist."""
        result = check_mcp_json(temp_project)

        assert result.status == CheckStatus.PASS
        assert "not present" in result.message

    def test_warns_with_mcp_json_no_config(self, tmp_path: Path):
        """Test warning when mcp.json exists but no LDF config."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "mcp.json").write_text('{"mcpServers": {}}')

        result = check_mcp_json(tmp_path)

        assert result.status == CheckStatus.WARN
        assert "no LDF config" in result.message

    def test_passes_with_no_servers_configured(self, temp_project: Path):
        """Test passing when no LDF servers are configured."""
        config_path = temp_project / ".ldf" / "config.yaml"
        config_path.write_text("version: '1.0'\nmcp_servers: []")

        claude_dir = temp_project / ".claude"
        claude_dir.mkdir()
        (claude_dir / "mcp.json").write_text('{"mcpServers": {}}')

        result = check_mcp_json(temp_project)

        assert result.status == CheckStatus.PASS

    def test_warns_on_invalid_json(self, temp_project: Path):
        """Test warning when mcp.json is invalid JSON."""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir()
        (claude_dir / "mcp.json").write_text("not valid json")

        result = check_mcp_json(temp_project)

        assert result.status == CheckStatus.WARN
        assert "Parse error" in result.message


class TestRunDoctor:
    """Tests for run_doctor function."""

    def test_runs_all_checks(self, temp_project: Path):
        """Test that all checks are run."""
        # Create required structure
        ldf_dir = temp_project / ".ldf"
        for d in ["specs", "question-packs", "templates", "macros"]:
            (ldf_dir / d).mkdir(exist_ok=True)

        report = run_doctor(temp_project)

        assert len(report.checks) >= 8  # At least 8 checks
        assert report.passed > 0

    def test_uses_cwd_when_none(self, temp_project: Path, monkeypatch):
        """Test using current directory when project_root is None."""
        monkeypatch.chdir(temp_project)

        report = run_doctor(None)

        assert len(report.checks) > 0


class TestDoctorReport:
    """Tests for DoctorReport dataclass."""

    def test_counts_statuses(self):
        """Test counting passed/warnings/failed."""
        report = DoctorReport(
            checks=[
                CheckResult("A", CheckStatus.PASS, "OK"),
                CheckResult("B", CheckStatus.PASS, "OK"),
                CheckResult("C", CheckStatus.WARN, "Warning"),
                CheckResult("D", CheckStatus.FAIL, "Failed"),
            ]
        )

        assert report.passed == 2
        assert report.warnings == 1
        assert report.failed == 1
        assert report.success is False

    def test_success_without_failures(self):
        """Test success is True when no failures."""
        report = DoctorReport(
            checks=[
                CheckResult("A", CheckStatus.PASS, "OK"),
                CheckResult("B", CheckStatus.WARN, "Warning"),
            ]
        )

        assert report.success is True

    def test_to_dict(self):
        """Test converting to dictionary."""
        report = DoctorReport(
            checks=[
                CheckResult("A", CheckStatus.PASS, "OK"),
            ]
        )

        d = report.to_dict()

        assert "checks" in d
        assert "summary" in d
        assert d["summary"]["passed"] == 1


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_to_dict_without_fix_hint(self):
        """Test converting to dict without fix hint."""
        result = CheckResult("Test", CheckStatus.PASS, "OK")

        d = result.to_dict()

        assert d["name"] == "Test"
        assert d["status"] == "pass"
        assert "fix_hint" not in d

    def test_to_dict_with_fix_hint(self):
        """Test converting to dict with fix hint."""
        result = CheckResult("Test", CheckStatus.FAIL, "Failed", "Run: ldf init")

        d = result.to_dict()

        assert d["fix_hint"] == "Run: ldf init"


class TestPrintReport:
    """Tests for print_report function."""

    def test_prints_report(self, capsys):
        """Test printing a doctor report."""
        report = DoctorReport(
            checks=[
                CheckResult("A", CheckStatus.PASS, "OK"),
                CheckResult("B", CheckStatus.WARN, "Warning"),
                CheckResult("C", CheckStatus.FAIL, "Failed", "Fix it"),
            ]
        )

        print_report(report)

        captured = capsys.readouterr()
        assert "LDF Doctor" in captured.out
        assert "OK" in captured.out
        assert "Warning" in captured.out
        assert "Failed" in captured.out
        assert "Fix it" in captured.out
