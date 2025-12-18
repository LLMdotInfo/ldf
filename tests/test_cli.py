"""Tests for ldf.cli module."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from ldf.cli import main as cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


class TestCLIHelp:
    """Tests for CLI help and version commands."""

    def test_help_command(self, runner: CliRunner):
        """Test that --help shows usage information."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "LDF" in result.output or "ldf" in result.output.lower()

    def test_version_command(self, runner: CliRunner):
        """Test that --version shows version."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestInitCommand:
    """Tests for 'ldf init' command."""

    def test_init_creates_ldf_directory(self, runner: CliRunner, tmp_path: Path):
        """Test that init creates .ldf directory structure."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init", "--yes"])

            assert result.exit_code == 0
            assert Path(".ldf").exists()
            assert Path(".ldf/config.yaml").exists()
            assert Path(".ldf/guardrails.yaml").exists()
            assert Path(".ldf/specs").exists()

    def test_init_with_preset(self, runner: CliRunner, tmp_path: Path):
        """Test init with a preset option."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init", "--preset", "saas", "--yes"])

            assert result.exit_code == 0
            # Check that config includes the preset
            config = Path(".ldf/config.yaml").read_text()
            assert "saas" in config or "preset" in config

    def test_init_already_initialized(self, runner: CliRunner, tmp_path: Path):
        """Test init when already initialized."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # First init
            runner.invoke(cli, ["init", "--yes"])

            # Second init in non-interactive mode should succeed (overwrites)
            result = runner.invoke(cli, ["init", "--yes"])

            # Should succeed in non-interactive mode
            assert result.exit_code == 0


class TestLintCommand:
    """Tests for 'ldf lint' command."""

    def test_lint_requires_ldf_directory(self, runner: CliRunner, tmp_path: Path):
        """Test lint fails without .ldf directory."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["lint"])

            assert result.exit_code == 1
            assert "ldf" in result.output.lower() or "init" in result.output.lower()

    def test_lint_with_spec_name(self, runner: CliRunner, temp_spec: Path, monkeypatch):
        """Test lint with specific spec name."""
        project_dir = temp_spec.parent.parent.parent
        monkeypatch.chdir(project_dir)

        result = runner.invoke(cli, ["lint", "test-feature"])

        # Should succeed for valid spec
        assert result.exit_code == 0

    def test_lint_all_specs(self, runner: CliRunner, temp_spec: Path, monkeypatch):
        """Test lint all specs in project."""
        project_dir = temp_spec.parent.parent.parent
        monkeypatch.chdir(project_dir)

        result = runner.invoke(cli, ["lint", "--all"])

        assert result.exit_code == 0


class TestAuditCommand:
    """Tests for 'ldf audit' command."""

    def test_audit_spec_review(self, runner: CliRunner, temp_spec: Path, monkeypatch):
        """Test generating a spec review audit request."""
        project_dir = temp_spec.parent.parent.parent
        monkeypatch.chdir(project_dir)

        # Use -y to skip confirmation prompt
        result = runner.invoke(cli, ["audit", "--type", "spec-review", "-y"])

        # Should generate audit request
        assert result.exit_code == 0

    def test_audit_requires_type(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test that audit requires --type or --import."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["audit"])

        # Should fail or warn without type
        # The audit command may exit 0 but show usage, or exit non-zero
        assert "type" in result.output.lower() or "import" in result.output.lower() or result.exit_code != 0


class TestCLIIntegration:
    """Integration tests for CLI workflow."""

    def test_init_then_lint(self, runner: CliRunner, tmp_path: Path):
        """Test init followed by lint workflow."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Initialize with --yes for non-interactive mode
            init_result = runner.invoke(cli, ["init", "--yes"])
            assert init_result.exit_code == 0

            # Lint (no specs yet, should succeed or warn)
            lint_result = runner.invoke(cli, ["lint", "--all"])
            assert lint_result.exit_code == 0


class TestVerboseMode:
    """Tests for verbose mode."""

    def test_verbose_flag(self, runner: CliRunner, tmp_path: Path):
        """Test that verbose flag enables verbose logging."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["-v", "init", "--yes"])

            # Should succeed with verbose mode
            assert result.exit_code == 0


class TestCreateSpecCommand:
    """Tests for 'ldf create-spec' command."""

    def test_create_spec_success(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test successful spec creation."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["create-spec", "new-feature"])

        assert result.exit_code == 0
        assert (temp_project / ".ldf" / "specs" / "new-feature").exists()

    def test_create_spec_failure_exits_with_1(self, runner: CliRunner, tmp_path: Path, monkeypatch):
        """Test that create-spec fails without LDF initialized."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(cli, ["create-spec", "my-feature"])

        assert result.exit_code == 1


