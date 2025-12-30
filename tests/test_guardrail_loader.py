"""Tests for ldf.utils.guardrail_loader module."""

from pathlib import Path

import pytest

from ldf.utils.guardrail_loader import (
    Guardrail,
    _get_default_core_guardrails,
    get_active_guardrails,
    get_guardrail_by_id,
    get_guardrail_by_name,
    load_core_guardrails,
    load_guardrails,
    load_preset_guardrails,
)


class TestLoadCoreGuardrails:
    """Tests for load_core_guardrails function."""

    def test_loads_core_guardrails(self):
        """Test loading core guardrails from framework."""
        guardrails = load_core_guardrails()

        assert len(guardrails) == 8
        assert guardrails[0].id == 1
        assert guardrails[0].name == "Testing Coverage"
        assert guardrails[0].severity == "critical"
        assert guardrails[0].enabled is True

    def test_core_guardrails_have_required_fields(self):
        """Test that all core guardrails have required fields."""
        guardrails = load_core_guardrails()

        for g in guardrails:
            assert isinstance(g.id, int)
            assert isinstance(g.name, str)
            assert len(g.name) > 0
            assert g.severity in ("critical", "high", "medium", "low")


class TestLoadPresetGuardrails:
    """Tests for load_preset_guardrails function."""

    def test_loads_saas_preset(self, ldf_framework_path: Path):
        """Test loading SaaS preset guardrails."""
        saas_file = ldf_framework_path / "guardrails" / "presets" / "saas.yaml"
        if not saas_file.exists():
            pytest.skip("SaaS preset not found")

        guardrails = load_preset_guardrails("saas")

        # SaaS preset should have additional guardrails
        assert len(guardrails) > 0
        assert any(g.name == "Multi-Tenancy" or "tenancy" in g.name.lower() for g in guardrails)

    def test_handles_missing_preset(self):
        """Test handling of non-existent preset."""
        guardrails = load_preset_guardrails("nonexistent-preset")

        assert guardrails == []

    def test_custom_preset_returns_empty(self):
        """Test that 'custom' preset returns empty list."""
        guardrails = load_preset_guardrails("custom")

        assert guardrails == []


class TestLoadGuardrails:
    """Tests for load_guardrails function."""

    def test_returns_core_guardrails_for_project(self, temp_project: Path):
        """Test that core guardrails are returned for a project."""
        guardrails = load_guardrails(temp_project)

        assert len(guardrails) == 8
        assert all(isinstance(g, Guardrail) for g in guardrails)

    def test_returns_core_for_non_ldf_project(self, tmp_path: Path):
        """Test returns core guardrails for non-LDF project."""
        guardrails = load_guardrails(tmp_path)

        # Should fall back to core guardrails
        assert len(guardrails) == 8
        assert isinstance(guardrails, list)


class TestGetActiveGuardrails:
    """Tests for get_active_guardrails function."""

    def test_returns_enabled_guardrails(self, temp_project: Path):
        """Test that only enabled guardrails are returned."""
        guardrails = get_active_guardrails(temp_project)

        assert len(guardrails) == 8
        assert all(isinstance(g, Guardrail) for g in guardrails)
        assert all(g.enabled for g in guardrails)

    def test_filters_disabled_guardrails(self, temp_project: Path):
        """Test that disabled guardrails are filtered out."""
        # Update guardrails.yaml to disable one
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
extends: core
disabled:
  - 8  # Disable Documentation guardrail
