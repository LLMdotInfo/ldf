"""Tests for ldf.utils.guardrail_loader module."""

import pytest
from pathlib import Path

from ldf.utils.guardrail_loader import (
    get_active_guardrails,
    load_core_guardrails,
    load_preset_guardrails,
    load_guardrails,
    Guardrail,
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
