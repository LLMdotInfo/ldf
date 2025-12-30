"""Tests for ldf.models.workspace module."""

from datetime import datetime

from ldf.models.workspace import (
    DiscoveryConfig,
    ProjectEntry,
    ProjectInfo,
    ReferencesConfig,
    ReportingConfig,
    SharedConfig,
    WorkspaceManifest,
    WorkspaceProjects,
)


class TestProjectEntry:
    """Tests for ProjectEntry dataclass."""

    def test_basic_creation(self):
        """Test creating a ProjectEntry."""
        entry = ProjectEntry(path="services/auth", alias="auth")
        assert entry.path == "services/auth"
        assert entry.alias == "auth"

    def test_from_dict_with_alias(self):
        """Test creating from dict with explicit alias."""
        entry = ProjectEntry.from_dict({"path": "services/auth", "alias": "authentication"})
        assert entry.path == "services/auth"
        assert entry.alias == "authentication"

    def test_from_dict_auto_generates_alias(self):
        """Test auto-generating alias from path when not provided."""
        entry = ProjectEntry.from_dict({"path": "services/user-auth"})
        assert entry.path == "services/user-auth"
        assert entry.alias == "user-auth"

    def test_from_dict_empty_path(self):
        """Test handling empty path."""
        entry = ProjectEntry.from_dict({})
        assert entry.path == ""
        assert entry.alias == ""  # Path("").name is ""


class TestDiscoveryConfig:
    """Tests for DiscoveryConfig dataclass."""

    def test_default_values(self):
        """Test default discovery config."""
        config = DiscoveryConfig()
        assert config.patterns == ["**/.ldf/config.yaml"]
        assert "node_modules" in config.exclude
        assert ".venv" in config.exclude

    def test_from_dict_none(self):
        """Test from_dict with None returns defaults."""
        config = DiscoveryConfig.from_dict(None)
        assert config.patterns == ["**/.ldf/config.yaml"]
        assert "node_modules" in config.exclude

    def test_from_dict_empty(self):
        """Test from_dict with empty dict returns defaults."""
        config = DiscoveryConfig.from_dict({})
        assert config.patterns == ["**/.ldf/config.yaml"]

    def test_from_dict_custom_values(self):
        """Test from_dict with custom values."""
        config = DiscoveryConfig.from_dict(
            {"patterns": ["**/ldf.yaml"], "exclude": ["build", "dist"]}
        )
        assert config.patterns == ["**/ldf.yaml"]
        assert config.exclude == ["build", "dist"]


class TestWorkspaceProjects:
    """Tests for WorkspaceProjects dataclass."""

    def test_default_values(self):
        """Test default workspace projects."""
        projects = WorkspaceProjects()
        assert projects.explicit == []
        assert isinstance(projects.discovery, DiscoveryConfig)

    def test_from_dict_none(self):
        """Test from_dict with None returns defaults."""
        projects = WorkspaceProjects.from_dict(None)
        assert projects.explicit == []

    def test_from_dict_empty(self):
        """Test from_dict with empty dict returns defaults."""
        projects = WorkspaceProjects.from_dict({})
        assert projects.explicit == []

    def test_from_dict_with_explicit_projects(self):
        """Test from_dict with explicit project entries."""
        projects = WorkspaceProjects.from_dict(
            {
                "explicit": [
                    {"path": "services/auth", "alias": "auth"},
                    {"path": "services/billing", "alias": "billing"},
                ]
            }
        )
        assert len(projects.explicit) == 2
        assert projects.explicit[0].alias == "auth"
        assert projects.explicit[1].alias == "billing"

    def test_from_dict_with_discovery(self):
        """Test from_dict with custom discovery config."""
        projects = WorkspaceProjects.from_dict(
            {"discovery": {"patterns": ["**/project.yaml"], "exclude": ["temp"]}}
        )
        assert projects.discovery.patterns == ["**/project.yaml"]
        assert projects.discovery.exclude == ["temp"]