""")

        guardrails = get_active_guardrails(temp_project)

        assert len(guardrails) == 7
        assert not any(g.id == 8 for g in guardrails)


class TestGuardrailDataclass:
    """Tests for Guardrail dataclass."""

    def test_guardrail_creation(self):
        """Test creating a Guardrail instance."""
        guardrail = Guardrail(
            id=1,
            name="Test Guardrail",
            description="A test guardrail",
            severity="high",
            enabled=True,
        )

        assert guardrail.id == 1
        assert guardrail.name == "Test Guardrail"
        assert guardrail.description == "A test guardrail"
        assert guardrail.severity == "high"
        assert guardrail.enabled is True

    def test_guardrail_defaults(self):
        """Test Guardrail default values."""
        guardrail = Guardrail(
            id=1,
            name="Test",
            description="Test",
            severity="medium",
            enabled=True,
        )

        assert guardrail.config == {}

    def test_guardrail_with_config(self):
        """Test Guardrail with custom config."""
        guardrail = Guardrail(
            id=1,
            name="Coverage",
            description="Test coverage",
            severity="critical",
            enabled=True,
            config={"threshold": 80, "critical_paths": 90},
        )

        assert guardrail.config["threshold"] == 80
        assert guardrail.config["critical_paths"] == 90

    def test_guardrail_from_dict(self):
        """Test creating Guardrail from dictionary."""
        data = {
            "id": 99,
            "name": "Custom Check",
            "description": "A custom guardrail",
            "severity": "low",
            "enabled": False,
            "checklist": ["Check item 1", "Check item 2"],
            "config": {"key": "value"},
        }

        guardrail = Guardrail.from_dict(data)

        assert guardrail.id == 99
        assert guardrail.name == "Custom Check"
        assert guardrail.description == "A custom guardrail"
        assert guardrail.severity == "low"
        assert guardrail.enabled is False
        assert len(guardrail.checklist) == 2
        assert guardrail.config == {"key": "value"}

    def test_guardrail_from_dict_minimal(self):
        """Test creating Guardrail from minimal dictionary."""
        data = {
            "id": 1,
            "name": "Minimal",
        }

        guardrail = Guardrail.from_dict(data)

        assert guardrail.id == 1
        assert guardrail.name == "Minimal"
        assert guardrail.description == ""
        assert guardrail.severity == "medium"  # default
        assert guardrail.enabled is True  # default
        assert guardrail.checklist == []  # default
        assert guardrail.config == {}  # default


class TestLoadCoreGuardrailsFallback:
    """Tests for load_core_guardrails fallback behavior."""

    def test_uses_defaults_when_core_file_missing(self, monkeypatch):
        """Test fallback to defaults when core.yaml is missing."""
        from ldf.utils import guardrail_loader

        # Mock the path to not exist
        fake_path = Path("/nonexistent/path/core.yaml")
        monkeypatch.setattr(guardrail_loader, "CORE_GUARDRAILS_PATH", fake_path)

        guardrails = load_core_guardrails()

        # Should return default guardrails
        assert len(guardrails) == 8
        assert guardrails[0].name == "Testing Coverage"


class TestGetDefaultCoreGuardrails:
    """Tests for _get_default_core_guardrails function."""

    def test_returns_eight_guardrails(self):
        """Test that defaults return 8 guardrails."""
        defaults = _get_default_core_guardrails()

        assert len(defaults) == 8

    def test_default_guardrails_have_all_ids(self):
        """Test that default guardrails have IDs 1-8."""
        defaults = _get_default_core_guardrails()
        ids = [g.id for g in defaults]

        assert ids == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_default_guardrails_have_names(self):
        """Test that default guardrails have expected names."""
        defaults = _get_default_core_guardrails()
        names = [g.name for g in defaults]

        assert "Testing Coverage" in names
        assert "Security Basics" in names
        assert "Error Handling" in names


class TestLoadGuardrailsEdgeCases:
    """Edge case tests for load_guardrails function."""

    def test_uses_cwd_when_project_root_is_none(self, temp_project: Path, monkeypatch):
        """Test using cwd when project_root is None."""
        monkeypatch.chdir(temp_project)

        guardrails = load_guardrails(None)

        assert len(guardrails) == 8
        assert all(isinstance(g, Guardrail) for g in guardrails)

    def test_loads_preset_guardrails(self, temp_project: Path, ldf_framework_path: Path):
        """Test loading guardrails with a preset."""
        # Check if saas preset exists
        saas_file = ldf_framework_path / "guardrails" / "presets" / "saas.yaml"
        if not saas_file.exists():
            pytest.skip("SaaS preset not found")

        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
preset: saas
""")

        guardrails = load_guardrails(temp_project)

        # Should have core + preset guardrails
        assert len(guardrails) > 8

    def test_applies_overrides(self, temp_project: Path):
        """Test applying overrides to guardrails."""
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
overrides:
  "1":
    enabled: false
    config:
      threshold: 95
""")

        guardrails = load_guardrails(temp_project)

        guardrail_1 = next(g for g in guardrails if g.id == 1)
        assert guardrail_1.enabled is False
        assert guardrail_1.config.get("threshold") == 95

    def test_adds_custom_guardrails(self, temp_project: Path):
        """Test adding custom guardrails from config."""
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
custom:
  - id: 100
    name: "Custom Team Rule"
    description: "A custom rule for the team"
    severity: "medium"
    checklist:
      - "Check custom thing"
""")

        guardrails = load_guardrails(temp_project)

        # Should have 8 core + 1 custom
        assert len(guardrails) == 9
        custom = next((g for g in guardrails if g.id == 100), None)
        assert custom is not None
        assert custom.name == "Custom Team Rule"

    def test_disables_guardrail_by_name(self, temp_project: Path):
        """Test disabling guardrail by name."""
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
disabled:
  - "Testing Coverage"