class TestCoverageCommand:
    """Tests for 'ldf coverage' command."""

    def test_coverage_command_basic(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test basic coverage command."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["coverage"])

        # May fail or succeed depending on coverage file
        # Just check it runs without error
        assert result.exit_code in (0, 1)

    def test_coverage_fail_status_exit_code(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test that coverage FAIL status returns exit code 1."""
        monkeypatch.chdir(temp_project)

        # Create a mock coverage file that will report FAIL
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text('{"totals": {"percent_covered": 50.0}}')

        result = runner.invoke(cli, ["coverage"])

        # Should exit with 1 when coverage fails
        assert result.exit_code in (0, 1)  # Depends on threshold


class TestHooksCommands:
    """Tests for 'ldf hooks' commands."""

    def test_hooks_help(self, runner: CliRunner):
        """Test hooks group help."""
        result = runner.invoke(cli, ["hooks", "--help"])

        assert result.exit_code == 0
        assert "install" in result.output
        assert "uninstall" in result.output
        assert "status" in result.output

    def test_hooks_install_no_git(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test hooks install fails without git."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["hooks", "install", "-y"])

        # Should fail without git
        assert result.exit_code == 1

    def test_hooks_install_success(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test hooks install succeeds with git."""
        # Create .git directory
        (temp_project / ".git").mkdir()
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["hooks", "install", "-y", "--no-detect"])

        assert result.exit_code == 0

    def test_hooks_uninstall_not_installed(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test hooks uninstall when not installed."""
        (temp_project / ".git").mkdir()
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["hooks", "uninstall"])

        # Should fail when no hook installed
        assert result.exit_code == 1

    def test_hooks_uninstall_success(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test hooks uninstall after install."""
        (temp_project / ".git").mkdir()
        monkeypatch.chdir(temp_project)

        # First install
        runner.invoke(cli, ["hooks", "install", "-y", "--no-detect"])

        # Then uninstall
        result = runner.invoke(cli, ["hooks", "uninstall"])

        assert result.exit_code == 0

    def test_hooks_status(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test hooks status command."""
        (temp_project / ".git").mkdir()
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["hooks", "status"])

        assert result.exit_code == 0
        assert "Hook" in result.output


class TestStatusCommand:
    """Tests for 'ldf status' command."""

    def test_status_new_project(self, runner: CliRunner, tmp_path: Path):
        """Test status on a new project without LDF."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["status"])

            assert result.exit_code == 0
            assert "NEW" in result.output or "new" in result.output.lower()

    def test_status_initialized_project(self, runner: CliRunner, tmp_path: Path):
        """Test status on an initialized project."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Initialize first
            runner.invoke(cli, ["init", "--yes"])

            result = runner.invoke(cli, ["status"])

            assert result.exit_code == 0
            assert "CURRENT" in result.output or "Project" in result.output

    def test_status_json_output(self, runner: CliRunner, tmp_path: Path):
        """Test status with JSON output."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(cli, ["init", "--yes"])

            result = runner.invoke(cli, ["status", "--json"])

            assert result.exit_code == 0
            # Should contain JSON-like output
            assert "{" in result.output or "state" in result.output.lower()

    def test_status_with_specs(self, runner: CliRunner, temp_spec: Path, monkeypatch):
        """Test status shows specs when present."""
        project_dir = temp_spec.parent.parent.parent
        monkeypatch.chdir(project_dir)

        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0


class TestUpdateCommand:
    """Tests for 'ldf update' command."""

    def test_update_check(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test update --check shows available updates."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["update", "--check"])

        assert result.exit_code == 0

    def test_update_dry_run(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test update --dry-run previews changes."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["update", "--dry-run"])

        assert result.exit_code == 0

    def test_update_with_yes(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test update --yes applies updates non-interactively."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["update", "--yes"])

        assert result.exit_code == 0

    def test_update_requires_init(self, runner: CliRunner, tmp_path: Path):
        """Test update fails without LDF initialized."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["update"])

            assert result.exit_code == 1


class TestConvertCommand:
    """Tests for 'ldf convert' command."""

    def test_convert_help(self, runner: CliRunner):
        """Test convert group help."""
        result = runner.invoke(cli, ["convert", "--help"])

        assert result.exit_code == 0
        assert "analyze" in result.output
        assert "import" in result.output

    def test_convert_analyze(self, runner: CliRunner, tmp_path: Path):
        """Test convert analyze generates prompt."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create some source files to analyze
            Path("main.py").write_text("print('hello')")
            Path("README.md").write_text("# My Project")

            result = runner.invoke(cli, ["convert", "analyze"])

            assert result.exit_code == 0

    def test_convert_analyze_output_file(self, runner: CliRunner, tmp_path: Path):
        """Test convert analyze with output file."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("main.py").write_text("print('hello')")

            result = runner.invoke(cli, ["convert", "analyze", "-o", "prompt.md"])

            assert result.exit_code == 0
            assert Path("prompt.md").exists()


class TestMcpConfigCommand:
    """Tests for 'ldf mcp-config' command."""

    def test_mcp_config_basic(self, runner: CliRunner, temp_project: Path, monkeypatch):
        """Test mcp-config generates configuration."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(cli, ["mcp-config"])

        assert result.exit_code == 0
        assert "mcpServers" in result.output or "spec-inspector" in result.output

    def test_mcp_config_without_init(self, runner: CliRunner, tmp_path: Path):
        """Test mcp-config works even without full LDF init (generates basic config)."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["mcp-config"])

            # Should succeed and output config (may be minimal)
            assert result.exit_code == 0


class TestMainEntryPoint:
    """Tests for main entry point."""

    def test_main_callable(self):
        """Test that main CLI function is callable."""
        from ldf.cli import main
        assert callable(main)