class TestSharedConfig:
    """Tests for SharedConfig dataclass."""

    def test_default_values(self):
        """Test default shared config."""
        config = SharedConfig()
        assert config.path == ".ldf-shared/"
        assert config.inherit_guardrails is True
        assert config.inherit_templates is True
        assert config.inherit_question_packs is True
        assert config.inherit_macros is True

    def test_from_dict_none(self):
        """Test from_dict with None returns defaults."""
        config = SharedConfig.from_dict(None)
        assert config.inherit_guardrails is True

    def test_from_dict_empty(self):
        """Test from_dict with empty dict returns defaults."""
        config = SharedConfig.from_dict({})
        assert config.inherit_guardrails is True

    def test_from_dict_custom_values(self):
        """Test from_dict with custom values."""
        config = SharedConfig.from_dict(
            {
                "path": ".shared-resources/",
                "inherit": {
                    "guardrails": False,
                    "templates": False,
                    "question_packs": True,
                    "macros": False,
                },
            }
        )
        assert config.path == ".shared-resources/"
        assert config.inherit_guardrails is False
        assert config.inherit_templates is False
        assert config.inherit_question_packs is True
        assert config.inherit_macros is False


class TestReferencesConfig:
    """Tests for ReferencesConfig dataclass."""

    def test_default_values(self):
        """Test default references config."""
        config = ReferencesConfig()
        assert config.enabled is True

    def test_from_dict_none(self):
        """Test from_dict with None returns defaults."""
        config = ReferencesConfig.from_dict(None)
        assert config.enabled is True

    def test_from_dict_disabled(self):
        """Test from_dict with disabled references."""
        config = ReferencesConfig.from_dict({"enabled": False})
        assert config.enabled is False


class TestReportingConfig:
    """Tests for ReportingConfig dataclass."""

    def test_default_values(self):
        """Test default reporting config."""
        config = ReportingConfig()
        assert config.enabled is True
        assert config.output_dir == ".ldf-reports/"

    def test_from_dict_none(self):
        """Test from_dict with None returns defaults."""
        config = ReportingConfig.from_dict(None)
        assert config.enabled is True

    def test_from_dict_custom_values(self):
        """Test from_dict with custom values."""
        config = ReportingConfig.from_dict({"enabled": False, "output_dir": "reports/"})
        assert config.enabled is False
        assert config.output_dir == "reports/"


class TestWorkspaceManifest:
    """Tests for WorkspaceManifest dataclass."""

    def test_basic_creation(self):
        """Test basic manifest creation."""
        manifest = WorkspaceManifest(version="1.0", name="test-workspace")
        assert manifest.version == "1.0"
        assert manifest.name == "test-workspace"

    def test_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        manifest = WorkspaceManifest.from_dict({})
        assert manifest.version == "1.0"
        assert manifest.name == ""

    def test_from_dict_full(self):
        """Test from_dict with full data."""
        manifest = WorkspaceManifest.from_dict(
            {
                "version": "2.0",
                "name": "my-workspace",
                "projects": {"explicit": [{"path": "services/auth", "alias": "auth"}]},
                "shared": {"path": ".shared/", "inherit": {"guardrails": False}},
                "references": {"enabled": False},
                "reporting": {"enabled": False},
            }
        )
        assert manifest.version == "2.0"
        assert manifest.name == "my-workspace"
        assert len(manifest.projects.explicit) == 1
        assert manifest.shared.path == ".shared/"
        assert manifest.references.enabled is False
        assert manifest.reporting.enabled is False

    def test_get_all_project_entries_explicit_only(self):
        """Test get_all_project_entries with only explicit projects."""
        manifest = WorkspaceManifest.from_dict(
            {
                "name": "test",
                "projects": {
                    "explicit": [
                        {"path": "services/auth", "alias": "auth"},
                        {"path": "services/billing", "alias": "billing"},
                    ]
                },
            }
        )
        # No workspace_root means no discovery
        entries = manifest.get_all_project_entries()
        assert len(entries) == 2
        assert entries[0].alias == "auth"
        assert entries[1].alias == "billing"

    def test_get_all_project_entries_with_discovery(self, tmp_path):
        """Test get_all_project_entries with discovery."""
        # Create project structure
        auth_project = tmp_path / "services" / "auth" / ".ldf"
        auth_project.mkdir(parents=True)
        (auth_project / "config.yaml").write_text("")

        manifest = WorkspaceManifest.from_dict(
            {"name": "test", "projects": {"discovery": {"patterns": ["**/.ldf/config.yaml"]}}}
        )

        entries = manifest.get_all_project_entries(tmp_path)
        assert len(entries) == 1
        assert entries[0].path == "services/auth"
        assert entries[0].alias == "auth"

    def test_get_all_project_entries_deduplicates(self, tmp_path):
        """Test that explicit and discovered entries are deduplicated."""
        # Create project structure
        auth_project = tmp_path / "services" / "auth" / ".ldf"
        auth_project.mkdir(parents=True)
        (auth_project / "config.yaml").write_text("")

        manifest = WorkspaceManifest.from_dict(
            {
                "name": "test",
                "projects": {
                    "explicit": [{"path": "services/auth", "alias": "auth-explicit"}],
                    "discovery": {"patterns": ["**/.ldf/config.yaml"]},
                },
            }
        )

        entries = manifest.get_all_project_entries(tmp_path)
        # Should only have 1 entry (explicit takes precedence)
        assert len(entries) == 1
        assert entries[0].alias == "auth-explicit"