""")

        guardrails = load_guardrails(temp_project)

        testing_coverage = next(g for g in guardrails if g.name == "Testing Coverage")
        assert testing_coverage.enabled is False

    def test_filters_by_selected_ids(self, temp_project: Path):
        """Test filtering guardrails by selected_ids from ldf init --custom."""
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
selected_ids:
  - 1
  - 3
  - 5
""")

        guardrails = load_guardrails(temp_project)

        # Should only return the 3 selected guardrails
        assert len(guardrails) == 3
        ids = [g.id for g in guardrails]
        assert ids == [1, 3, 5]

    def test_selected_ids_maintains_order(self, temp_project: Path):
        """Test that selected_ids maintains the specified order."""
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
selected_ids:
  - 8
  - 2
  - 5
  - 1
""")

        guardrails = load_guardrails(temp_project)

        ids = [g.id for g in guardrails]
        assert ids == [8, 2, 5, 1]

    def test_selected_ids_ignores_nonexistent(self, temp_project: Path):
        """Test that selected_ids ignores IDs that don't exist."""
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("""version: "1.0"
selected_ids:
  - 1
  - 999
  - 3
""")

        guardrails = load_guardrails(temp_project)

        # Should only return guardrails 1 and 3, not 999
        assert len(guardrails) == 2
        ids = [g.id for g in guardrails]
        assert ids == [1, 3]


class TestGetGuardrailById:
    """Tests for get_guardrail_by_id function."""

    def test_finds_guardrail_by_id(self, temp_project: Path):
        """Test finding a guardrail by its ID."""
        guardrail = get_guardrail_by_id(1, temp_project)

        assert guardrail is not None
        assert guardrail.id == 1
        assert guardrail.name == "Testing Coverage"

    def test_returns_none_for_unknown_id(self, temp_project: Path):
        """Test returning None for unknown ID."""
        guardrail = get_guardrail_by_id(999, temp_project)

        assert guardrail is None

    def test_uses_cwd_when_project_root_is_none(self, temp_project: Path, monkeypatch):
        """Test using cwd when project_root is None."""
        monkeypatch.chdir(temp_project)

        guardrail = get_guardrail_by_id(1, None)

        assert guardrail is not None
        assert guardrail.id == 1


class TestLoadSharedGuardrails:
    """Tests for load_shared_guardrails function."""

    def test_returns_empty_when_no_guardrails_dir(self, tmp_path):
        """Test returns empty list when guardrails directory doesn't exist."""
        from ldf.utils.guardrail_loader import load_shared_guardrails

        shared_path = tmp_path / ".ldf-shared"
        shared_path.mkdir()
        # No guardrails subdirectory

        result = load_shared_guardrails(shared_path)

        assert result == []

    def test_loads_guardrails_from_yaml_files(self, tmp_path):
        """Test loading guardrails from YAML files in shared resources."""
        from ldf.utils.guardrail_loader import load_shared_guardrails

        shared_path = tmp_path / ".ldf-shared"
        guardrails_dir = shared_path / "guardrails"
        guardrails_dir.mkdir(parents=True)

        # Create a shared guardrails file
        guardrails_dir.joinpath("team-rules.yaml").write_text("""
guardrails:
  - id: 100
    name: "Team Rule 1"
    description: "First shared rule"
    severity: high
  - id: 101
    name: "Team Rule 2"
    description: "Second shared rule"
    severity: medium
""")

        result = load_shared_guardrails(shared_path)

        assert len(result) == 2
        assert result[0].id == 100
        assert result[0].name == "Team Rule 1"
        assert result[1].id == 101

    def test_handles_malformed_yaml(self, tmp_path, caplog):
        """Test graceful handling of malformed YAML files."""
        from ldf.utils.guardrail_loader import load_shared_guardrails

        shared_path = tmp_path / ".ldf-shared"
        guardrails_dir = shared_path / "guardrails"
        guardrails_dir.mkdir(parents=True)

        # Create a malformed YAML file
        guardrails_dir.joinpath("bad.yaml").write_text("not: valid: yaml: [[[")

        result = load_shared_guardrails(shared_path)

        # Should return empty list and log a warning
        assert result == []

    def test_loads_from_multiple_yaml_files(self, tmp_path):
        """Test loading from multiple YAML files in alphabetical order."""
        from ldf.utils.guardrail_loader import load_shared_guardrails

        shared_path = tmp_path / ".ldf-shared"
        guardrails_dir = shared_path / "guardrails"
        guardrails_dir.mkdir(parents=True)

        guardrails_dir.joinpath("a-rules.yaml").write_text("""
guardrails:
  - id: 1
    name: "From A"
""")
        guardrails_dir.joinpath("b-rules.yaml").write_text("""
guardrails:
  - id: 2
    name: "From B"
""")

        result = load_shared_guardrails(shared_path)

        assert len(result) == 2
        # Files loaded in sorted order
        assert result[0].name == "From A"
        assert result[1].name == "From B"


