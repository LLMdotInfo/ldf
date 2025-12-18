"""Tests for ldf.spec module."""

from pathlib import Path

from ldf.spec import create_spec, get_spec_path, list_specs


class TestCreateSpec:
    """Tests for create_spec function."""

    def test_creates_spec_directory(self, temp_project: Path):
        """Test that create_spec creates the spec directory."""
        result = create_spec("test-feature", temp_project)

        assert result is True
        spec_dir = temp_project / ".ldf" / "specs" / "test-feature"
        assert spec_dir.exists()

    def test_creates_requirements_md(self, temp_project: Path):
        """Test that create_spec creates requirements.md."""
        create_spec("test-feature", temp_project)

        requirements = temp_project / ".ldf" / "specs" / "test-feature" / "requirements.md"
        assert requirements.exists()
        content = requirements.read_text()
        assert "test-feature" in content

    def test_creates_design_md(self, temp_project: Path):
        """Test that create_spec creates design.md."""
        create_spec("test-feature", temp_project)

        design = temp_project / ".ldf" / "specs" / "test-feature" / "design.md"
        assert design.exists()
        content = design.read_text()
        assert "test-feature" in content

    def test_creates_tasks_md(self, temp_project: Path):
        """Test that create_spec creates tasks.md."""
        create_spec("test-feature", temp_project)

        tasks = temp_project / ".ldf" / "specs" / "test-feature" / "tasks.md"
        assert tasks.exists()
        content = tasks.read_text()
        assert "test-feature" in content

    def test_creates_answerpack_directory(self, temp_project: Path):
        """Test that create_spec creates the answerpack directory."""
        create_spec("test-feature", temp_project)

        answerpack = temp_project / ".ldf" / "answerpacks" / "test-feature"
        assert answerpack.exists()

    def test_fails_if_ldf_not_initialized(self, tmp_path: Path):
        """Test that create_spec fails if LDF is not initialized."""
        result = create_spec("test-feature", tmp_path)

        assert result is False

    def test_fails_if_spec_already_exists(self, temp_project: Path):
        """Test that create_spec fails if the spec already exists."""
        # Create the spec first
        create_spec("test-feature", temp_project)

        # Try to create it again
        result = create_spec("test-feature", temp_project)

        assert result is False

    def test_replaces_feature_name_placeholder(self, temp_project: Path):
        """Test that create_spec replaces {feature-name} placeholder."""
        # Create templates directory with a placeholder
        templates_dir = temp_project / ".ldf" / "templates"
        templates_dir.mkdir(exist_ok=True)
        (templates_dir / "requirements.md").write_text("# {feature-name} - Requirements\n\nFeature: {feature}\n")

        create_spec("my-cool-feature", temp_project)

        requirements = temp_project / ".ldf" / "specs" / "my-cool-feature" / "requirements.md"
        content = requirements.read_text()
        assert "my-cool-feature" in content
        assert "{feature-name}" not in content
        assert "{feature}" not in content


class TestListSpecs:
    """Tests for list_specs function."""

    def test_returns_empty_list_for_new_project(self, temp_project: Path):
        """Test that list_specs returns empty list for new project."""
        result = list_specs(temp_project)

        assert result == []

    def test_returns_spec_names(self, temp_project: Path):
        """Test that list_specs returns spec names."""
        create_spec("feature-a", temp_project)
        create_spec("feature-b", temp_project)

        result = list_specs(temp_project)

        assert "feature-a" in result
        assert "feature-b" in result

    def test_returns_empty_for_non_ldf_project(self, tmp_path: Path):
        """Test that list_specs returns empty for non-LDF project."""
        result = list_specs(tmp_path)

        assert result == []


class TestGetSpecPath:
    """Tests for get_spec_path function."""

    def test_returns_path_for_existing_spec(self, temp_project: Path):
        """Test that get_spec_path returns path for existing spec."""
        create_spec("test-feature", temp_project)

        result = get_spec_path("test-feature", temp_project)

        assert result is not None
        assert result == temp_project / ".ldf" / "specs" / "test-feature"

    def test_returns_none_for_nonexistent_spec(self, temp_project: Path):
        """Test that get_spec_path returns None for nonexistent spec."""
        result = get_spec_path("nonexistent", temp_project)

        assert result is None

    def test_returns_none_for_non_ldf_project(self, tmp_path: Path):
        """Test that get_spec_path returns None for non-LDF project."""
        result = get_spec_path("test-feature", tmp_path)

        assert result is None