class TestDiscoverProjects:
    """Tests for WorkspaceManifest._discover_projects method."""

    def test_discovers_nested_projects(self, tmp_path):
        """Test discovering nested projects."""
        # Create multiple projects
        for name in ["auth", "billing", "api"]:
            project = tmp_path / "services" / name / ".ldf"
            project.mkdir(parents=True)
            (project / "config.yaml").write_text("")

        manifest = WorkspaceManifest(version="1.0", name="test")
        discovered = manifest._discover_projects(tmp_path)

        assert len(discovered) == 3
        aliases = {e.alias for e in discovered}
        assert aliases == {"auth", "billing", "api"}

    def test_excludes_node_modules(self, tmp_path):
        """Test that node_modules directories are excluded."""
        # Create project in node_modules (should be excluded)
        excluded = tmp_path / "node_modules" / "some-package" / ".ldf"
        excluded.mkdir(parents=True)
        (excluded / "config.yaml").write_text("")

        # Create valid project
        valid = tmp_path / "services" / "auth" / ".ldf"
        valid.mkdir(parents=True)
        (valid / "config.yaml").write_text("")

        manifest = WorkspaceManifest(version="1.0", name="test")
        discovered = manifest._discover_projects(tmp_path)

        assert len(discovered) == 1
        assert discovered[0].alias == "auth"

    def test_excludes_venv(self, tmp_path):
        """Test that .venv directories are excluded."""
        # Create project in .venv (should be excluded)
        excluded = tmp_path / ".venv" / "lib" / ".ldf"
        excluded.mkdir(parents=True)
        (excluded / "config.yaml").write_text("")

        manifest = WorkspaceManifest(version="1.0", name="test")
        discovered = manifest._discover_projects(tmp_path)

        assert len(discovered) == 0

    def test_skips_workspace_root(self, tmp_path):
        """Test that workspace root itself is skipped."""
        # Create .ldf at workspace root
        root_ldf = tmp_path / ".ldf"
        root_ldf.mkdir()
        (root_ldf / "config.yaml").write_text("")

        manifest = WorkspaceManifest(version="1.0", name="test")
        discovered = manifest._discover_projects(tmp_path)

        assert len(discovered) == 0

    def test_custom_patterns(self, tmp_path):
        """Test discovery with custom patterns."""
        # Create project with custom pattern
        project = tmp_path / "apps" / "web" / "ldf.yaml"
        project.parent.mkdir(parents=True)
        project.write_text("")

        manifest = WorkspaceManifest.from_dict(
            {"name": "test", "projects": {"discovery": {"patterns": ["**/ldf.yaml"]}}}
        )
        discovered = manifest._discover_projects(tmp_path)

        # Pattern matches ldf.yaml, so parent is "web" and parent.parent is "apps"
        assert len(discovered) == 1

    def test_custom_exclude(self, tmp_path):
        """Test discovery with custom exclude list."""
        # Create project in custom excluded directory
        excluded = tmp_path / "legacy" / "old" / ".ldf"
        excluded.mkdir(parents=True)
        (excluded / "config.yaml").write_text("")

        # Create valid project
        valid = tmp_path / "services" / "auth" / ".ldf"
        valid.mkdir(parents=True)
        (valid / "config.yaml").write_text("")

        manifest = WorkspaceManifest.from_dict(
            {
                "name": "test",
                "projects": {
                    "discovery": {"patterns": ["**/.ldf/config.yaml"], "exclude": ["legacy"]}
                },
            }
        )
        discovered = manifest._discover_projects(tmp_path)

        assert len(discovered) == 1
        assert discovered[0].alias == "auth"