class TestMergeGuardrails:
    """Tests for _merge_guardrails function."""

    def test_overlay_overrides_base(self, tmp_path):
        """Test that overlay guardrails override base guardrails with same ID."""
        from ldf.utils.guardrail_loader import Guardrail, _merge_guardrails

        base = [
            Guardrail(id=1, name="Base Rule", description="Original", severity="low", enabled=True),
            Guardrail(
                id=2, name="Unchanged", description="Stays same", severity="medium", enabled=True
            ),
        ]

        overlay = [
            Guardrail(
                id=1,
                name="Overlay Rule",
                description="Updated",
                severity="high",
                enabled=False,
                checklist=["Check 1"],
            ),
        ]

        result = _merge_guardrails(base, overlay)

        # Should have 2 guardrails
        assert len(result) == 2

        # ID 1 should be updated
        merged_1 = next(g for g in result if g.id == 1)
        assert merged_1.enabled is False
        assert merged_1.checklist == ["Check 1"]

        # ID 2 should be unchanged
        merged_2 = next(g for g in result if g.id == 2)
        assert merged_2.name == "Unchanged"

    def test_overlay_adds_new_guardrails(self, tmp_path):
        """Test that overlay can add new guardrails not in base."""
        from ldf.utils.guardrail_loader import Guardrail, _merge_guardrails

        base = [
            Guardrail(id=1, name="Existing", description="", severity="medium", enabled=True),
        ]

        overlay = [
            Guardrail(
                id=100,
                name="New Rule",
                description="Added by overlay",
                severity="high",
                enabled=True,
            ),
        ]

        result = _merge_guardrails(base, overlay)

        assert len(result) == 2
        new_rule = next((g for g in result if g.id == 100), None)
        assert new_rule is not None
        assert new_rule.name == "New Rule"

    def test_overlay_updates_config(self, tmp_path):
        """Test that overlay config is merged into base config."""
        from ldf.utils.guardrail_loader import Guardrail, _merge_guardrails

        base = [
            Guardrail(
                id=1,
                name="Rule",
                description="",
                severity="medium",
                enabled=True,
                config={"threshold": 80, "key1": "original"},
            ),
        ]

        overlay = [
            Guardrail(
                id=1,
                name="Rule",
                description="",
                severity="medium",
                enabled=True,
                config={"threshold": 95, "key2": "new"},
            ),
        ]

        result = _merge_guardrails(base, overlay)

        merged = result[0]
        assert merged.config["threshold"] == 95  # Updated
        assert merged.config["key1"] == "original"  # Preserved
        assert merged.config["key2"] == "new"  # Added


class TestDetectSharedResourcesPath:
    """Tests for detect_shared_resources_path function."""

    def test_returns_none_when_no_workspace(self, tmp_path):
        """Test returns None when not in a workspace."""
        from ldf.utils.guardrail_loader import detect_shared_resources_path

        project = tmp_path / "standalone-project"
        project.mkdir()

        result = detect_shared_resources_path(project)

        assert result is None

    def test_finds_shared_resources_from_manifest(self, tmp_path):
        """Test finds shared resources path from workspace manifest."""
        from ldf.utils.guardrail_loader import detect_shared_resources_path

        # Create workspace
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        manifest = workspace / "ldf-workspace.yaml"
        manifest.write_text("""
version: "1.0"
name: test-workspace
projects:
  explicit: []
shared:
  path: .ldf-shared/
""")

        # Create shared resources directory
        shared = workspace / ".ldf-shared"
        shared.mkdir()

        # Create a project inside the workspace
        project = workspace / "services" / "api"
        project.mkdir(parents=True)

        result = detect_shared_resources_path(project)

        assert result == shared

    def test_finds_custom_shared_path(self, tmp_path):
        """Test finds custom shared path from manifest."""
        from ldf.utils.guardrail_loader import detect_shared_resources_path

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        manifest = workspace / "ldf-workspace.yaml"
        manifest.write_text("""
version: "1.0"
name: test-workspace
shared:
  path: shared-resources/
""")

        # Create custom shared directory
        shared = workspace / "shared-resources"
        shared.mkdir()

        result = detect_shared_resources_path(workspace)

        assert result == shared

    def test_returns_none_when_shared_dir_missing(self, tmp_path):
        """Test returns None when shared directory doesn't exist."""
        from ldf.utils.guardrail_loader import detect_shared_resources_path

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        manifest = workspace / "ldf-workspace.yaml"
        manifest.write_text("""
version: "1.0"
name: test-workspace
shared:
  path: .ldf-shared/
""")
        # Don't create the .ldf-shared directory

        result = detect_shared_resources_path(workspace)

        assert result is None

    def test_handles_malformed_manifest(self, tmp_path):
        """Test graceful fallback when manifest is malformed."""
        from ldf.utils.guardrail_loader import detect_shared_resources_path

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        manifest = workspace / "ldf-workspace.yaml"
        manifest.write_text("not: valid: yaml: [[[")

        # Create default shared dir as fallback
        shared = workspace / ".ldf-shared"
        shared.mkdir()

        result = detect_shared_resources_path(workspace)

        # Should fall back to default .ldf-shared
        assert result == shared


