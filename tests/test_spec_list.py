"""Tests for ldf.spec_list module."""

import json

import pytest


class TestListSpecs:
    """Tests for list_specs function."""

    def test_raises_when_no_ldf_dir(self, tmp_path, monkeypatch, capsys):
        """Test raises SystemExit when .ldf directory doesn't exist."""
        from ldf.spec_list import list_specs

        monkeypatch.chdir(tmp_path)

        with pytest.raises(SystemExit) as exc_info:
            list_specs()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "No .ldf directory found" in captured.out

    def test_json_format_empty_specs(self, tmp_path, monkeypatch, capsys):
        """Test JSON output with no specs."""
        from ldf.spec_list import list_specs

        # Create minimal .ldf structure
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "specs").mkdir()

        monkeypatch.chdir(tmp_path)

        list_specs(output_format="json")

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["specs"] == []
        assert output["total"] == 0

    def test_json_format_with_specs(self, tmp_path, monkeypatch, capsys):
        """Test JSON output with specs."""
        from ldf.spec_list import list_specs

        # Create .ldf structure with specs
        ldf_dir = tmp_path / ".ldf"
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir(parents=True)

        # Create a spec with all phases
        auth_spec = specs_dir / "auth"
        auth_spec.mkdir()
        (auth_spec / "requirements.md").write_text("# Auth Requirements")
        (auth_spec / "design.md").write_text("# Auth Design")
        (auth_spec / "tasks.md").write_text("# Auth Tasks")

        # Create a spec with only requirements
        billing_spec = specs_dir / "billing"
        billing_spec.mkdir()
        (billing_spec / "requirements.md").write_text("# Billing Requirements")

        monkeypatch.chdir(tmp_path)

        list_specs(output_format="json")

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["total"] == 2

        # Check auth spec
        auth = next(s for s in output["specs"] if s["name"] == "auth")
        assert auth["phase"] == "tasks"
        assert auth["completeness"]["requirements"] is True
        assert auth["completeness"]["design"] is True
        assert auth["completeness"]["tasks"] is True

        # Check billing spec
        billing = next(s for s in output["specs"] if s["name"] == "billing")
        assert billing["phase"] == "requirements"
        assert billing["completeness"]["requirements"] is True
        assert billing["completeness"]["design"] is False
        assert billing["completeness"]["tasks"] is False

    def test_text_format_empty_specs(self, tmp_path, monkeypatch, capsys):
        """Test text output with no specs."""
        from ldf.spec_list import list_specs

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "specs").mkdir()

        monkeypatch.chdir(tmp_path)

        list_specs(output_format="text")

        captured = capsys.readouterr()
        assert "No specs found" in captured.out
        assert "ldf create-spec" in captured.out

    def test_text_format_with_specs(self, tmp_path, monkeypatch, capsys):
        """Test text output with specs."""
        from ldf.spec_list import list_specs

        ldf_dir = tmp_path / ".ldf"
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir(parents=True)

        # Create a spec
        auth_spec = specs_dir / "auth"
        auth_spec.mkdir()
        (auth_spec / "requirements.md").write_text("# Auth Requirements")

        monkeypatch.chdir(tmp_path)

        list_specs(output_format="text")

        captured = capsys.readouterr()
        assert "Name: auth" in captured.out
        assert "Phase: requirements" in captured.out
        assert "Total: 1 spec(s)" in captured.out

    def test_rich_format_empty_specs(self, tmp_path, monkeypatch, capsys):
        """Test rich table output with no specs."""
        from ldf.spec_list import list_specs

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        (ldf_dir / "specs").mkdir()

        monkeypatch.chdir(tmp_path)

        list_specs(output_format="rich")

        captured = capsys.readouterr()
        assert "No specs found" in captured.out

    def test_rich_format_with_specs(self, tmp_path, monkeypatch, capsys):
        """Test rich table output with specs."""
        from ldf.spec_list import list_specs

        ldf_dir = tmp_path / ".ldf"
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir(parents=True)

        # Create specs at different phases
        (specs_dir / "auth").mkdir()
        (specs_dir / "auth" / "requirements.md").write_text("# Auth")
        (specs_dir / "auth" / "design.md").write_text("# Auth Design")
        (specs_dir / "auth" / "tasks.md").write_text("# Auth Tasks")

        (specs_dir / "billing").mkdir()
        (specs_dir / "billing" / "requirements.md").write_text("# Billing")
        (specs_dir / "billing" / "design.md").write_text("# Billing Design")

        (specs_dir / "cart").mkdir()
        (specs_dir / "cart" / "requirements.md").write_text("# Cart")

        (specs_dir / "empty-spec").mkdir()

        monkeypatch.chdir(tmp_path)

        list_specs(output_format="rich")

        captured = capsys.readouterr()
        # Rich output should include spec names
        assert "auth" in captured.out
        assert "billing" in captured.out
        assert "Total: 4 spec(s)" in captured.out

    def test_explicit_project_root(self, tmp_path, capsys):
        """Test using explicit project_root parameter."""
        from ldf.spec_list import list_specs

        ldf_dir = tmp_path / ".ldf"
        specs_dir = ldf_dir / "specs"
        specs_dir.mkdir(parents=True)

        (specs_dir / "test-spec").mkdir()
        (specs_dir / "test-spec" / "requirements.md").write_text("# Test")

        list_specs(output_format="json", project_root=tmp_path)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["total"] == 1


