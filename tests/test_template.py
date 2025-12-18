"""Tests for ldf.template module."""

import zipfile
from pathlib import Path

import pytest
import yaml

from ldf.template import (
    TemplateMetadata,
    VerifyResult,
    _check_version_compatible,
    _find_template_root,
    _scan_for_secrets,
    _validate_yaml_files,
    import_template,
    print_verify_result,
    verify_template,
)


@pytest.fixture
def valid_template(tmp_path: Path) -> Path:
    """Create a valid template directory."""
    template_dir = tmp_path / "valid-template"
    template_dir.mkdir()

    # Create template.yaml
    metadata = template_dir / "template.yaml"
    metadata.write_text("""name: test-template
version: 1.0.0
ldf_version: "0.1.0"
description: Test template for unit tests
components:
  - config
  - guardrails
""")

    # Create .ldf directory with config
    ldf_dir = template_dir / ".ldf"
    ldf_dir.mkdir()

    config = ldf_dir / "config.yaml"
    config.write_text("""version: "1.0"
project:
  name: template-project
guardrails:
  preset: core
""")

    guardrails = ldf_dir / "guardrails.yaml"
    guardrails.write_text("""version: "1.0"
extends: core
""")

    # Create question-packs directory
    packs_dir = ldf_dir / "question-packs"
    packs_dir.mkdir()

    return template_dir


@pytest.fixture
def valid_template_zip(valid_template: Path, tmp_path: Path) -> Path:
    """Create a valid template zip file."""
    zip_path = tmp_path / "template.zip"

    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in valid_template.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(valid_template)
                zf.write(file, arcname)

    return zip_path


class TestVerifyTemplate:
    """Tests for verify_template function."""

    def test_verifies_valid_template(self, valid_template: Path):
        """Test verifying a valid template."""
        result = verify_template(valid_template)

        assert result.valid is True
        assert len(result.errors) == 0
        assert result.metadata is not None
        assert result.metadata.name == "test-template"
        assert result.metadata.version == "1.0.0"

    def test_verifies_valid_zip_template(self, valid_template_zip: Path):
        """Test verifying a valid zip template."""
        result = verify_template(valid_template_zip)

        assert result.valid is True
        assert result.metadata is not None

    def test_fails_without_template_yaml(self, tmp_path: Path):
        """Test failure when template.yaml is missing."""
        template_dir = tmp_path / "bad-template"
        template_dir.mkdir()

        result = verify_template(template_dir)

        assert result.valid is False
        assert "template.yaml not found" in result.errors

    def test_fails_with_missing_name(self, tmp_path: Path):
        """Test failure when name field is missing."""
        template_dir = tmp_path / "bad-template"
        template_dir.mkdir()

        metadata = template_dir / "template.yaml"
        metadata.write_text("""version: 1.0.0
ldf_version: "0.1.0"
""")

        result = verify_template(template_dir)

        assert result.valid is False
        assert any("missing 'name'" in e for e in result.errors)

    def test_fails_with_missing_version(self, tmp_path: Path):
        """Test failure when version field is missing."""
        template_dir = tmp_path / "bad-template"
        template_dir.mkdir()

        metadata = template_dir / "template.yaml"
        metadata.write_text("""name: test
ldf_version: "0.1.0"
""")

        result = verify_template(template_dir)

        assert result.valid is False
        assert any("missing 'version'" in e for e in result.errors)

    def test_fails_with_missing_ldf_version(self, tmp_path: Path):
        """Test failure when ldf_version field is missing."""
        template_dir = tmp_path / "bad-template"
        template_dir.mkdir()

        metadata = template_dir / "template.yaml"
        metadata.write_text("""name: test
version: 1.0.0
""")

        result = verify_template(template_dir)

        assert result.valid is False
        assert any("missing 'ldf_version'" in e for e in result.errors)

    def test_fails_with_specs_directory(self, valid_template: Path):
        """Test failure when specs directory is included."""
        specs_dir = valid_template / ".ldf" / "specs"
        specs_dir.mkdir()
        (specs_dir / "test.md").write_text("# Test")

        result = verify_template(valid_template)

        assert result.valid is False
        assert any("specs" in e for e in result.errors)

    def test_fails_with_answerpacks_directory(self, valid_template: Path):
        """Test failure when answerpacks directory is included."""
        packs_dir = valid_template / ".ldf" / "answerpacks"
        packs_dir.mkdir()
        (packs_dir / "test.yaml").write_text("key: value")

        result = verify_template(valid_template)

        assert result.valid is False
        assert any("answerpacks" in e for e in result.errors)

    def test_fails_with_invalid_zip(self, tmp_path: Path):
        """Test failure with invalid zip file."""
        bad_zip = tmp_path / "bad.zip"
        bad_zip.write_text("not a zip file")

        result = verify_template(bad_zip)

        assert result.valid is False
        assert any("Invalid zip" in e for e in result.errors)

    def test_fails_with_empty_zip(self, tmp_path: Path):
        """Test failure with zip that has no template.yaml."""
        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("readme.txt", "No template here")

        result = verify_template(zip_path)

        assert result.valid is False
        assert any("No template.yaml" in e for e in result.errors)

    def test_fails_with_invalid_yaml(self, tmp_path: Path):
        """Test failure when template.yaml has invalid YAML."""
        template_dir = tmp_path / "bad-template"
        template_dir.mkdir()

        metadata = template_dir / "template.yaml"
        metadata.write_text("invalid: yaml: [[[")

        result = verify_template(template_dir)

        assert result.valid is False
        assert any("invalid YAML" in e for e in result.errors)

    def test_warns_on_version_mismatch(self, tmp_path: Path):
        """Test warning when LDF version doesn't match."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()

        metadata = template_dir / "template.yaml"
        metadata.write_text("""name: test