class TestLoadGuardrailsWithSharedResources:
    """Tests for load_guardrails with workspace shared resources."""

    def test_loads_shared_guardrails_in_workspace(self, tmp_path):
        """Test loading shared guardrails when in a workspace."""
        from ldf.utils.guardrail_loader import load_guardrails

        # Create workspace
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        manifest = workspace / "ldf-workspace.yaml"
        manifest.write_text("""
version: "1.0"
name: test-workspace
shared:
  path: .ldf-shared/
""")

        # Create shared guardrails
        shared = workspace / ".ldf-shared"
        shared_guardrails = shared / "guardrails"
        shared_guardrails.mkdir(parents=True)
        shared_guardrails.joinpath("team.yaml").write_text("""
guardrails:
  - id: 200
    name: "Shared Team Rule"
    severity: high
""")

        # Create project with guardrails config
        project = workspace / "api"
        project.mkdir()
        ldf_dir = project / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "guardrails.yaml").write_text("""
version: "1.0"
""")

        result = load_guardrails(project, shared_resources_path=shared)

        # Should have core guardrails + shared guardrail
        assert len(result) == 9
        shared_rule = next((g for g in result if g.id == 200), None)
        assert shared_rule is not None
        assert shared_rule.name == "Shared Team Rule"

    def test_disables_shared_guardrails_when_inherit_none(self, tmp_path):
        """Test that inherit_guardrails: none disables shared loading."""
        from ldf.utils.guardrail_loader import load_guardrails

        # Create shared resources with guardrails
        shared = tmp_path / ".ldf-shared"
        shared_guardrails = shared / "guardrails"
        shared_guardrails.mkdir(parents=True)
        shared_guardrails.joinpath("team.yaml").write_text("""
guardrails:
  - id: 200
    name: "Shared Rule"
""")

        # Create project that disables shared guardrails
        project = tmp_path / "project"
        ldf_dir = project / ".ldf"
        ldf_dir.mkdir(parents=True)
        (ldf_dir / "guardrails.yaml").write_text("""
version: "1.0"
workspace:
  inherit_guardrails: none
""")

        result = load_guardrails(project, shared_resources_path=shared)

        # Should only have core guardrails, not shared
        assert len(result) == 8
        assert not any(g.id == 200 for g in result)


class TestGetGuardrailByName:
    """Tests for get_guardrail_by_name function."""

    def test_finds_guardrail_by_name(self, temp_project: Path):
        """Test finding a guardrail by its name."""
        guardrail = get_guardrail_by_name("Testing Coverage", temp_project)

        assert guardrail is not None
        assert guardrail.name == "Testing Coverage"
        assert guardrail.id == 1

    def test_finds_guardrail_case_insensitive(self, temp_project: Path):
        """Test finding a guardrail with case-insensitive name."""
        guardrail = get_guardrail_by_name("testing coverage", temp_project)

        assert guardrail is not None
        assert guardrail.name == "Testing Coverage"

    def test_returns_none_for_unknown_name(self, temp_project: Path):
        """Test returning None for unknown name."""
        guardrail = get_guardrail_by_name("Nonexistent Guardrail", temp_project)

        assert guardrail is None

    def test_uses_cwd_when_project_root_is_none(self, temp_project: Path, monkeypatch):
        """Test using cwd when project_root is None."""
        monkeypatch.chdir(temp_project)

        guardrail = get_guardrail_by_name("Testing Coverage", None)

        assert guardrail is not None
