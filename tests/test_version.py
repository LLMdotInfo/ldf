"""Tests for ldf.__init__ version handling."""

from unittest.mock import patch


class TestVersionImport:
    """Tests for __version__ import."""

    def test_version_from_metadata(self):
        """Test that __version__ is read from package metadata."""
        from ldf import __version__

        # Should be a valid version string (not the fallback)
        assert __version__ != "0.0.0.dev"
        assert isinstance(__version__, str)
        # Should have version-like format
        assert "." in __version__

    def test_version_fallback_on_package_not_found(self):
        """Test that __version__ falls back when package is not installed."""
        from importlib.metadata import PackageNotFoundError

        # Mock version() to raise PackageNotFoundError
        with patch("importlib.metadata.version") as mock_version:
            mock_version.side_effect = PackageNotFoundError("llm-ldf")

            # Re-import the module to trigger the fallback
            import importlib

            import ldf

            importlib.reload(ldf)

            # Should use fallback version
            assert ldf.__version__ == "0.0.0.dev"

            # Reload again to restore normal behavior
            mock_version.side_effect = None
            mock_version.return_value = "1.2.0"
            importlib.reload(ldf)