version: 1.0.0
ldf_version: "99.0.0"
""")

        result = verify_template(template_dir)

        # Should still be valid but have warning
        assert any("99.0.0" in w for w in result.warnings)


class TestImportTemplate:
    """Tests for import_template function."""

    def test_imports_valid_template(self, valid_template: Path, tmp_path: Path):
        """Test importing a valid template."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = import_template(valid_template, project_root)

        assert result is True
        assert (project_root / ".ldf").exists()
        assert (project_root / ".ldf" / "config.yaml").exists()

    def test_imports_zip_template(self, valid_template_zip: Path, tmp_path: Path):
        """Test importing a zip template."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = import_template(valid_template_zip, project_root)

        assert result is True
        assert (project_root / ".ldf").exists()

    def test_fails_if_ldf_exists(self, valid_template: Path, tmp_path: Path):
        """Test failure when .ldf already exists."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".ldf").mkdir()

        result = import_template(valid_template, project_root, force=False)

        assert result is False

    def test_overwrites_with_force(self, valid_template: Path, tmp_path: Path):
        """Test overwriting existing .ldf with force flag."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        ldf_dir = project_root / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "old-file.txt").write_text("old content")

        result = import_template(valid_template, project_root, force=True)

        assert result is True
        # Old file should be backed up, not in new .ldf
        assert not (ldf_dir / "old-file.txt").exists()

    def test_creates_backup_with_force(self, valid_template: Path, tmp_path: Path):
        """Test that backup is created when using force."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        ldf_dir = project_root / ".ldf"
        ldf_dir.mkdir()

        result = import_template(valid_template, project_root, force=True)

        assert result is True
        # Should have a backup directory
        backups = list(project_root.glob(".ldf.backup.*"))
        assert len(backups) == 1

    def test_tracks_template_in_config(self, valid_template: Path, tmp_path: Path):
        """Test that template tracking info is added to config."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = import_template(valid_template, project_root)

        assert result is True

        config_path = project_root / ".ldf" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "template" in config
        assert config["template"]["name"] == "test-template"
        assert config["template"]["version"] == "1.0.0"

    def test_creates_required_directories(self, valid_template: Path, tmp_path: Path):
        """Test that required directories are created."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = import_template(valid_template, project_root)

        assert result is True
        ldf_dir = project_root / ".ldf"
        assert (ldf_dir / "specs").exists()
        assert (ldf_dir / "answerpacks").exists()
        assert (ldf_dir / "templates").exists()
        assert (ldf_dir / "question-packs").exists()
        assert (ldf_dir / "macros").exists()

    def test_fails_with_invalid_template(self, tmp_path: Path):
        """Test failure when template is invalid."""
        template_dir = tmp_path / "bad-template"
        template_dir.mkdir()
        # No template.yaml

        project_root = tmp_path / "project"
        project_root.mkdir()

        result = import_template(template_dir, project_root)

        assert result is False


