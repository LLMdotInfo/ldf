"""Tests for ldf.init module."""

import pytest
from pathlib import Path

from ldf.init import (
    initialize_project,
    _create_directories,
    _create_config,
    _create_guardrails,
    _copy_question_packs,
    _create_claude_md,
    _print_summary,
    _prompt_preset,
    _prompt_question_packs,
    _prompt_mcp_servers,
    FRAMEWORK_DIR,
    DEFAULT_QUESTION_PACKS,
    DOMAIN_QUESTION_PACKS,
    PRESETS,
)


class TestConstants:
    """Test module constants."""

    def test_framework_dir_exists(self):
        """Test that the framework directory exists."""
        assert FRAMEWORK_DIR.exists()

    def test_default_question_packs(self):
        """Test default question packs are defined."""
        assert len(DEFAULT_QUESTION_PACKS) > 0
        assert "security" in DEFAULT_QUESTION_PACKS
        assert "testing" in DEFAULT_QUESTION_PACKS

    def test_presets_defined(self):
        """Test presets are defined."""
        assert "saas" in PRESETS
        assert "fintech" in PRESETS
        assert "custom" in PRESETS


class TestCreateDirectories:
    """Tests for _create_directories function."""

    def test_creates_all_directories(self, tmp_path: Path):
        """Test that all directories are created."""
        ldf_dir = tmp_path / ".ldf"
        _create_directories(ldf_dir)

        assert ldf_dir.exists()
        assert (ldf_dir / "specs").exists()
        assert (ldf_dir / "question-packs").exists()
        assert (ldf_dir / "answerpacks").exists()
        assert (ldf_dir / "templates").exists()
        assert (ldf_dir / "audit-history").exists()

    def test_idempotent(self, tmp_path: Path):
        """Test creating directories twice is safe."""
        ldf_dir = tmp_path / ".ldf"
        _create_directories(ldf_dir)
        _create_directories(ldf_dir)

        assert ldf_dir.exists()


class TestCreateConfig:
    """Tests for _create_config function."""

    def test_creates_config_file(self, tmp_path: Path):
        """Test that config file is created."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        _create_config(ldf_dir, "saas", ["security"], ["spec-inspector"])

        config_path = ldf_dir / "config.yaml"
        assert config_path.exists()

    def test_config_contains_preset(self, tmp_path: Path):
        """Test that config contains the preset."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        _create_config(ldf_dir, "fintech", ["security"], ["spec-inspector"])

        config_path = ldf_dir / "config.yaml"
        content = config_path.read_text()
        assert "fintech" in content

    def test_config_contains_question_packs(self, tmp_path: Path):
        """Test that config contains question packs."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        _create_config(ldf_dir, "custom", ["security", "testing"], [])

        config_path = ldf_dir / "config.yaml"
        content = config_path.read_text()
        assert "security" in content
        assert "testing" in content


class TestCreateGuardrails:
    """Tests for _create_guardrails function."""

    def test_creates_guardrails_file(self, tmp_path: Path):
        """Test that guardrails file is created."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        _create_guardrails(ldf_dir, "custom")

        guardrails_path = ldf_dir / "guardrails.yaml"
        assert guardrails_path.exists()

    def test_guardrails_extends_core(self, tmp_path: Path):
        """Test that guardrails extends core."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        _create_guardrails(ldf_dir, "custom")

        guardrails_path = ldf_dir / "guardrails.yaml"
        content = guardrails_path.read_text()
        assert "extends: core" in content

    def test_guardrails_with_preset(self, tmp_path: Path):
        """Test guardrails with a preset."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        _create_guardrails(ldf_dir, "saas")

        guardrails_path = ldf_dir / "guardrails.yaml"
        content = guardrails_path.read_text()
        assert "saas" in content


