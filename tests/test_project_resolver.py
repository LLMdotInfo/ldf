"""Tests for ldf.project_resolver module."""

from unittest.mock import patch

import pytest

from ldf.project_resolver import (
    WORKSPACE_MANIFEST,
    ProjectContext,
    ProjectNotFoundError,
    ProjectResolver,
    WorkspaceNotFoundError,
    find_workspace_root,
)


class TestFindWorkspaceRoot:
    """Tests for the find_workspace_root function."""

    def test_finds_workspace_in_current_dir(self, tmp_path):
        """Test finding workspace when manifest is in current directory."""
        manifest = tmp_path / WORKSPACE_MANIFEST
        manifest.write_text("name: test-workspace\n")

        result = find_workspace_root(tmp_path)
        assert result == tmp_path

    def test_finds_workspace_in_parent_dir(self, tmp_path):
        """Test finding workspace when manifest is in parent directory."""
        manifest = tmp_path / WORKSPACE_MANIFEST
        manifest.write_text("name: test-workspace\n")

        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        result = find_workspace_root(subdir)
        assert result == tmp_path

    def test_returns_none_when_no_workspace(self, tmp_path):
        """Test returning None when no workspace manifest exists."""
        result = find_workspace_root(tmp_path)
        assert result is None

    def test_uses_cwd_as_default(self, tmp_path, monkeypatch):
        """Test using cwd as default start path."""
        manifest = tmp_path / WORKSPACE_MANIFEST
        manifest.write_text("name: test-workspace\n")

        monkeypatch.chdir(tmp_path)
        result = find_workspace_root()
        assert result == tmp_path


class TestProjectContext:
    """Tests for the ProjectContext dataclass."""

    def test_basic_context(self, tmp_path):
        """Test creating a basic ProjectContext."""
        ctx = ProjectContext(project_root=tmp_path)

        assert ctx.project_root == tmp_path
        assert ctx.workspace_root is None
        assert ctx.project_alias is None
        assert ctx.is_workspace_member is False
        assert ctx.shared_resources_path is None

    def test_workspace_context(self, tmp_path):
        """Test creating a workspace ProjectContext."""
        workspace_root = tmp_path / "workspace"
        project_root = workspace_root / "projects" / "auth"
        shared_path = workspace_root / ".ldf-shared"

        ctx = ProjectContext(
            project_root=project_root,
            workspace_root=workspace_root,
            project_alias="auth",
            is_workspace_member=True,
            shared_resources_path=shared_path,
        )

        assert ctx.project_root == project_root
        assert ctx.workspace_root == workspace_root
        assert ctx.project_alias == "auth"
        assert ctx.is_workspace_member is True
        assert ctx.shared_resources_path == shared_path

    def test_ldf_dir_property(self, tmp_path):
        """Test the ldf_dir property."""
        ctx = ProjectContext(project_root=tmp_path)
        assert ctx.ldf_dir == tmp_path / ".ldf"

    def test_config_path_property(self, tmp_path):
        """Test the config_path property."""
        ctx = ProjectContext(project_root=tmp_path)
        assert ctx.config_path == tmp_path / ".ldf" / "config.yaml"

    def test_specs_dir_property(self, tmp_path):
        """Test the specs_dir property."""
        ctx = ProjectContext(project_root=tmp_path)
        assert ctx.specs_dir == tmp_path / ".ldf" / "specs"


class TestProjectNotFoundError:
    """Tests for ProjectNotFoundError exception."""

    def test_basic_error(self):
        """Test basic error without available projects."""
        error = ProjectNotFoundError("Project not found")
        assert str(error) == "Project not found"
        assert error.available_projects == []

    def test_error_with_available_projects(self):
        """Test error with available projects list."""
        error = ProjectNotFoundError(
            "Project 'foo' not found", available_projects=["auth", "billing", "api"]
        )
        assert "foo" in str(error)
        assert error.available_projects == ["auth", "billing", "api"]


class TestWorkspaceNotFoundError:
    """Tests for WorkspaceNotFoundError exception."""

    def test_basic_error(self):
        """Test basic workspace not found error."""
        error = WorkspaceNotFoundError("Workspace not found")
        assert str(error) == "Workspace not found"