class TestFindTemplateRoot:
    """Tests for _find_template_root function."""

    def test_finds_template_at_root(self, tmp_path: Path):
        """Test finding template.yaml at root."""
        (tmp_path / "template.yaml").write_text("name: test")

        result = _find_template_root(tmp_path)

        assert result == tmp_path

    def test_finds_template_in_subdirectory(self, tmp_path: Path):
        """Test finding template.yaml in subdirectory."""
        subdir = tmp_path / "my-template"
        subdir.mkdir()
        (subdir / "template.yaml").write_text("name: test")

        result = _find_template_root(tmp_path)

        assert result == subdir

    def test_returns_none_when_not_found(self, tmp_path: Path):
        """Test returning None when no template.yaml exists."""
        result = _find_template_root(tmp_path)

        assert result is None


class TestCheckVersionCompatible:
    """Tests for _check_version_compatible function."""

    def test_same_version_compatible(self):
        """Test that same version is compatible."""
        assert _check_version_compatible("0.1.0", "0.1.0") is True

    def test_different_patch_compatible(self):
        """Test that different patch versions are compatible."""
        assert _check_version_compatible("0.1.0", "0.1.5") is True

    def test_higher_minor_compatible(self):
        """Test that template with lower minor version is compatible."""
        assert _check_version_compatible("0.1.0", "0.2.0") is True

    def test_lower_current_minor_incompatible(self):
        """Test that template with higher minor version is incompatible."""
        assert _check_version_compatible("0.2.0", "0.1.0") is False

    def test_different_major_incompatible(self):
        """Test that different major versions are incompatible."""
        assert _check_version_compatible("1.0.0", "0.1.0") is False
        assert _check_version_compatible("0.1.0", "1.0.0") is False

    def test_handles_v_prefix(self):
        """Test handling version with v prefix."""
        assert _check_version_compatible("v0.1.0", "v0.1.0") is True

    def test_handles_invalid_version(self):
        """Test handling invalid version strings."""
        # Should return True (allow) if parsing fails
        assert _check_version_compatible("invalid", "0.1.0") is True
        assert _check_version_compatible("0.1.0", "invalid") is True


class TestValidateYamlFiles:
    """Tests for _validate_yaml_files function."""

    def test_validates_valid_yaml(self, valid_template: Path):
        """Test validating valid YAML files."""
        errors = _validate_yaml_files(valid_template)

        assert len(errors) == 0

    def test_detects_invalid_yaml(self, tmp_path: Path):
        """Test detecting invalid YAML files."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()
        ldf_dir = template_dir / ".ldf"
        ldf_dir.mkdir()

        bad_yaml = ldf_dir / "bad.yaml"
        bad_yaml.write_text("invalid: yaml: [[[")

        errors = _validate_yaml_files(template_dir)

        assert len(errors) == 1
        assert "bad.yaml" in errors[0]

    def test_handles_missing_ldf_dir(self, tmp_path: Path):
        """Test handling when .ldf directory doesn't exist."""
        errors = _validate_yaml_files(tmp_path)

        assert len(errors) == 0