class TestInitializeProject:
    """Tests for initialize_project function."""

    def test_non_interactive_creates_all_files(self, tmp_path: Path, monkeypatch):
        """Test non-interactive init creates all files."""
        monkeypatch.chdir(tmp_path)

        initialize_project("custom", [], [], non_interactive=True)

        assert (tmp_path / ".ldf").exists()
        assert (tmp_path / ".ldf" / "config.yaml").exists()
        assert (tmp_path / ".ldf" / "guardrails.yaml").exists()
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / ".claude" / "commands").exists()

    def test_creates_claude_commands(self, tmp_path: Path, monkeypatch):
        """Test that Claude commands are created."""
        monkeypatch.chdir(tmp_path)

        initialize_project("custom", [], [], non_interactive=True)

        commands_dir = tmp_path / ".claude" / "commands"
        assert (commands_dir / "create-spec.md").exists()
        assert (commands_dir / "implement-task.md").exists()
        assert (commands_dir / "review-spec.md").exists()

    def test_custom_preset_uses_defaults(self, tmp_path: Path, monkeypatch):
        """Test that custom preset uses default question packs."""
        monkeypatch.chdir(tmp_path)

        initialize_project("custom", [], [], non_interactive=True)

        config_path = tmp_path / ".ldf" / "config.yaml"
        content = config_path.read_text()
        # Should have default question packs when none specified
        assert "security" in content

    def test_overwrite_confirmation_aborted(self, tmp_path: Path, monkeypatch, capsys):
        """Test that overwrite confirmation can abort."""
        monkeypatch.chdir(tmp_path)

        # Create existing .ldf directory
        (tmp_path / ".ldf").mkdir()

        # Mock Confirm.ask to return False
        monkeypatch.setattr("ldf.init.Confirm.ask", lambda *a, **kw: False)

        initialize_project("custom", [], [], non_interactive=False)

        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    def test_overwrite_confirmation_accepted(self, tmp_path: Path, monkeypatch):
        """Test that overwrite confirmation can continue."""
        monkeypatch.chdir(tmp_path)

        # Create existing .ldf directory
        (tmp_path / ".ldf").mkdir()

        # Mock Confirm.ask to return True for overwrite, then defaults for others
        monkeypatch.setattr("ldf.init.Confirm.ask", lambda *a, **kw: True)
        monkeypatch.setattr("ldf.init.Prompt.ask", lambda *a, **kw: "custom")

        initialize_project("custom", [], [], non_interactive=False)

        assert (tmp_path / ".ldf" / "config.yaml").exists()

    def test_with_hooks_installation(self, tmp_path: Path, monkeypatch):
        """Test initialization with hooks installation."""
        monkeypatch.chdir(tmp_path)

        # Create git repo
        (tmp_path / ".git").mkdir()

        initialize_project("custom", [], [], non_interactive=True, install_hooks=True)

        assert (tmp_path / ".ldf").exists()
        assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()


class TestPromptPreset:
    """Tests for _prompt_preset function."""

    def test_prompt_preset_returns_current_if_not_custom(self):
        """Test that non-custom preset is returned as-is."""
        result = _prompt_preset("saas")
        assert result == "saas"

    def test_prompt_preset_interactive_custom(self, monkeypatch, capsys):
        """Test interactive preset selection."""
        monkeypatch.setattr("ldf.init.Prompt.ask", lambda *a, **kw: "fintech")

        result = _prompt_preset("custom")

        assert result == "fintech"
        captured = capsys.readouterr()
        assert "guardrail preset" in captured.out

    def test_prompt_preset_interactive_empty(self, monkeypatch, capsys):
        """Test interactive preset selection with empty current."""
        monkeypatch.setattr("ldf.init.Prompt.ask", lambda *a, **kw: "saas")

        result = _prompt_preset("")

        assert result == "saas"


class TestPromptQuestionPacks:
    """Tests for _prompt_question_packs function."""

    def test_prompt_packs_returns_current_if_set(self):
        """Test that current packs are returned as-is."""
        result = _prompt_question_packs(["security", "testing"])
        assert result == ["security", "testing"]

    def test_prompt_packs_include_core(self, monkeypatch, capsys):
        """Test including all core packs."""
        # Return True for "Include all core packs?" and False for all domain packs
        monkeypatch.setattr("ldf.init.Confirm.ask", lambda *a, **kw: "core" in a[0] if a else False)

        result = _prompt_question_packs([])

        # Should have all default packs
        for pack in DEFAULT_QUESTION_PACKS:
            assert pack in result
        captured = capsys.readouterr()
        assert "question packs" in captured.out

    def test_prompt_packs_exclude_core_include_domain(self, monkeypatch):
        """Test excluding core but including a domain pack."""
        call_count = [0]

        def mock_confirm(*args, **kwargs):
            call_count[0] += 1
            # First call is for core packs - return False
            if call_count[0] == 1:
                return False
            # Return True for first domain pack
            if call_count[0] == 2:
                return True
            return False

        monkeypatch.setattr("ldf.init.Confirm.ask", mock_confirm)

        result = _prompt_question_packs([])

        # Should have just the first domain pack
        assert DOMAIN_QUESTION_PACKS[0] in result
        assert "security" not in result  # Core pack should not be included


