"""Tests for LDF update functionality."""


import pytest

from ldf import __version__
from ldf.init import FRAMEWORK_DIR, compute_file_checksum, initialize_project
from ldf.update import (
    UpdateDiff,
    apply_updates,
    check_for_updates,
    get_update_diff,
    load_project_config,
    save_project_config,
)


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with LDF initialized."""
    project_root = tmp_path / "test-project"
    project_root.mkdir()

    # Initialize LDF in non-interactive mode
    initialize_project(
        project_path=project_root,
        preset="custom",
        question_packs=["security", "testing"],
        mcp_servers=["spec-inspector"],
        non_interactive=True,
    )

    return project_root


@pytest.fixture
def temp_project_old_version(temp_project):
    """Create a project with an older framework version."""
    config = load_project_config(temp_project)
    config["framework_version"] = "0.0.1"
    save_project_config(temp_project, config)
    return temp_project


class TestCheckForUpdates:
    """Tests for check_for_updates()."""

    def test_check_detects_version_difference(self, temp_project_old_version):
        """Should detect when framework version differs from project version."""
        info = check_for_updates(temp_project_old_version)

        assert info.current_version == "0.0.1"
        assert info.latest_version == __version__
        assert info.has_updates is True

    def test_check_reports_no_updates_when_current(self, temp_project):
        """Should report no updates when versions match."""
        info = check_for_updates(temp_project)

        assert info.current_version == __version__
        assert info.latest_version == __version__
        assert info.has_updates is False

    def test_check_lists_updatable_components(self, temp_project):
        """Should list all updatable components."""
        info = check_for_updates(temp_project)

        assert "templates" in info.updatable_components
        assert "macros" in info.updatable_components
        assert "question-packs" in info.updatable_components


class TestGetUpdateDiff:
    """Tests for get_update_diff()."""

    def test_dry_run_shows_unchanged_files(self, temp_project):
        """Should show files as unchanged when they match framework."""
        diff = get_update_diff(temp_project)

        # Templates should show as unchanged since they were just copied
        unchanged_templates = [p for p in diff.files_unchanged if "templates/" in p]
        assert len(unchanged_templates) > 0

    def test_dry_run_detects_modified_templates(self, temp_project):
        """Should detect when template files have been modified."""
        # Modify a template
        template_path = temp_project / ".ldf" / "templates" / "requirements.md"
        original_content = template_path.read_text()
        template_path.write_text(original_content + "\n\n# Custom addition")

        diff = get_update_diff(temp_project, components=["templates"])

        # Should show the modified template as needing update
        update_paths = [c.path for c in diff.files_to_update]
        assert "templates/requirements.md" in update_paths

    def test_detects_user_modified_question_packs(self, temp_project):
        """Should detect when user has modified a question pack."""
        # Get the config with checksums
        config = load_project_config(temp_project)
        _original_checksums = config.get("_checksums", {})  # noqa: F841 - stored for reference

        # Modify the security question pack
        pack_path = temp_project / ".ldf" / "question-packs" / "security.yaml"
        original_content = pack_path.read_text()
        pack_path.write_text(original_content + "\n\n# User customization")

        # Now simulate a framework update by changing the checksum expectation
        # (In real usage, the framework source would have changed)
        # For testing, we modify the stored checksum to something different
        config["_checksums"]["question-packs/security.yaml"] = "fake_old_checksum"
        save_project_config(temp_project, config)

        diff = get_update_diff(temp_project, components=["question-packs"])

        # Should show as a conflict since checksum doesn't match
        conflict_paths = [c.file_path for c in diff.conflicts]
        assert "question-packs/security.yaml" in conflict_paths

    def test_filters_by_component(self, temp_project):
        """Should only show changes for specified components."""
        diff = get_update_diff(temp_project, components=["templates"])

        # Should only have templates-related paths
        all_paths = (
            [c.path for c in diff.files_to_update]
            + [c.path for c in diff.files_to_add]
            + diff.files_unchanged
        )

        for path in all_paths:
            assert path.startswith("templates/"), f"Unexpected path: {path}"


class TestApplyUpdates:
    """Tests for apply_updates()."""

    def test_update_replaces_templates(self, temp_project):
        """Should replace template files with framework versions."""
        # Modify a template
        template_path = temp_project / ".ldf" / "templates" / "design.md"
        template_path.write_text("# Modified template\n")

        result = apply_updates(temp_project, components=["templates"])

        assert result.success is True
        assert any("templates/design.md" in f for f in result.files_updated)

        # Verify content matches framework
        framework_content = (FRAMEWORK_DIR / "templates" / "design.md").read_text()
        updated_content = template_path.read_text()
        assert updated_content == framework_content

    def test_update_replaces_macros(self, temp_project):
        """Should replace macro files with framework versions."""
        # Modify a macro
        macro_path = temp_project / ".ldf" / "macros" / "clarify-first.md"
        macro_path.write_text("# Modified macro\n")

        result = apply_updates(temp_project, components=["macros"])

        assert result.success is True
        assert any("macros/clarify-first.md" in f for f in result.files_updated)

    def test_update_preserves_modified_question_packs_when_skipped(self, temp_project):
        """Should preserve user-modified question packs when skip is chosen."""
        # Modify a question pack
        pack_path = temp_project / ".ldf" / "question-packs" / "security.yaml"
        custom_content = "# My custom security questions\n"
        pack_path.write_text(custom_content)

        # Simulate a framework update scenario by changing the stored checksum
        config = load_project_config(temp_project)
        config["_checksums"]["question-packs/security.yaml"] = "old_checksum"
        save_project_config(temp_project, config)

        # Apply with skip resolution
        result = apply_updates(
            temp_project,
            components=["question-packs"],
            conflict_resolutions={"question-packs/security.yaml": "skip"},
        )

        assert result.success is True
        # Content should be preserved
        assert pack_path.read_text() == custom_content

    def test_update_overwrites_when_use_framework(self, temp_project):
        """Should overwrite user changes when use_framework is chosen."""
        # Modify a question pack
        pack_path = temp_project / ".ldf" / "question-packs" / "security.yaml"
        pack_path.write_text("# My custom security questions\n")

        # Simulate a framework update scenario
        config = load_project_config(temp_project)
        config["_checksums"]["question-packs/security.yaml"] = "old_checksum"
        save_project_config(temp_project, config)

        # Apply with use_framework resolution
        result = apply_updates(
            temp_project,
            components=["question-packs"],
            conflict_resolutions={"question-packs/security.yaml": "use_framework"},
        )

        assert result.success is True
        # Content should match framework
        framework_content = (
            FRAMEWORK_DIR / "question-packs" / "core" / "security.yaml"
        ).read_text()
        assert pack_path.read_text() == framework_content

    def test_update_updates_version_in_config(self, temp_project_old_version):
        """Should update framework_version in config after successful update."""
        result = apply_updates(temp_project_old_version)

        assert result.success is True

        config = load_project_config(temp_project_old_version)
        assert config["framework_version"] == __version__
        assert "framework_updated" in config

    def test_update_never_touches_specs(self, temp_project):
        """Should never modify files in specs/ directory."""
        # Create a spec
        spec_dir = temp_project / ".ldf" / "specs" / "test-feature"
        spec_dir.mkdir(parents=True)
        req_file = spec_dir / "requirements.md"
        custom_content = "# My custom spec\n"
        req_file.write_text(custom_content)

        _result = apply_updates(temp_project)

        # Spec should be untouched
        assert req_file.read_text() == custom_content

    def test_update_never_touches_answerpacks(self, temp_project):
        """Should never modify files in answerpacks/ directory."""
        # Create an answerpack
        answerpack_dir = temp_project / ".ldf" / "answerpacks" / "test-feature"
        answerpack_dir.mkdir(parents=True)
        answers_file = answerpack_dir / "security.yaml"
        custom_content = "answers:\n  - question: test\n    answer: yes\n"
        answers_file.write_text(custom_content)

        _result = apply_updates(temp_project)

        # Answerpack should be untouched
        assert answers_file.read_text() == custom_content

    def test_update_with_only_flag(self, temp_project):
        """Should only update specified components."""
        # Modify both templates and macros
        template_path = temp_project / ".ldf" / "templates" / "design.md"
        macro_path = temp_project / ".ldf" / "macros" / "clarify-first.md"

        template_path.write_text("# Modified\n")
        macro_path.write_text("# Modified\n")

        # Only update templates
        _result = apply_updates(temp_project, components=["templates"])

        # Template should be updated
        framework_template = (FRAMEWORK_DIR / "templates" / "design.md").read_text()
        assert template_path.read_text() == framework_template

        # Macro should still be modified
        assert macro_path.read_text() == "# Modified\n"

    def test_update_dry_run_does_not_modify(self, temp_project):
        """Dry run should not modify any files."""
        # Modify a template
        template_path = temp_project / ".ldf" / "templates" / "design.md"
        modified_content = "# Modified template\n"
        template_path.write_text(modified_content)

        _result = apply_updates(temp_project, dry_run=True)

        # File should not be changed
        assert template_path.read_text() == modified_content


class TestChecksums:
    """Tests for checksum functionality."""

    def test_update_stores_checksums_on_init(self, temp_project):
        """Init should store checksums for question packs."""
        config = load_project_config(temp_project)

        assert "_checksums" in config
        assert "question-packs/security.yaml" in config["_checksums"]
        assert "question-packs/testing.yaml" in config["_checksums"]

    def test_checksums_match_file_content(self, temp_project):
        """Stored checksums should match actual file content."""
        config = load_project_config(temp_project)
        checksums = config.get("_checksums", {})

        for relative_path, stored_checksum in checksums.items():
            file_path = temp_project / ".ldf" / relative_path
            if file_path.exists():
                actual_checksum = compute_file_checksum(file_path)
                assert actual_checksum == stored_checksum, f"Checksum mismatch for {relative_path}"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_project_without_version_tracking(self, temp_project):
        """Should handle projects initialized before version tracking."""
        # Remove version tracking fields
        config = load_project_config(temp_project)
        config.pop("framework_version", None)
        config.pop("framework_updated", None)
        config.pop("_checksums", None)
        save_project_config(temp_project, config)

        info = check_for_updates(temp_project)

        assert info.current_version == "0.0.0"
        assert info.has_updates is True

    def test_missing_framework_file_handled(self, temp_project):
        """Should handle missing framework files gracefully."""
        # This is mainly a defensive test - framework files should always exist
        diff = get_update_diff(temp_project)
        # Should complete without error
        assert isinstance(diff, UpdateDiff)

    def test_empty_project_directory(self, tmp_path):
        """Should handle project with no .ldf directory."""
        project_root = tmp_path / "empty-project"
        project_root.mkdir()

        info = check_for_updates(project_root)

        # Should return empty/default values without crashing
        assert info.current_version == "0.0.0"
        assert info.updatable_components == []