class TestProjectResolver:
    """Tests for the ProjectResolver class."""

    def test_init_with_default_cwd(self, tmp_path, monkeypatch):
        """Test initializing resolver with default cwd."""
        monkeypatch.chdir(tmp_path)
        resolver = ProjectResolver()
        assert resolver._cwd == tmp_path

    def test_init_with_custom_cwd(self, tmp_path):
        """Test initializing resolver with custom cwd."""
        resolver = ProjectResolver(cwd=tmp_path)
        assert resolver._cwd == tmp_path

    def test_resolve_single_project(self, tmp_path):
        """Test resolving a single project (not in workspace)."""
        # Create LDF project structure
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=tmp_path)
        ctx = resolver.resolve()

        assert ctx.project_root == tmp_path
        assert ctx.is_workspace_member is False
        assert ctx.workspace_root is None

    def test_resolve_no_project_raises_error(self, tmp_path):
        """Test that resolving without a project raises error."""
        resolver = ProjectResolver(cwd=tmp_path)

        with pytest.raises(ProjectNotFoundError) as exc_info:
            resolver.resolve()

        assert "No LDF project found" in str(exc_info.value)

    def test_resolve_from_env_variable(self, tmp_path, monkeypatch):
        """Test resolving project from LDF_PROJECT environment variable."""
        # Create LDF project structure
        project_path = tmp_path / "my-project"
        project_path.mkdir()
        ldf_dir = project_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        # Set environment variable
        monkeypatch.setenv("LDF_PROJECT", str(project_path))

        resolver = ProjectResolver(cwd=tmp_path)
        ctx = resolver.resolve()

        assert ctx.project_root == project_path

    def test_resolve_with_explicit_workspace(self, tmp_path):
        """Test resolving with explicit workspace argument."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create workspace manifest
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: true
    templates: true
""")

        # Create project
        auth_project = workspace / "services" / "auth"
        auth_project.mkdir(parents=True)
        auth_ldf = auth_project / ".ldf"
        auth_ldf.mkdir()
        (auth_ldf / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=auth_project)
        ctx = resolver.resolve(workspace=str(workspace))

        assert ctx.project_root == auth_project
        assert ctx.workspace_root == workspace
        assert ctx.is_workspace_member is True

    def test_resolve_with_invalid_workspace_raises_error(self, tmp_path):
        """Test that invalid workspace path raises error."""
        resolver = ProjectResolver(cwd=tmp_path)

        with pytest.raises(WorkspaceNotFoundError) as exc_info:
            resolver.resolve(workspace=str(tmp_path / "nonexistent"))

        assert "No ldf-workspace.yaml found" in str(exc_info.value)

    def test_resolve_project_by_alias(self, tmp_path):
        """Test resolving project by alias in workspace."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create workspace manifest
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
    - path: services/billing
      alias: billing
shared:
  path: .ldf-shared
  inherit:
    guardrails: false
    templates: false
""")

        # Create projects
        for proj in ["auth", "billing"]:
            proj_path = workspace / "services" / proj
            proj_path.mkdir(parents=True)
            ldf_dir = proj_path / ".ldf"
            ldf_dir.mkdir()
            (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=workspace)
        ctx = resolver.resolve(project="billing")

        assert ctx.project_root == workspace / "services" / "billing"
        assert ctx.project_alias == "billing"
        assert ctx.is_workspace_member is True

    def test_resolve_project_by_path(self, tmp_path):
        """Test resolving project by path in workspace."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create workspace manifest
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: false
    templates: false
""")

        # Create project
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)
        ldf_dir = auth_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=workspace)
        ctx = resolver.resolve(project="services/auth")

        assert ctx.project_root == auth_path
        assert ctx.project_alias == "auth"

    def test_resolve_project_not_found_in_workspace(self, tmp_path):
        """Test error when project not found in workspace."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create workspace manifest
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: false
    templates: false
""")

        # Create project
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)
        ldf_dir = auth_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=workspace)

        with pytest.raises(ProjectNotFoundError) as exc_info:
            resolver.resolve(project="nonexistent")

        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.available_projects == ["auth"]

    def test_resolve_project_as_path_without_workspace(self, tmp_path):
        """Test resolving project as direct path when no workspace."""
        # Create LDF project structure
        project_path = tmp_path / "my-project"
        project_path.mkdir()
        ldf_dir = project_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=tmp_path)
        ctx = resolver.resolve(project=str(project_path))

        assert ctx.project_root == project_path
        assert ctx.is_workspace_member is False

    def test_resolve_invalid_project_path_raises_error(self, tmp_path):
        """Test error when project path is invalid."""
        resolver = ProjectResolver(cwd=tmp_path)

        with pytest.raises(ProjectNotFoundError) as exc_info:
            resolver.resolve(project=str(tmp_path / "nonexistent"))

        assert "not a valid project path" in str(exc_info.value)

    def test_resolve_cwd_in_workspace(self, tmp_path):
        """Test auto-detecting project from cwd within workspace."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create workspace manifest
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: false
    templates: false
""")

        # Create project
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)
        ldf_dir = auth_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        # Create subdir within project
        subdir = auth_path / "src" / "handlers"
        subdir.mkdir(parents=True)

        # Resolve from within project subdir
        resolver = ProjectResolver(cwd=subdir)
        ctx = resolver.resolve()

        assert ctx.project_root == auth_path
        assert ctx.project_alias == "auth"
        assert ctx.is_workspace_member is True


