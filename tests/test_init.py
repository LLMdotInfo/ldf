"""Tests for ldf.init module."""

from pathlib import Path

from ldf.init import (
    FRAMEWORK_DIR,
    _copy_question_packs,
    _create_claude_md,
    _create_config,
    _create_directories,
    _create_guardrails,
    _print_summary,
    initialize_project,
)
from ldf.utils.descriptions import (
    get_core_packs,
    get_domain_packs,
    get_preset_recommended_packs,
)


class TestFrameworkDir:
    """Test framework directory."""

    def test_framework_dir_exists(self):
        """Test that the framework directory exists."""
        assert FRAMEWORK_DIR.exists()


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

        initialize_project(
            project_path=tmp_path,
            preset="custom",
            question_packs=[],
            mcp_servers=[],
            non_interactive=True,
        )

        assert (tmp_path / ".ldf").exists()
        assert (tmp_path / ".ldf" / "config.yaml").exists()
        assert (tmp_path / ".ldf" / "guardrails.yaml").exists()
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / ".claude" / "commands").exists()

    def test_creates_claude_commands(self, tmp_path: Path, monkeypatch):
        """Test that Claude commands are created."""
        monkeypatch.chdir(tmp_path)

        initialize_project(
            project_path=tmp_path,
            preset="custom",
            question_packs=[],
            mcp_servers=[],
            non_interactive=True,
        )

        commands_dir = tmp_path / ".claude" / "commands"
        assert (commands_dir / "create-spec.md").exists()
        assert (commands_dir / "implement-task.md").exists()
        assert (commands_dir / "review-spec.md").exists()

    def test_custom_preset_uses_defaults(self, tmp_path: Path, monkeypatch):
        """Test that custom preset uses default question packs."""
        monkeypatch.chdir(tmp_path)

        initialize_project(
            project_path=tmp_path,
            preset="custom",
            question_packs=None,
            mcp_servers=None,
            non_interactive=True,
        )

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

        initialize_project(
            project_path=tmp_path,
            preset="custom",
            question_packs=[],
            mcp_servers=[],
            non_interactive=False,
        )

        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    def test_overwrite_confirmation_accepted(self, tmp_path: Path, monkeypatch):
        """Test that overwrite confirmation can continue."""
        monkeypatch.chdir(tmp_path)

        # Create existing .ldf directory
        (tmp_path / ".ldf").mkdir()

        # Mock Confirm.ask to return True for overwrite
        monkeypatch.setattr("ldf.init.Confirm.ask", lambda *a, **kw: True)

        # Mock prompts module functions to avoid interactive prompts
        monkeypatch.setattr("ldf.init.prompt_preset", lambda: "custom")
        monkeypatch.setattr("ldf.init.prompt_question_packs", lambda preset: ["security"])
        monkeypatch.setattr("ldf.init.prompt_mcp_servers", lambda: ["spec-inspector"])
        monkeypatch.setattr("ldf.init.prompt_install_hooks", lambda: False)
        monkeypatch.setattr("ldf.init.confirm_initialization", lambda *a, **kw: True)

        initialize_project(
            project_path=tmp_path,
            preset=None,
            question_packs=None,
            mcp_servers=None,
            non_interactive=False,
        )

        assert (tmp_path / ".ldf" / "config.yaml").exists()

    def test_with_hooks_installation(self, tmp_path: Path, monkeypatch):
        """Test initialization with hooks installation."""
        monkeypatch.chdir(tmp_path)

        # Create git repo
        (tmp_path / ".git").mkdir()

        initialize_project(
            project_path=tmp_path,
            preset="custom",
            question_packs=[],
            mcp_servers=[],
            non_interactive=True,
            install_hooks=True,
        )

        assert (tmp_path / ".ldf").exists()
        assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()

    def test_creates_project_directory_if_not_exists(self, tmp_path: Path, monkeypatch):
        """Test that project directory is created if it doesn't exist."""
        new_project = tmp_path / "new-project"

        initialize_project(
            project_path=new_project,
            preset="custom",
            question_packs=[],
            mcp_servers=[],
            non_interactive=True,
        )

        assert new_project.exists()
        assert (new_project / ".ldf").exists()


class TestDescriptionsIntegration:
    """Tests for descriptions module integration with init."""

    def test_core_packs_defined(self):
        """Test that core packs are defined in descriptions."""
        core_packs = get_core_packs()
        assert len(core_packs) > 0
        assert "security" in core_packs
        assert "testing" in core_packs

    def test_domain_packs_defined(self):
        """Test that domain packs are defined in descriptions."""
        domain_packs = get_domain_packs()
        assert len(domain_packs) > 0
        assert "billing" in domain_packs
        assert "multi-tenancy" in domain_packs

    def test_preset_recommendations_exist(self):
        """Test that preset recommendations are defined."""
        saas_packs = get_preset_recommended_packs("saas")
        assert len(saas_packs) > 0
        # SaaS should recommend multi-tenancy
        assert "multi-tenancy" in saas_packs


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

        # Track which prompts were called
        prompts_called = []

        def mock_prompt_preset():
            prompts_called.append("preset")
            return "custom"

        def mock_prompt_question_packs(preset):
            prompts_called.append("question_packs")
            return ["security"]

        def mock_prompt_mcp_servers():
            prompts_called.append("mcp_servers")
            return ["spec-inspector"]

        def mock_prompt_install_hooks():
            prompts_called.append("install_hooks")
            return False

        def mock_confirm_initialization(*args, **kwargs):
            prompts_called.append("confirm")
            return True

        # Mock all prompts
        monkeypatch.setattr("ldf.init.prompt_preset", mock_prompt_preset)
        monkeypatch.setattr("ldf.init.prompt_question_packs", mock_prompt_question_packs)
        monkeypatch.setattr("ldf.init.prompt_mcp_servers", mock_prompt_mcp_servers)
        monkeypatch.setattr("ldf.init.prompt_install_hooks", mock_prompt_install_hooks)
        monkeypatch.setattr("ldf.init.confirm_initialization", mock_confirm_initialization)

        initialize_project(
            project_path=tmp_path,
            preset=None,
            question_packs=None,
            mcp_servers=None,
            non_interactive=False,
        )

        # Should have called all prompt functions
        assert "preset" in prompts_called
        assert "question_packs" in prompts_called
        assert "mcp_servers" in prompts_called
        assert "confirm" in prompts_called