class TestScanForSecrets:
    """Tests for _scan_for_secrets function."""

    def test_detects_api_key(self, tmp_path: Path):
        """Test detecting potential API key."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()
        ldf_dir = template_dir / ".ldf"
        ldf_dir.mkdir()

        config = ldf_dir / "config.yaml"
        # Use a 20+ character string after api_key: to match the regex pattern
        config.write_text("api-key: abcdefghij1234567890abcd")

        warnings = _scan_for_secrets(template_dir)

        assert len(warnings) == 1
        assert "API key" in warnings[0]

    def test_detects_password(self, tmp_path: Path):
        """Test detecting potential password."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()
        ldf_dir = template_dir / ".ldf"
        ldf_dir.mkdir()

        config = ldf_dir / "config.yaml"
        config.write_text("password: my-secret-password")

        warnings = _scan_for_secrets(template_dir)

        assert len(warnings) == 1
        assert "password" in warnings[0].lower()

    def test_detects_private_key(self, tmp_path: Path):
        """Test detecting private key."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()
        ldf_dir = template_dir / ".ldf"
        ldf_dir.mkdir()

        config = ldf_dir / "config.yaml"
        config.write_text("key: |\n  -----BEGIN RSA PRIVATE KEY-----\n  content\n")

        warnings = _scan_for_secrets(template_dir)

        assert len(warnings) == 1
        assert "Private key" in warnings[0]

    def test_handles_clean_template(self, valid_template: Path):
        """Test handling template without secrets."""
        warnings = _scan_for_secrets(valid_template)

        assert len(warnings) == 0

    def test_handles_missing_ldf_dir(self, tmp_path: Path):
        """Test handling when .ldf directory doesn't exist."""
        warnings = _scan_for_secrets(tmp_path)

        assert len(warnings) == 0


class TestVerifyResult:
    """Tests for VerifyResult dataclass."""

    def test_to_dict_with_metadata(self):
        """Test converting result with metadata to dict."""
        metadata = TemplateMetadata(
            name="test",
            version="1.0.0",
            ldf_version="0.1.0",
            description="Test",
        )
        result = VerifyResult(
            valid=True,
            metadata=metadata,
            warnings=["Warning 1"],
        )

        d = result.to_dict()

        assert d["valid"] is True
        assert d["metadata"]["name"] == "test"
        assert d["metadata"]["version"] == "1.0.0"
        assert d["warnings"] == ["Warning 1"]

    def test_to_dict_without_metadata(self):
        """Test converting result without metadata to dict."""
        result = VerifyResult(
            valid=False,
            errors=["Error 1"],
        )

        d = result.to_dict()

        assert d["valid"] is False
        assert d["metadata"] is None
        assert d["errors"] == ["Error 1"]


class TestPrintVerifyResult:
    """Tests for print_verify_result function."""

    def test_prints_valid_result(self, valid_template: Path, capsys):
        """Test printing a valid verification result."""
        result = verify_template(valid_template)

        print_verify_result(result, valid_template)

        captured = capsys.readouterr()
        assert "Template Verification" in captured.out
        assert "test-template" in captured.out

    def test_prints_invalid_result(self, tmp_path: Path, capsys):
        """Test printing an invalid verification result."""
        template_dir = tmp_path / "bad"
        template_dir.mkdir()

        result = verify_template(template_dir)

        print_verify_result(result, template_dir)

        captured = capsys.readouterr()
        assert "Errors:" in captured.out
        assert "template.yaml not found" in captured.out

    def test_prints_warnings(self, tmp_path: Path, capsys):
        """Test printing result with warnings."""
        template_dir = tmp_path / "template"
        template_dir.mkdir()

        metadata = template_dir / "template.yaml"
        metadata.write_text("""name: test
version: 1.0.0
ldf_version: "99.0.0"
""")

        result = verify_template(template_dir)

        print_verify_result(result, template_dir)

        captured = capsys.readouterr()
        assert "Warnings:" in captured.out