class TestLoadWorkspaceManifest:
    """Tests for _load_workspace_manifest method."""

    def test_returns_none_for_missing_manifest(self, tmp_path):
        """Test returning None when manifest doesn't exist."""
        resolver = ProjectResolver(cwd=tmp_path)
        result = resolver._load_workspace_manifest(tmp_path)
        assert result is None

    def test_raises_on_yaml_error(self, tmp_path):
        """Test raising WorkspaceNotFoundError on YAML parse error."""
        manifest = tmp_path / WORKSPACE_MANIFEST
        manifest.write_text("invalid: yaml: content: [")

        resolver = ProjectResolver(cwd=tmp_path)

        with pytest.raises(WorkspaceNotFoundError) as exc_info:
            resolver._load_workspace_manifest(tmp_path)

        assert "Invalid workspace manifest" in str(exc_info.value)

    def test_raises_on_validation_error(self, tmp_path):
        """Test raising WorkspaceNotFoundError on manifest validation error."""
        manifest = tmp_path / WORKSPACE_MANIFEST
        # Pass a list where dict is expected for projects - this causes TypeError
        # when trying to call .get() on a list
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - this-is-a-string-not-a-dict
""")

        resolver = ProjectResolver(cwd=tmp_path)

        with pytest.raises(WorkspaceNotFoundError) as exc_info:
            resolver._load_workspace_manifest(tmp_path)

        assert "Invalid workspace manifest" in str(exc_info.value)

    def test_returns_none_on_unexpected_error(self, tmp_path):
        """Test returning None on unexpected errors (with logging)."""
        manifest = tmp_path / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit: []
""")

        resolver = ProjectResolver(cwd=tmp_path)

        # Mock WorkspaceManifest.from_dict to raise unexpected error
        # The import is inside the method, so patch at the source module
        with patch("ldf.models.workspace.WorkspaceManifest.from_dict") as mock:
            mock.side_effect = RuntimeError("Unexpected error")
            result = resolver._load_workspace_manifest(tmp_path)

        assert result is None


class TestIsLdfProject:
    """Tests for _is_ldf_project method."""

    def test_returns_true_for_valid_project(self, tmp_path):
        """Test returning True for valid LDF project."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=tmp_path)
        assert resolver._is_ldf_project(tmp_path) is True

    def test_returns_false_for_missing_ldf_dir(self, tmp_path):
        """Test returning False when .ldf directory is missing."""
        resolver = ProjectResolver(cwd=tmp_path)
        assert resolver._is_ldf_project(tmp_path) is False

    def test_returns_false_for_missing_config(self, tmp_path):
        """Test returning False when config.yaml is missing."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        # Don't create config.yaml

        resolver = ProjectResolver(cwd=tmp_path)
        assert resolver._is_ldf_project(tmp_path) is False


