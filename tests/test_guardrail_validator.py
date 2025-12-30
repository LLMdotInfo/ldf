"""Tests for ldf._mcp_servers.coverage_reporter.guardrail_validator module."""

from pathlib import Path
from unittest.mock import patch


class TestGuardrailCoverageValidator:
    """Tests for GuardrailCoverageValidator class."""

    def test_loads_guardrails_successfully(self, temp_project: Path):
        """Test loading guardrails from a valid project."""
        from ldf._mcp_servers.coverage_reporter.guardrail_validator import (
            GuardrailCoverageValidator,
        )

        validator = GuardrailCoverageValidator(temp_project)
        # Use get_guardrail_name which internally calls _load_guardrails
        name = validator.get_guardrail_name(1)

        # Should return a valid name (either from config or default)
        assert isinstance(name, str)
        assert len(name) > 0

    def test_falls_back_to_defaults_on_yaml_error(self, temp_project: Path):
        """Test that YAML errors in guardrails.yaml fall back to defaults gracefully."""
        from ldf._mcp_servers.coverage_reporter.guardrail_validator import (
            GuardrailCoverageValidator,
        )

        # Write invalid YAML to guardrails file
        guardrails_file = temp_project / ".ldf" / "guardrails.yaml"
        guardrails_file.write_text("invalid: yaml: content: [")

        validator = GuardrailCoverageValidator(temp_project)
        # Should not crash - falls back to defaults
        name = validator.get_guardrail_name(1)

        # Should return the default name for guardrail 1
        assert isinstance(name, str)
        assert "Testing" in name or len(name) > 0

    def test_falls_back_to_defaults_on_missing_file(self, tmp_path: Path):
        """Test that missing guardrails.yaml falls back to defaults gracefully."""
        from ldf._mcp_servers.coverage_reporter.guardrail_validator import (
            GuardrailCoverageValidator,
        )

        # Create minimal LDF structure without guardrails
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        validator = GuardrailCoverageValidator(tmp_path)
        # Should not crash - falls back to defaults
        name = validator.get_guardrail_name(1)

        # Should return the default name
        assert isinstance(name, str)
        assert len(name) > 0

    def test_falls_back_to_defaults_on_loader_exception(self, temp_project: Path):
        """Test that exceptions from get_active_guardrails fall back to defaults."""
        from ldf._mcp_servers.coverage_reporter.guardrail_validator import (
            GuardrailCoverageValidator,
        )

        # Mock get_active_guardrails to raise an exception
        with patch(
            "ldf._mcp_servers.coverage_reporter.guardrail_validator.get_active_guardrails"
        ) as mock_loader:
            mock_loader.side_effect = RuntimeError("Test error")

            validator = GuardrailCoverageValidator(temp_project)
            # Should not crash - falls back to defaults
            name = validator.get_guardrail_name(1)

            # Should return the default name
            assert isinstance(name, str)
            assert "Testing" in name

    def test_caches_guardrails(self, temp_project: Path):
        """Test that guardrails are cached after first load."""
        from ldf._mcp_servers.coverage_reporter.guardrail_validator import (
            GuardrailCoverageValidator,
        )

        validator = GuardrailCoverageValidator(temp_project)

        # First call loads guardrails via _load_guardrails
        _ = validator.get_guardrail_name(1)
        guardrails1 = validator._guardrails
        # Second call should use cached value
        _ = validator.get_guardrail_name(2)
        guardrails2 = validator._guardrails

        assert guardrails1 is guardrails2  # Same object (cached)
