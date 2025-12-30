"""Tests for ldf.workspace.commands module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

from ldf.workspace.commands import (
    _create_shared_structure,
    _discover_ldf_projects,
    _generate_dot_graph,
    _generate_mermaid_graph,
    workspace,
)


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def workspace_dir(tmp_path):
    """Create a basic workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def initialized_workspace(workspace_dir):
    """Create an initialized workspace with manifest."""
    manifest = workspace_dir / "ldf-workspace.yaml"
    manifest.write_text("""
version: "1.0"
name: test-workspace
projects:
  explicit: []
  discovery:
    patterns: ["**/.ldf/config.yaml"]
    exclude: ["node_modules", ".venv"]
shared:
  path: .ldf-shared/
  inherit:
    guardrails: true
    templates: true
""")
    return workspace_dir


class TestWorkspaceGroup:
    """Tests for workspace command group."""

    def test_help_message(self, runner):
        """Test workspace --help shows help."""
        result = runner.invoke(workspace, ["--help"])
        assert result.exit_code == 0
        assert "Manage multi-project workspaces" in result.output


class TestWorkspaceInit:
    """Tests for 'ldf workspace init' command."""

    def test_basic_init(self, runner, tmp_path):
        """Test basic workspace initialization."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["init"])
            assert result.exit_code == 0
            assert "Created ldf-workspace.yaml" in result.output

            # Check manifest was created
            manifest_path = Path("ldf-workspace.yaml")
            assert manifest_path.exists()

            # Check content
            with open(manifest_path) as f:
                data = yaml.safe_load(f)
            assert "version" in data
            assert "projects" in data
            assert "shared" in data

    def test_init_with_custom_name(self, runner, tmp_path):
        """Test init with custom workspace name."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["init", "--name", "my-platform"])
            assert result.exit_code == 0

            with open("ldf-workspace.yaml") as f:
                data = yaml.safe_load(f)
            assert data["name"] == "my-platform"

    def test_init_creates_shared_dir(self, runner, tmp_path):
        """Test init creates .ldf-shared directory structure."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["init"])
            assert result.exit_code == 0

            assert Path(".ldf-shared").is_dir()
            assert Path(".ldf-shared/guardrails").is_dir()
            assert Path(".ldf-shared/templates").is_dir()
            assert Path(".ldf-shared/question-packs").is_dir()
            assert Path(".ldf-shared/macros").is_dir()
            assert Path(".ldf-shared/README.md").exists()

    def test_init_creates_workspace_state_dir(self, runner, tmp_path):
        """Test init creates .ldf-workspace directory."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["init"])
            assert result.exit_code == 0

            assert Path(".ldf-workspace").is_dir()
            assert Path(".ldf-workspace/.gitignore").exists()

    def test_init_fails_if_exists(self, runner, tmp_path):
        """Test init fails if workspace already exists."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # First init
            runner.invoke(workspace, ["init"])

            # Second init should fail
            result = runner.invoke(workspace, ["init"])
            assert result.exit_code == 1
            assert "already exists" in result.output

    def test_init_force_overwrites(self, runner, tmp_path):
        """Test init --force overwrites existing workspace."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # First init
            runner.invoke(workspace, ["init", "--name", "old-name"])

            # Second init with force
            result = runner.invoke(workspace, ["init", "--force", "--name", "new-name"])
            assert result.exit_code == 0

            with open("ldf-workspace.yaml") as f:
                data = yaml.safe_load(f)
            assert data["name"] == "new-name"

    def test_init_with_discover(self, runner, tmp_path):
        """Test init --discover finds existing projects."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create an existing LDF project
            project = Path("services/auth/.ldf")
            project.mkdir(parents=True)
            (project / "config.yaml").write_text("_schema_version: '1.1'")

            result = runner.invoke(workspace, ["init", "--discover"])
            assert result.exit_code == 0
            assert "Found 1 LDF project" in result.output
            assert "auth" in result.output

            # Check it was added to manifest
            with open("ldf-workspace.yaml") as f:
                data = yaml.safe_load(f)
            assert len(data["projects"]["explicit"]) == 1
            assert data["projects"]["explicit"][0]["alias"] == "auth"


class TestWorkspaceList:
    """Tests for 'ldf workspace list' command."""

    def test_list_not_in_workspace(self, runner, tmp_path):
        """Test list fails when not in a workspace."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["list"])
            assert result.exit_code == 1
            assert "Not in a workspace" in result.output

    @patch("ldf.detection.detect_workspace_state")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_list_json_format(self, mock_find, mock_detect, runner, tmp_path):
        """Test list with JSON format."""
        mock_find.return_value = tmp_path
        mock_detect.return_value = {
            "status": "ok",
            "name": "test-workspace",
            "projects": [
                {"alias": "auth", "path": "services/auth", "state": "current", "version": "1.0.0"}
            ],
            "shared": {"exists": False},
        }

        result = runner.invoke(workspace, ["list", "--format", "json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["name"] == "test-workspace"
        assert len(data["projects"]) == 1

    @patch("ldf.detection.detect_workspace_state")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_list_text_format(self, mock_find, mock_detect, runner, tmp_path):
        """Test list with text format."""
        mock_find.return_value = tmp_path
        mock_detect.return_value = {
            "status": "ok",
            "name": "test-workspace",
            "projects": [
                {"alias": "auth", "path": "services/auth", "state": "current", "version": "1.0.0"}
            ],
            "shared": {"exists": False},
        }

        result = runner.invoke(workspace, ["list", "--format", "text"])
        assert result.exit_code == 0
        assert "test-workspace" in result.output
        assert "auth" in result.output
        assert "CURRENT" in result.output

    @patch("ldf.detection.detect_workspace_state")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_list_handles_error(self, mock_find, mock_detect, runner, tmp_path):
        """Test list handles detection errors."""
        mock_find.return_value = tmp_path
        mock_detect.return_value = {
            "status": "error",
            "error": "Failed to parse manifest",
        }

        result = runner.invoke(workspace, ["list"])
        assert result.exit_code == 1
        assert "Failed to parse manifest" in result.output


class TestWorkspaceAdd:
    """Tests for 'ldf workspace add' command."""

    def test_add_not_in_workspace(self, runner, tmp_path):
        """Test add fails when not in a workspace."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("project").mkdir()
            result = runner.invoke(workspace, ["add", "project"])
            assert result.exit_code == 1
            assert "Not in a workspace" in result.output

    def test_add_project(self, runner, tmp_path):
        """Test adding a project to workspace."""
        import os

        # Initialize workspace first
        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        # Create a project directory
        project = tmp_path / "services" / "auth"
        project.mkdir(parents=True)

        result = runner.invoke(workspace, ["add", str(project)])
        assert result.exit_code == 0
        assert "Added project 'auth'" in result.output

        # Check manifest was updated
        with open(tmp_path / "ldf-workspace.yaml") as f:
            data = yaml.safe_load(f)
        assert len(data["projects"]["explicit"]) == 1
        assert data["projects"]["explicit"][0]["alias"] == "auth"

    def test_add_with_custom_alias(self, runner, tmp_path):
        """Test adding a project with custom alias."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        project = tmp_path / "services" / "auth"
        project.mkdir(parents=True)

        result = runner.invoke(workspace, ["add", str(project), "--alias", "authentication"])
        assert result.exit_code == 0
        assert "Added project 'authentication'" in result.output

    def test_add_duplicate_alias_fails(self, runner, tmp_path):
        """Test adding project with duplicate alias fails."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        project1 = tmp_path / "services" / "auth1"
        project1.mkdir(parents=True)
        project2 = tmp_path / "services" / "auth2"
        project2.mkdir(parents=True)

        runner.invoke(workspace, ["add", str(project1), "--alias", "auth"])
        result = runner.invoke(workspace, ["add", str(project2), "--alias", "auth"])
        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_add_duplicate_path_skipped(self, runner, tmp_path):
        """Test adding same project path is skipped."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        project = tmp_path / "services" / "auth"
        project.mkdir(parents=True)

        runner.invoke(workspace, ["add", str(project), "--alias", "auth1"])
        # Use different alias to test path duplicate detection (not alias collision)
        result = runner.invoke(workspace, ["add", str(project), "--alias", "auth2"])
        assert result.exit_code == 0
        assert "already in workspace" in result.output

    def test_add_warns_if_no_ldf(self, runner, tmp_path):
        """Test add warns if project doesn't have LDF initialized."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        project = tmp_path / "services" / "auth"
        project.mkdir(parents=True)
        # Don't create .ldf directory

        result = runner.invoke(workspace, ["add", str(project)])
        assert result.exit_code == 0
        assert "doesn't have LDF initialized" in result.output


class TestWorkspaceSync:
    """Tests for 'ldf workspace sync' command."""

    def test_sync_not_in_workspace(self, runner, tmp_path):
        """Test sync fails when not in a workspace."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["sync"])
            assert result.exit_code == 1
            assert "Not in a workspace" in result.output

    @patch("ldf.lint.lint_workspace_references")
    @patch("ldf.detection.detect_workspace_state")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_sync_success(self, mock_find, mock_detect, mock_lint, runner, tmp_path):
        """Test successful sync."""
        mock_find.return_value = tmp_path
        mock_detect.return_value = {
            "status": "ok",
            "name": "test-workspace",
            "projects": [],
        }
        mock_lint.return_value = 0

        # Create state dir for registry
        (tmp_path / ".ldf-workspace").mkdir()

        result = runner.invoke(workspace, ["sync"])
        assert result.exit_code == 0
        assert "Sync complete" in result.output


class TestWorkspaceReport:
    """Tests for 'ldf workspace report' command."""

    def test_report_not_in_workspace(self, runner, tmp_path):
        """Test report fails when not in a workspace."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["report"])
            assert result.exit_code == 1
            assert "Not in a workspace" in result.output


class TestWorkspaceGraph:
    """Tests for 'ldf workspace graph' command."""

    def test_graph_not_in_workspace(self, runner, tmp_path):
        """Test graph fails when not in a workspace."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["graph"])
            assert result.exit_code == 1
            assert "Not in a workspace" in result.output


class TestWorkspaceValidateRefs:
    """Tests for 'ldf workspace validate-refs' command."""

    def test_validate_refs_not_in_workspace(self, runner, tmp_path):
        """Test validate-refs fails when not in a workspace."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(workspace, ["validate-refs"])
            assert result.exit_code == 1
            assert "Not in a workspace" in result.output


class TestDiscoverLdfProjects:
    """Tests for _discover_ldf_projects helper function."""

    def test_discovers_projects(self, tmp_path):
        """Test discovering LDF projects."""
        # Create multiple projects
        for name in ["auth", "billing"]:
            project = tmp_path / "services" / name / ".ldf"
            project.mkdir(parents=True)
            (project / "config.yaml").write_text("")

        projects = _discover_ldf_projects(tmp_path)

        assert len(projects) == 2
        aliases = {p["alias"] for p in projects}
        assert aliases == {"auth", "billing"}

    def test_excludes_node_modules(self, tmp_path):
        """Test excluding node_modules."""
        # Create project in node_modules
        excluded = tmp_path / "node_modules" / "pkg" / ".ldf"
        excluded.mkdir(parents=True)
        (excluded / "config.yaml").write_text("")

        # Create valid project
        valid = tmp_path / "services" / "auth" / ".ldf"
        valid.mkdir(parents=True)
        (valid / "config.yaml").write_text("")

        projects = _discover_ldf_projects(tmp_path)

        assert len(projects) == 1
        assert projects[0]["alias"] == "auth"

    def test_excludes_venv(self, tmp_path):
        """Test excluding .venv."""
        excluded = tmp_path / ".venv" / "lib" / ".ldf"
        excluded.mkdir(parents=True)
        (excluded / "config.yaml").write_text("")

        projects = _discover_ldf_projects(tmp_path)
        assert len(projects) == 0

    def test_excludes_ldf_shared(self, tmp_path):
        """Test excluding .ldf-shared."""
        excluded = tmp_path / ".ldf-shared" / "templates" / ".ldf"
        excluded.mkdir(parents=True)
        (excluded / "config.yaml").write_text("")

        projects = _discover_ldf_projects(tmp_path)
        assert len(projects) == 0

    def test_skips_workspace_root_project(self, tmp_path):
        """Test skipping project at workspace root."""
        root_project = tmp_path / ".ldf"
        root_project.mkdir()
        (root_project / "config.yaml").write_text("")

        projects = _discover_ldf_projects(tmp_path)
        assert len(projects) == 0

    def test_sorts_by_path(self, tmp_path):
        """Test results are sorted by path."""
        for name in ["zebra", "alpha", "middle"]:
            project = tmp_path / "services" / name / ".ldf"
            project.mkdir(parents=True)
            (project / "config.yaml").write_text("")

        projects = _discover_ldf_projects(tmp_path)

        paths = [p["path"] for p in projects]
        assert paths == sorted(paths)


class TestCreateSharedStructure:
    """Tests for _create_shared_structure helper function."""

    def test_creates_directories(self, tmp_path, capsys):
        """Test creating shared directory structure."""
        shared_dir = tmp_path / ".ldf-shared"

        # Suppress console output during test
        with patch("ldf.workspace.commands.console"):
            _create_shared_structure(shared_dir)

        assert shared_dir.is_dir()
        assert (shared_dir / "guardrails").is_dir()
        assert (shared_dir / "templates").is_dir()
        assert (shared_dir / "question-packs").is_dir()
        assert (shared_dir / "macros").is_dir()
        assert (shared_dir / "README.md").exists()

    def test_preserves_existing_readme(self, tmp_path):
        """Test existing README is preserved."""
        shared_dir = tmp_path / ".ldf-shared"
        shared_dir.mkdir()
        readme = shared_dir / "README.md"
        readme.write_text("Custom content")

        with patch("ldf.workspace.commands.console"):
            _create_shared_structure(shared_dir)

        assert readme.read_text() == "Custom content"


class TestGenerateMermaidGraph:
    """Tests for _generate_mermaid_graph helper function."""

    def test_empty_graph(self, tmp_path):
        """Test generating empty graph."""
        result = _generate_mermaid_graph({}, tmp_path)
        assert "graph LR" in result
        assert "No cross-project references" in result

    def test_simple_graph(self, tmp_path):
        """Test generating simple graph."""
        graph_data = {
            "auth": {"billing"},
            "billing": {"api"},
        }
        result = _generate_mermaid_graph(graph_data, tmp_path)

        assert "graph LR" in result
        assert "auth[auth]" in result
        assert "billing[billing]" in result
        assert "api[api]" in result
        assert "auth --> billing" in result
        assert "billing --> api" in result


class TestGenerateDotGraph:
    """Tests for _generate_dot_graph helper function."""

    def test_empty_graph(self, tmp_path):
        """Test generating empty DOT graph."""
        result = _generate_dot_graph({}, tmp_path)
        assert "digraph workspace" in result
        assert "No cross-project references" in result

    def test_simple_graph(self, tmp_path):
        """Test generating simple DOT graph."""
        graph_data = {
            "auth": {"billing"},
        }
        result = _generate_dot_graph(graph_data, tmp_path)

        assert "digraph workspace" in result
        assert '"auth" -> "billing"' in result
        assert "rankdir=LR" in result


class TestWorkspaceListRichOutput:
    """Tests for workspace list with rich output."""

    @patch("ldf.detection.detect_workspace_state")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_list_rich_output_with_projects(self, mock_find, mock_detect, runner, tmp_path):
        """Test rich output shows project table."""
        mock_find.return_value = tmp_path
        mock_detect.return_value = {
            "status": "ok",
            "name": "test-workspace",
            "projects": [
                {"alias": "auth", "path": "services/auth", "state": "current", "version": "1.0.0"},
                {
                    "alias": "billing",
                    "path": "services/billing",
                    "state": "outdated",
                    "version": "0.9.0",
                },
            ],
            "shared": {"exists": False},
        }

        result = runner.invoke(workspace, ["list"])
        assert result.exit_code == 0
        assert "test-workspace" in result.output
        assert "auth" in result.output
        assert "billing" in result.output

    @patch("ldf.detection.detect_workspace_state")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_list_rich_output_with_shared_resources(self, mock_find, mock_detect, runner, tmp_path):
        """Test rich output shows shared resources info."""
        mock_find.return_value = tmp_path
        mock_detect.return_value = {
            "status": "ok",
            "name": "test-workspace",
            "projects": [],
            "shared": {
                "exists": True,
                "path": ".ldf-shared",
                "has_guardrails": True,
                "has_templates": True,
            },
        }

        result = runner.invoke(workspace, ["list"])
        assert result.exit_code == 0
        assert "Shared Resources" in result.output

    @patch("ldf.detection.detect_workspace_state")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_list_shows_all_states(self, mock_find, mock_detect, runner, tmp_path):
        """Test list shows different project states."""
        mock_find.return_value = tmp_path
        mock_detect.return_value = {
            "status": "ok",
            "name": "test-workspace",
            "projects": [
                {"alias": "proj1", "path": "p1", "state": "current", "version": "1.0"},
                {"alias": "proj2", "path": "p2", "state": "outdated", "version": "0.9"},
                {"alias": "proj3", "path": "p3", "state": "legacy", "version": "0.5"},
                {"alias": "proj4", "path": "p4", "state": "corrupted", "version": None},
                {"alias": "proj5", "path": "p5", "state": "missing", "version": None},
            ],
            "shared": {"exists": False},
        }

        result = runner.invoke(workspace, ["list"])
        assert result.exit_code == 0
        # Output should include all projects
        assert "proj1" in result.output


class TestWorkspaceReportFull:
    """Full tests for workspace report command."""

    def test_report_json_output(self, runner, tmp_path):
        """Test report with JSON output."""
        import os

        # Create workspace with a project
        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        project = tmp_path / "services" / "auth"
        ldf_dir = project / ".ldf"
        ldf_dir.mkdir(parents=True)
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\nproject:\n  name: auth")
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir()
        (specs_dir / "login").mkdir()

        runner.invoke(workspace, ["add", str(project)])

        result = runner.invoke(workspace, ["report", "--format", "json"])
        assert result.exit_code == 0

        import json

        data = json.loads(result.output)
        assert "workspace" in data
        assert "summary" in data
        assert "projects" in data

    def test_report_html_output(self, runner, tmp_path):
        """Test report with HTML output."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        result = runner.invoke(workspace, ["report", "--format", "html"])
        assert result.exit_code == 0

        # Check HTML file was created
        html_path = tmp_path / ".ldf-reports" / "workspace-report.html"
        assert html_path.exists()
        html_content = html_path.read_text()
        assert "<html>" in html_content

    def test_report_json_to_file(self, runner, tmp_path):
        """Test report JSON output to file."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        output_file = tmp_path / "report.json"
        result = runner.invoke(
            workspace, ["report", "--format", "json", "--output", str(output_file)]
        )
        assert result.exit_code == 0
        assert output_file.exists()

    def test_report_handles_malformed_registry(self, runner, tmp_path):
        """Test report gracefully handles malformed .registry.yaml."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        # Create a project
        project = tmp_path / "services" / "auth"
        ldf_dir = project / ".ldf"
        ldf_dir.mkdir(parents=True)
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\nproject:\n  name: auth")
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir()

        runner.invoke(workspace, ["add", str(project)])

        # Create malformed registry file (non-dict YAML)
        registry_path = tmp_path / ".ldf-workspace" / ".registry.yaml"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("just a string, not a dict")

        # Report should still work, just skip the coverage data
        result = runner.invoke(workspace, ["report", "--format", "json"])
        assert result.exit_code == 0

        import json

        data = json.loads(result.output)
        assert "projects" in data

    def test_report_handles_empty_registry(self, runner, tmp_path):
        """Test report gracefully handles empty .registry.yaml (None)."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        # Create a project
        project = tmp_path / "services" / "auth"
        ldf_dir = project / ".ldf"
        ldf_dir.mkdir(parents=True)
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\nproject:\n  name: auth")
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir()

        runner.invoke(workspace, ["add", str(project)])

        # Create empty registry file (yaml.safe_load returns None)
        registry_path = tmp_path / ".ldf-workspace" / ".registry.yaml"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("")

        # Report should still work
        result = runner.invoke(workspace, ["report", "--format", "json"])
        assert result.exit_code == 0


class TestWorkspaceGraphFull:
    """Full tests for workspace graph command."""

    def test_graph_mermaid_output(self, runner, tmp_path):
        """Test graph with mermaid output."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        # Create projects with references
        auth = tmp_path / "services" / "auth"
        (auth / ".ldf" / "specs" / "login").mkdir(parents=True)
        (auth / ".ldf" / "config.yaml").write_text("_schema_version: '1.1'")
        (auth / ".ldf" / "specs" / "login" / "requirements.md").write_text(
            "# Login\nDepends on @billing/payment"
        )
        runner.invoke(workspace, ["add", str(auth)])

        billing = tmp_path / "services" / "billing"
        (billing / ".ldf" / "specs" / "payment").mkdir(parents=True)
        (billing / ".ldf" / "config.yaml").write_text("_schema_version: '1.1'")
        runner.invoke(workspace, ["add", str(billing)])

        result = runner.invoke(workspace, ["graph", "--format", "mermaid"])
        assert result.exit_code == 0
        assert "graph LR" in result.output

    def test_graph_dot_output(self, runner, tmp_path):
        """Test graph with DOT output."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        result = runner.invoke(workspace, ["graph", "--format", "dot"])
        assert result.exit_code == 0
        assert "digraph workspace" in result.output

    def test_graph_json_output(self, runner, tmp_path):
        """Test graph with JSON output."""
        import os

        os.chdir(tmp_path)
        runner.invoke(workspace, ["init"])

        result = runner.invoke(workspace, ["graph", "--format", "json"])
        assert result.exit_code == 0

        import json

        data = json.loads(result.output)
        # JSON output is a dict of project -> list of dependencies
        assert isinstance(data, dict)


class TestWorkspaceValidateRefsFull:
    """Full tests for validate-refs command."""

    @patch("ldf.lint.lint_workspace_references")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_validate_refs_success(self, mock_find, mock_lint, runner, tmp_path):
        """Test validate-refs with no errors."""
        mock_find.return_value = tmp_path
        mock_lint.return_value = 0

        # Create manifest
        (tmp_path / "ldf-workspace.yaml").write_text("""
version: "1.0"
name: test
projects:
  explicit: []
""")

        result = runner.invoke(workspace, ["validate-refs"])
        assert result.exit_code == 0

    @patch("ldf.lint.lint_workspace_references")
    @patch("ldf.workspace.commands.find_workspace_root")
    def test_validate_refs_with_errors(self, mock_find, mock_lint, runner, tmp_path):
        """Test validate-refs with errors returns non-zero (exit code = error count)."""
        mock_find.return_value = tmp_path
        mock_lint.return_value = 3  # 3 errors

        (tmp_path / "ldf-workspace.yaml").write_text("""
version: "1.0"
name: test
projects:
  explicit: []
""")

        result = runner.invoke(workspace, ["validate-refs"])
        # Exit code is the number of errors found
        assert result.exit_code == 3