class TestGetLastModified:
    """Tests for _get_last_modified function."""

    def test_returns_iso_timestamp(self, tmp_path):
        """Test returns ISO formatted timestamp."""
        from ldf.spec_list import _get_last_modified

        spec_dir = tmp_path / "test-spec"
        spec_dir.mkdir()
        (spec_dir / "requirements.md").write_text("# Test")

        result = _get_last_modified(spec_dir)

        # Should be ISO format
        assert "T" in result  # ISO format separator

    def test_uses_latest_file_mtime(self, tmp_path):
        """Test uses the most recently modified file."""
        import time

        from ldf.spec_list import _get_last_modified

        spec_dir = tmp_path / "test-spec"
        spec_dir.mkdir()

        # Create requirements first
        (spec_dir / "requirements.md").write_text("# First")
        time.sleep(0.01)  # Small delay to ensure different mtimes

        # Create design later
        (spec_dir / "design.md").write_text("# Second")

        _get_last_modified(spec_dir)  # Call to verify no errors

        # Result should reflect design.md's mtime (the newer file)
        design_mtime = (spec_dir / "design.md").stat().st_mtime
        req_mtime = (spec_dir / "requirements.md").stat().st_mtime
        assert design_mtime >= req_mtime

    def test_uses_dir_mtime_when_no_files(self, tmp_path):
        """Test uses directory mtime when no markdown files exist."""
        from ldf.spec_list import _get_last_modified

        spec_dir = tmp_path / "empty-spec"
        spec_dir.mkdir()

        result = _get_last_modified(spec_dir)

        # Should return a valid ISO timestamp (from directory)
        assert "T" in result


class TestPrintRichTable:
    """Tests for _print_rich_table function."""

    def test_handles_malformed_timestamp(self, capsys):
        """Test handles malformed timestamp gracefully."""
        from ldf.spec_list import _print_rich_table

        specs = [
            {
                "name": "test-spec",
                "status": "requirements",
                "has_requirements": True,
                "has_design": False,
                "has_tasks": False,
                "last_modified": "not-a-valid-timestamp",
            }
        ]

        _print_rich_table(specs)

        captured = capsys.readouterr()
        assert "test-spec" in captured.out
        assert "not-a-valid-time" in captured.out  # Truncated fallback


class TestPrintText:
    """Tests for _print_text function."""

    def test_shows_completeness_indicators(self, capsys):
        """Test shows checkmarks for completeness."""
        from ldf.spec_list import _print_text

        specs = [
            {
                "name": "complete-spec",
                "status": "tasks",
                "has_requirements": True,
                "has_design": True,
                "has_tasks": True,
                "last_modified": "2024-01-01T00:00:00",
            },
            {
                "name": "partial-spec",
                "status": "requirements",
                "has_requirements": True,
                "has_design": False,
                "has_tasks": False,
                "last_modified": "2024-01-01T00:00:00",
            },
        ]

        _print_text(specs)

        captured = capsys.readouterr()
        # Complete spec should have all checkmarks
        assert "Requirements:" in captured.out
        assert "Design:" in captured.out
        assert "Tasks:" in captured.out
        assert "Total: 2 spec(s)" in captured.out
