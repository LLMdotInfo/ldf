"""Tests for ldf.template_mgmt module."""

import os
import zipfile
from unittest.mock import patch

import pytest
import yaml


class TestExportTemplate:
    """Tests for export_template function."""

    def test_returns_false_when_no_ldf_dir(self, tmp_path, capsys):
        """Test returns False when .ldf directory doesn't exist."""
        from ldf.template_mgmt import export_template

        result = export_template(tmp_path)

        assert result is False
        captured = capsys.readouterr()
        assert "No .ldf/ directory found" in captured.out

    def test_dry_run_shows_preview(self, tmp_path, capsys):
        """Test dry-run mode shows preview without creating files."""
        from ldf.template_mgmt import export_template

        # Create minimal .ldf structure
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("project:\n  name: test")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        (ldf_dir / "templates").mkdir()
        (ldf_dir / "templates" / "requirements.md").write_text("# Req")
        (ldf_dir / "macros").mkdir()
        (ldf_dir / "question-packs").mkdir()

        result = export_template(tmp_path, dry_run=True)

        assert result is True
        captured = capsys.readouterr()
        assert "DRY RUN MODE" in captured.out
        assert "Template Export Preview" in captured.out
        # Output path shouldn't exist
        assert not (tmp_path / "template").exists()

    def test_dry_run_shows_missing_components(self, tmp_path, capsys):
        """Test dry-run shows missing components."""
        from ldf.template_mgmt import export_template

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("project:\n  name: test")
        # Only config exists

        result = export_template(tmp_path, dry_run=True)

        assert result is True
        captured = capsys.readouterr()
        assert "guardrails (not found)" in captured.out

    def test_exports_to_directory(self, tmp_path, capsys):
        """Test exporting to a directory."""
        from ldf.template_mgmt import export_template

        # Create .ldf structure
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("project:\n  name: my-project\n  version: '1.0'")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")
        templates_dir = ldf_dir / "templates"
        templates_dir.mkdir()
        (templates_dir / "requirements.md").write_text("# Requirements Template")

        output_dir = tmp_path / "output-template"

        # Mock the prompts
        with patch("ldf.template_mgmt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["my-template", "A test template", "1.0.0"]
            result = export_template(tmp_path, output_path=output_dir)

        assert result is True
        assert output_dir.exists()
        assert (output_dir / "template.yaml").exists()
        assert (output_dir / "config.yaml").exists()
        assert (output_dir / "guardrails.yaml").exists()
        assert (output_dir / "templates").exists()

        # Check template.yaml content
        template_meta = yaml.safe_load((output_dir / "template.yaml").read_text())
        assert template_meta["name"] == "my-template"
        assert template_meta["version"] == "1.0.0"

    def test_exports_to_zip(self, tmp_path, capsys):
        """Test exporting to a zip file."""
        from ldf.template_mgmt import export_template

        # Create .ldf structure
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("project:\n  name: my-project")
        (ldf_dir / "guardrails.yaml").write_text("guardrails: []")

        output_zip = tmp_path / "output" / "my-template.zip"

        with patch("ldf.template_mgmt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["my-template", "A test template", "1.0.0"]
            result = export_template(tmp_path, output_path=output_zip)

        assert result is True
        assert output_zip.exists()

        # Verify zip contents
        with zipfile.ZipFile(output_zip, "r") as zf:
            names = zf.namelist()
            assert "template.yaml" in names
            assert "config.yaml" in names

    def test_scrubs_config_by_default(self, tmp_path, capsys):
        """Test that config is scrubbed by default."""
        from ldf.template_mgmt import export_template

        # Create .ldf structure with project name
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("""
project:
  name: super-secret-project
  version: "1.0"
_checksums:
  some: hash
""")

        output_dir = tmp_path / "output-template"

        with patch("ldf.template_mgmt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["test", "", "1.0.0"]
            result = export_template(tmp_path, output_path=output_dir, include=["config"])

        assert result is True
        config_content = (output_dir / "config.yaml").read_text()
        config = yaml.safe_load(config_content)

        # Project name should be scrubbed
        assert config["project"]["name"] == "my-project"
        # Checksums should be removed
        assert "_checksums" not in config

    def test_no_scrub_preserves_config(self, tmp_path, capsys):
        """Test that scrub=False preserves original config."""
        from ldf.template_mgmt import export_template

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("""
project:
  name: my-original-project
""")

        output_dir = tmp_path / "output-template"

        with patch("ldf.template_mgmt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["test", "", "1.0.0"]
            result = export_template(
                tmp_path, output_path=output_dir, include=["config"], scrub=False
            )

        assert result is True
        config_content = (output_dir / "config.yaml").read_text()
        config = yaml.safe_load(config_content)

        # Original name should be preserved
        assert config["project"]["name"] == "my-original-project"

    def test_fails_on_symlinks(self, tmp_path, capsys):
        """Test fails when symlinks are detected."""
        from ldf.template_mgmt import export_template

        if os.name == "nt":
            pytest.skip("Symlink tests not supported on Windows")

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("project:\n  name: test")

        # Create symlink
        external = tmp_path / "external"
        external.mkdir()
        symlink = ldf_dir / "evil-link"
        symlink.symlink_to(external)

        result = export_template(tmp_path, dry_run=True)

        assert result is False
        captured = capsys.readouterr()
        assert "Symlinks detected" in captured.out

    def test_warns_on_secrets(self, tmp_path, capsys):
        """Test warns when potential secrets are detected."""
        from ldf.template_mgmt import export_template

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("api_key: sk-12345678901234567890")

        # Dry run should show warning
        export_template(tmp_path, dry_run=True)

        # Should still succeed in dry-run
        captured = capsys.readouterr()
        assert "Potential secrets detected" in captured.out

    def test_cancels_on_secret_confirmation_no(self, tmp_path, capsys):
        """Test cancels export when user declines secret warning."""
        from ldf.template_mgmt import export_template

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("password: super-secret-password-123")

        with (
            patch("ldf.template_mgmt.Prompt.ask") as mock_prompt,
            patch("ldf.template_mgmt.Confirm.ask") as mock_confirm,
        ):
            mock_prompt.side_effect = ["test", "", "1.0.0"]
            mock_confirm.return_value = False  # User declines

            result = export_template(tmp_path)

        assert result is False
        captured = capsys.readouterr()
        assert "Export cancelled" in captured.out


class TestGetComponentPath:
    """Tests for _get_component_path function."""

    def test_config_component(self, tmp_path):
        """Test config component returns config.yaml path."""
        from ldf.template_mgmt import _get_component_path

        ldf_dir = tmp_path / ".ldf"

        result = _get_component_path(ldf_dir, "config")
        assert result == ldf_dir / "config.yaml"

    def test_guardrails_component(self, tmp_path):
        """Test guardrails component returns guardrails.yaml path."""
        from ldf.template_mgmt import _get_component_path

        ldf_dir = tmp_path / ".ldf"

        result = _get_component_path(ldf_dir, "guardrails")
        assert result == ldf_dir / "guardrails.yaml"

    def test_templates_component(self, tmp_path):
        """Test templates component returns templates directory."""
        from ldf.template_mgmt import _get_component_path

        ldf_dir = tmp_path / ".ldf"

        result = _get_component_path(ldf_dir, "templates")
        assert result == ldf_dir / "templates"

    def test_macros_component(self, tmp_path):
        """Test macros component returns macros directory."""
        from ldf.template_mgmt import _get_component_path

        ldf_dir = tmp_path / ".ldf"

        result = _get_component_path(ldf_dir, "macros")
        assert result == ldf_dir / "macros"

    def test_question_packs_component(self, tmp_path):
        """Test question-packs component returns question-packs directory."""
        from ldf.template_mgmt import _get_component_path

        ldf_dir = tmp_path / ".ldf"

        result = _get_component_path(ldf_dir, "question-packs")
        assert result == ldf_dir / "question-packs"

    def test_unknown_component(self, tmp_path):
        """Test unknown component returns path relative to ldf_dir."""
        from ldf.template_mgmt import _get_component_path

        ldf_dir = tmp_path / ".ldf"

        result = _get_component_path(ldf_dir, "custom-component")
        assert result == ldf_dir / "custom-component"


class TestScrubConfig:
    """Tests for _scrub_config function."""

    def test_removes_project_name(self):
        """Test removes project name from config."""
        from ldf.template_mgmt import _scrub_config

        content = """
project:
  name: my-secret-project
  version: "1.0"
"""
        result = _scrub_config(content)
        config = yaml.safe_load(result)

        assert config["project"]["name"] == "my-project"
        assert config["project"]["version"] == "1.0"

    def test_removes_checksums(self):
        """Test removes _checksums from config."""
        from ldf.template_mgmt import _scrub_config

        content = """
project:
  name: test
_checksums:
  file1: abc123
  file2: def456
"""
        result = _scrub_config(content)
        config = yaml.safe_load(result)

        assert "_checksums" not in config

    def test_removes_template_metadata(self):
        """Test removes _template from config."""
        from ldf.template_mgmt import _scrub_config

        content = """
project:
  name: test
_template:
  source: some-template
  version: 1.0
"""
        result = _scrub_config(content)
        config = yaml.safe_load(result)

        assert "_template" not in config

    def test_handles_invalid_yaml(self):
        """Test returns original content on invalid YAML."""
        from ldf.template_mgmt import _scrub_config

        content = "not: valid: yaml: [["

        result = _scrub_config(content)

        assert result == content


class TestScanForSecrets:
    """Tests for _scan_for_secrets function."""

    def test_no_warnings_for_clean_files(self, tmp_path):
        """Test no warnings for files without secrets."""
        from ldf.template_mgmt import _scan_for_secrets

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("project:\n  name: test")

        warnings = _scan_for_secrets(ldf_dir, ["config"])

        assert warnings == []

    def test_warns_on_api_key(self, tmp_path):
        """Test warns when API key pattern detected."""
        from ldf.template_mgmt import _scan_for_secrets

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("api_key: sk-12345678901234567890")

        warnings = _scan_for_secrets(ldf_dir, ["config"])

        assert len(warnings) == 1
        assert "config.yaml" in warnings[0]

    def test_scans_directory_recursively(self, tmp_path):
        """Test scans all files in a directory."""
        from ldf.template_mgmt import _scan_for_secrets

        ldf_dir = tmp_path / ".ldf"
        templates_dir = ldf_dir / "templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "requirements.md").write_text("Normal content")
        (templates_dir / "design.md").write_text("password: secret123")

        warnings = _scan_for_secrets(ldf_dir, ["templates"])

        assert len(warnings) == 1
        assert "design.md" in warnings[0]

    def test_skips_missing_components(self, tmp_path):
        """Test skips components that don't exist."""
        from ldf.template_mgmt import _scan_for_secrets

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        warnings = _scan_for_secrets(ldf_dir, ["nonexistent"])

        assert warnings == []


class TestCheckSymlinks:
    """Tests for _check_symlinks function."""

    def test_no_warnings_for_regular_files(self, tmp_path):
        """Test no warnings when no symlinks exist."""
        from ldf.template_mgmt import _check_symlinks

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "config.yaml").write_text("test: value")
        (ldf_dir / "subdir").mkdir()
        (ldf_dir / "subdir" / "file.txt").write_text("content")

        warnings = _check_symlinks(ldf_dir)

        assert warnings == []

    def test_warns_on_symlink_file(self, tmp_path):
        """Test warns when symlink file detected."""
        from ldf.template_mgmt import _check_symlinks

        if os.name == "nt":
            pytest.skip("Symlink tests not supported on Windows")

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        external = tmp_path / "external.txt"
        external.write_text("external content")
        (ldf_dir / "link.txt").symlink_to(external)

        warnings = _check_symlinks(ldf_dir)

        assert len(warnings) == 1
        assert "link.txt" in warnings[0]

    def test_warns_on_symlink_directory(self, tmp_path):
        """Test warns when symlink directory detected."""
        from ldf.template_mgmt import _check_symlinks

        if os.name == "nt":
            pytest.skip("Symlink tests not supported on Windows")

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        external_dir = tmp_path / "external"
        external_dir.mkdir()
        (ldf_dir / "link-dir").symlink_to(external_dir)

        warnings = _check_symlinks(ldf_dir)

        assert len(warnings) == 1
        assert "link-dir" in warnings[0]


class TestScanFileForSecrets:
    """Tests for _scan_file_for_secrets function."""

    def test_handles_binary_files(self, tmp_path):
        """Test gracefully handles binary files."""
        from ldf.template_mgmt import _scan_file_for_secrets

        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\xff\xfe")

        warnings = []
        _scan_file_for_secrets(binary_file, warnings)

        # Should not crash, may or may not add warnings depending on encoding
        assert isinstance(warnings, list)