class TestProjectInfo:
    """Tests for ProjectInfo dataclass."""

    def test_basic_creation(self):
        """Test basic ProjectInfo creation."""
        info = ProjectInfo(path="services/auth", alias="auth")
        assert info.path == "services/auth"
        assert info.alias == "auth"
        assert info.name == ""
        assert info.specs == []
        assert info.coverage is None
        assert info.last_lint is None

    def test_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        info = ProjectInfo.from_dict("auth", {})
        assert info.alias == "auth"
        assert info.path == ""
        assert info.specs == []

    def test_from_dict_full(self):
        """Test from_dict with full data."""
        info = ProjectInfo.from_dict(
            "auth",
            {
                "path": "services/auth",
                "name": "Authentication Service",
                "version": "2.0.0",
                "ldf_version": "1.1.0",
                "specs": ["login", "logout", "registration"],
                "coverage": 85.5,
                "last_lint": "2024-01-15T10:30:00",
            },
        )
        assert info.alias == "auth"
        assert info.path == "services/auth"
        assert info.name == "Authentication Service"
        assert info.version == "2.0.0"
        assert info.ldf_version == "1.1.0"
        assert info.specs == ["login", "logout", "registration"]
        assert info.coverage == 85.5
        assert info.last_lint == datetime(2024, 1, 15, 10, 30, 0)

    def test_from_dict_invalid_last_lint(self):
        """Test from_dict with invalid last_lint value."""
        info = ProjectInfo.from_dict("auth", {"last_lint": "not-a-date"})
        assert info.last_lint is None

    def test_from_dict_last_lint_wrong_type(self):
        """Test from_dict with wrong type for last_lint."""
        info = ProjectInfo.from_dict("auth", {"last_lint": 12345})
        assert info.last_lint is None

    def test_to_dict_minimal(self):
        """Test to_dict with minimal data."""
        info = ProjectInfo(path="services/auth", alias="auth")
        result = info.to_dict()

        assert result["path"] == "services/auth"
        assert result["name"] == ""
        assert result["specs"] == []
        assert "coverage" not in result
        assert "last_lint" not in result

    def test_to_dict_full(self):
        """Test to_dict with full data."""
        now = datetime(2024, 1, 15, 10, 30, 0)
        info = ProjectInfo(
            path="services/auth",
            alias="auth",
            name="Auth Service",
            version="1.0.0",
            ldf_version="1.1.0",
            specs=["login", "logout"],
            coverage=95.0,
            last_lint=now,
        )
        result = info.to_dict()

        assert result["path"] == "services/auth"
        assert result["name"] == "Auth Service"
        assert result["version"] == "1.0.0"
        assert result["ldf_version"] == "1.1.0"
        assert result["specs"] == ["login", "logout"]
        assert result["coverage"] == 95.0
        assert result["last_lint"] == "2024-01-15T10:30:00"

    def test_to_dict_no_coverage_when_none(self):
        """Test that coverage is not included when None."""
        info = ProjectInfo(path="test", alias="test", coverage=None)
        result = info.to_dict()
        assert "coverage" not in result

    def test_to_dict_includes_zero_coverage(self):
        """Test that zero coverage is included (not confused with None)."""
        info = ProjectInfo(path="test", alias="test", coverage=0.0)
        result = info.to_dict()
        assert result["coverage"] == 0.0