class TestPromptMcpServers:
    """Tests for _prompt_mcp_servers function."""

    def test_prompt_servers_returns_current_if_set(self):
        """Test that current servers are returned as-is."""
        result = _prompt_mcp_servers(["spec-inspector"])
        assert result == ["spec-inspector"]

    def test_prompt_servers_include_all(self, monkeypatch, capsys):
        """Test including all servers."""
        monkeypatch.setattr("ldf.init.Confirm.ask", lambda *a, **kw: True)

        result = _prompt_mcp_servers([])

        assert "spec-inspector" in result
        assert "coverage-reporter" in result
        captured = capsys.readouterr()
        assert "MCP servers" in captured.out

    def test_prompt_servers_exclude_all(self, monkeypatch):
        """Test excluding all servers."""
        monkeypatch.setattr("ldf.init.Confirm.ask", lambda *a, **kw: False)

        result = _prompt_mcp_servers([])

        assert result == []


class TestCopyQuestionPacks:
    """Tests for _copy_question_packs function."""

    def test_creates_placeholder_for_missing_pack(self, tmp_path: Path, capsys):
        """Test that missing domain packs get a placeholder."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "question-packs").mkdir()

        _copy_question_packs(ldf_dir, ["nonexistent-pack"])

        placeholder = ldf_dir / "question-packs" / "nonexistent-pack.yaml"
        assert placeholder.exists()
        content = placeholder.read_text()
        assert "TODO:" in content


class TestCreateClaudeMd:
    """Tests for _create_claude_md function."""

    def test_backup_existing_non_ldf_claude_md(self, tmp_path: Path, capsys):
        """Test that existing non-LDF CLAUDE.md is backed up."""
        # Create existing CLAUDE.md without LDF markers
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# My Custom Project Instructions\n\nThis is custom content.")

        _create_claude_md(tmp_path, "custom", ["security"])

        # Should have backed up the original
        backup = tmp_path / "CLAUDE.md.backup"
        assert backup.exists()
        assert "My Custom Project Instructions" in backup.read_text()

        captured = capsys.readouterr()
        assert "Backed up existing CLAUDE.md" in captured.out

    def test_no_backup_for_ldf_claude_md(self, tmp_path: Path, capsys):
        """Test that existing LDF CLAUDE.md is not backed up."""
        # Create existing CLAUDE.md with LDF marker
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# Project\n**Framework:** LDF\n")

        _create_claude_md(tmp_path, "custom", ["security"])

        # Should NOT have created a backup
        backup = tmp_path / "CLAUDE.md.backup"
        assert not backup.exists()

    def test_fintech_preset_coverage_threshold(self, tmp_path: Path):
        """Test that fintech preset uses 90% coverage threshold."""
        _create_claude_md(tmp_path, "fintech", ["security"])

        content = (tmp_path / "CLAUDE.md").read_text()
        assert "90%" in content

    def test_default_preset_coverage_threshold(self, tmp_path: Path):
        """Test that default preset uses 80% coverage threshold."""
        _create_claude_md(tmp_path, "custom", ["security"])

        content = (tmp_path / "CLAUDE.md").read_text()
        assert "80%" in content


class TestPrintSummary:
    """Tests for _print_summary function."""

    def test_summary_without_hooks(self, tmp_path: Path, capsys):
        """Test summary output without hooks installed."""
        _print_summary(tmp_path, "custom", ["security"], ["spec-inspector"], hooks_installed=False)

        captured = capsys.readouterr()
        assert "LDF initialized successfully" in captured.out
        assert "ldf hooks install" in captured.out  # Suggests installing hooks
        assert "Pre-commit hooks: installed" not in captured.out

    def test_summary_with_hooks(self, tmp_path: Path, capsys):
        """Test summary output with hooks installed."""
        _print_summary(tmp_path, "custom", ["security"], ["spec-inspector"], hooks_installed=True)

        captured = capsys.readouterr()
        assert "LDF initialized successfully" in captured.out
        assert "Pre-commit hooks:" in captured.out
        assert "installed" in captured.out
        assert ".git/hooks/pre-commit" in captured.out


class TestInitializeProjectInteractive:
    """Tests for initialize_project with interactive prompts."""

    def test_interactive_uses_prompts(self, tmp_path: Path, monkeypatch, capsys):
        """Test that interactive mode calls prompt functions."""
        monkeypatch.chdir(tmp_path)

        # Mock all prompts
        monkeypatch.setattr("ldf.init.Confirm.ask", lambda *a, **kw: True)
        monkeypatch.setattr("ldf.init.Prompt.ask", lambda *a, **kw: "custom")

        initialize_project("custom", [], [], non_interactive=False)

        captured = capsys.readouterr()
        # Should show interactive prompts
        assert "guardrail preset" in captured.out or "MCP servers" in captured.out or "question packs" in captured.out