class TestResolveProjectInWorkspace:
    """Tests for _resolve_project_in_workspace method."""

    def test_project_alias_exists_but_not_initialized(self, tmp_path):
        """Test error when project alias exists but project not initialized."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create workspace manifest (use correct YAML format)
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: false
    templates: false
""")

        # Create project directory but NOT .ldf/config.yaml
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)

        resolver = ProjectResolver(cwd=workspace)

        with pytest.raises(ProjectNotFoundError) as exc_info:
            resolver.resolve(project="auth")

        assert "not a valid LDF project" in str(exc_info.value)
        assert "missing .ldf/config.yaml" in str(exc_info.value)


class TestBuildWorkspaceContext:
    """Tests for _build_workspace_context method."""

    def test_with_shared_resources(self, tmp_path):
        """Test building context with shared resources."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create shared resources
        shared_path = workspace / ".ldf-shared"
        shared_path.mkdir()

        # Create workspace manifest
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: true
    templates: true
""")

        # Create project
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)
        ldf_dir = auth_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=workspace)
        ctx = resolver.resolve(project="auth")

        assert ctx.shared_resources_path == shared_path

    def test_without_shared_resources_when_disabled(self, tmp_path):
        """Test building context without shared resources when disabled."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create shared resources directory (but disabled in manifest)
        shared_path = workspace / ".ldf-shared"
        shared_path.mkdir()

        # Create workspace manifest with sharing disabled (correct YAML format)
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: false
    templates: false
""")

        # Create project
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)
        ldf_dir = auth_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=workspace)
        ctx = resolver.resolve(project="auth")

        assert ctx.shared_resources_path is None

    def test_without_shared_resources_when_missing(self, tmp_path):
        """Test building context without shared resources when path missing."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # DON'T create shared resources directory

        # Create workspace manifest with sharing enabled but path missing
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: true
    templates: true
""")

        # Create project
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)
        ldf_dir = auth_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        resolver = ProjectResolver(cwd=workspace)
        ctx = resolver.resolve(project="auth")

        assert ctx.shared_resources_path is None


class TestFindWorkspaceRootMethod:
    """Tests for ProjectResolver._find_workspace_root method."""

    def test_finds_workspace_walking_up(self, tmp_path):
        """Test finding workspace by walking up directories."""
        # Create workspace at root
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("name: test\n")

        # Create nested directory
        nested = workspace / "a" / "b" / "c"
        nested.mkdir(parents=True)

        resolver = ProjectResolver(cwd=nested)
        result = resolver._find_workspace_root(nested)

        assert result == workspace

    def test_returns_none_at_filesystem_root(self, tmp_path):
        """Test returning None when reaching filesystem root."""
        resolver = ProjectResolver(cwd=tmp_path)
        result = resolver._find_workspace_root(tmp_path)
        assert result is None


class TestResolveCwdInWorkspace:
    """Tests for _resolve_cwd_in_workspace method."""

    def test_cwd_not_in_any_project(self, tmp_path):
        """Test returning None when cwd is not in any project."""
        # Create workspace structure
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create workspace manifest
        manifest = workspace / WORKSPACE_MANIFEST
        manifest.write_text("""
name: test-workspace
version: "1.0"
projects:
  explicit:
    - path: services/auth
      alias: auth
shared:
  path: .ldf-shared
  inherit:
    guardrails: false
    templates: false
""")

        # Create project
        auth_path = workspace / "services" / "auth"
        auth_path.mkdir(parents=True)
        ldf_dir = auth_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("_schema_version: '1.1'\n")

        # Create a different directory outside any project
        other_dir = workspace / "other"
        other_dir.mkdir()

        resolver = ProjectResolver(cwd=other_dir)

        # This should fall through to single-project mode and fail
        with pytest.raises(ProjectNotFoundError):
            resolver.resolve()
