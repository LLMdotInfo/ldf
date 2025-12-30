"""Tests for ldf.utils.references module."""

import pytest

from ldf.utils.references import (
    REFERENCE_PATTERN,
    SHARED_REFERENCE_PATTERN,
    SpecReference,
    build_dependency_graph,
    detect_circular_dependencies,
    parse_references,
    parse_references_from_file,
    resolve_reference,
    validate_all_workspace_references,
    validate_references_in_spec,
)


class TestReferencePatterns:
    """Tests for reference regex patterns."""

    def test_basic_reference(self):
        """Test matching basic project:spec reference."""
        match = REFERENCE_PATTERN.search("See @auth:user-session for details")
        assert match is not None
        assert match.group("project") == "auth"
        assert match.group("spec") == "user-session"
        assert match.group("section") is None

    def test_reference_with_section(self):
        """Test matching reference with section anchor."""
        match = REFERENCE_PATTERN.search("Check @billing:payment#api-design")
        assert match is not None
        assert match.group("project") == "billing"
        assert match.group("spec") == "payment"
        assert match.group("section") == "api-design"

    def test_reference_with_dots(self):
        """Test matching reference with dots in names."""
        match = REFERENCE_PATTERN.search("See @api.v2:user.auth for auth")
        assert match is not None
        assert match.group("project") == "api.v2"
        assert match.group("spec") == "user.auth"

    def test_shared_reference(self):
        """Test matching shared resource reference."""
        match = SHARED_REFERENCE_PATTERN.search("Uses @shared:common-types")
        assert match is not None
        assert match.group("resource") == "common-types"


class TestSpecReference:
    """Tests for SpecReference dataclass."""

    def test_is_shared_property(self):
        """Test is_shared property."""
        shared_ref = SpecReference(project="shared", spec="types")
        assert shared_ref.is_shared is True

        normal_ref = SpecReference(project="auth", spec="login")
        assert normal_ref.is_shared is False

    def test_str_without_section(self):
        """Test string representation without section."""
        ref = SpecReference(project="auth", spec="user-session")
        assert str(ref) == "@auth:user-session"

    def test_str_with_section(self):
        """Test string representation with section."""
        ref = SpecReference(project="billing", spec="payment", section="api-design")
        assert str(ref) == "@billing:payment#api-design"


class TestParseReferences:
    """Tests for parse_references function."""

    def test_no_references(self):
        """Test parsing content with no references."""
        content = "This is a normal markdown document."
        refs = parse_references(content)
        assert refs == []

    def test_single_reference(self):
        """Test parsing single reference."""
        content = "Depends on @auth:user-session for authentication."
        refs = parse_references(content)

        assert len(refs) == 1
        assert refs[0].project == "auth"
        assert refs[0].spec == "user-session"
        assert refs[0].line_number == 1

    def test_multiple_references_same_line(self):
        """Test parsing multiple references on same line."""
        content = "Uses @auth:login and @billing:payment"
        refs = parse_references(content)

        assert len(refs) == 2
        assert refs[0].project == "auth"
        assert refs[1].project == "billing"

    def test_references_multiple_lines(self):
        """Test parsing references across multiple lines."""
        content = """# Dependencies
- @auth:user-session
- @billing:payment
"""
        refs = parse_references(content)

        assert len(refs) == 2
        assert refs[0].line_number == 2
        assert refs[1].line_number == 3

    def test_shared_reference(self):
        """Test parsing shared resource reference."""
        content = "Uses @shared:common-types for type definitions."
        refs = parse_references(content)

        # Note: @shared:common-types matches both REFERENCE_PATTERN and SHARED_REFERENCE_PATTERN
        # Both are included in results - deduplicated by consumers if needed
        assert len(refs) >= 1
        shared_refs = [r for r in refs if r.is_shared]
        assert len(shared_refs) >= 1
        assert shared_refs[0].spec == "common-types"


class TestParseReferencesFromFile:
    """Tests for parse_references_from_file function."""

    def test_file_not_exists(self, tmp_path):
        """Test parsing non-existent file."""
        refs = parse_references_from_file(tmp_path / "nonexistent.md")
        assert refs == []

    def test_file_with_references(self, tmp_path):
        """Test parsing file with references."""
        md_file = tmp_path / "requirements.md"
        md_file.write_text("""# Requirements
Depends on @auth:user-session
""")

        refs = parse_references_from_file(md_file)

        assert len(refs) == 1
        assert refs[0].project == "auth"

    def test_file_with_binary_content(self, tmp_path):
        """Test handling files with binary content (can't decode)."""
        md_file = tmp_path / "binary.md"
        md_file.write_bytes(b"\x00\x01\x02\xff\xfe")

        # Binary file may cause decode error, function should handle gracefully
        refs = parse_references_from_file(md_file)
        # Either returns empty list or parses whatever it can
        assert isinstance(refs, list)


class TestResolveReference:
    """Tests for resolve_reference function."""

    @pytest.fixture
    def workspace_with_projects(self, tmp_path):
        """Create a workspace with multiple projects."""
        from ldf.models.workspace import WorkspaceManifest

        # Create workspace manifest
        manifest_data = {
            "version": "1.0",
            "name": "test-workspace",
            "projects": {
                "explicit": [
                    {"path": "services/auth", "alias": "auth"},
                    {"path": "services/billing", "alias": "billing"},
                ]
            },
            "shared": {"path": ".ldf-shared/"},
        }

        # Create project directories with specs
        auth_spec = tmp_path / "services" / "auth" / ".ldf" / "specs" / "user-session"
        auth_spec.mkdir(parents=True)
        (auth_spec / "requirements.md").write_text("# User Session")

        billing_spec = tmp_path / "services" / "billing" / ".ldf" / "specs" / "payment"
        billing_spec.mkdir(parents=True)

        # Create shared resources
        shared = tmp_path / ".ldf-shared"
        shared.mkdir()
        (shared / "common-types.yaml").write_text("types: {}")

        manifest = WorkspaceManifest.from_dict(manifest_data)

        return tmp_path, manifest, shared

    def test_resolve_valid_reference(self, workspace_with_projects):
        """Test resolving a valid cross-project reference."""
        workspace_root, manifest, shared = workspace_with_projects

        ref = SpecReference(project="auth", spec="user-session")
        result = resolve_reference(ref, workspace_root, manifest)

        assert result.exists is True
        assert result.error is None
        assert "user-session" in str(result.resolved_path)

    def test_resolve_unknown_project(self, workspace_with_projects):
        """Test resolving reference to unknown project."""
        workspace_root, manifest, shared = workspace_with_projects

        ref = SpecReference(project="unknown", spec="some-spec")
        result = resolve_reference(ref, workspace_root, manifest)

        assert result.exists is False
        assert "not found" in result.error
        assert "auth" in result.error  # Should list available projects

    def test_resolve_unknown_spec(self, workspace_with_projects):
        """Test resolving reference to unknown spec in known project."""
        workspace_root, manifest, shared = workspace_with_projects

        ref = SpecReference(project="auth", spec="nonexistent-spec")
        result = resolve_reference(ref, workspace_root, manifest)

        assert result.exists is False
        assert "not found" in result.error

    def test_resolve_shared_reference(self, workspace_with_projects):
        """Test resolving shared resource reference."""
        workspace_root, manifest, shared = workspace_with_projects

        ref = SpecReference(project="shared", spec="common-types")
        result = resolve_reference(ref, workspace_root, manifest, shared)

        assert result.exists is True

    def test_resolve_shared_without_path(self, workspace_with_projects):
        """Test resolving shared reference without shared path."""
        workspace_root, manifest, _ = workspace_with_projects

        ref = SpecReference(project="shared", spec="types")
        result = resolve_reference(ref, workspace_root, manifest, None)

        assert result.exists is False
        assert "No shared resources" in result.error

    def test_resolve_shared_resource_not_found(self, workspace_with_projects):
        """Test resolving non-existent shared resource."""
        workspace_root, manifest, shared = workspace_with_projects

        ref = SpecReference(project="shared", spec="nonexistent")
        result = resolve_reference(ref, workspace_root, manifest, shared)

        assert result.exists is False
        assert "not found" in result.error

    def test_resolve_reference_with_valid_section(self, workspace_with_projects):
        """Test resolving reference with a valid section."""
        workspace_root, manifest, shared = workspace_with_projects

        # Add spec.md with section headers to auth project
        spec_path = workspace_root / "services" / "auth" / ".ldf" / "specs" / "user-session"
        (spec_path / "spec.md").write_text(
            "# User Session\n\n## API Design\n\nSome API details.\n\n## Data Model\n\nModels."
        )

        ref = SpecReference(project="auth", spec="user-session", section="API Design")
        result = resolve_reference(ref, workspace_root, manifest)

        assert result.exists is True
        assert result.error is None

    def test_resolve_reference_with_invalid_section(self, workspace_with_projects):
        """Test resolving reference with a non-existent section."""
        workspace_root, manifest, shared = workspace_with_projects

        # Add spec.md to auth project
        spec_path = workspace_root / "services" / "auth" / ".ldf" / "specs" / "user-session"
        (spec_path / "spec.md").write_text("# User Session\n\n## Overview\n\nBasic info.")

        ref = SpecReference(project="auth", spec="user-session", section="API Design")
        result = resolve_reference(ref, workspace_root, manifest)

        assert result.exists is False
        assert "Section 'API Design' not found" in result.error
        assert "auth:user-session" in result.error

    def test_resolve_reference_section_case_insensitive(self, workspace_with_projects):
        """Test that section matching is case-insensitive."""
        workspace_root, manifest, shared = workspace_with_projects

        spec_path = workspace_root / "services" / "auth" / ".ldf" / "specs" / "user-session"
        (spec_path / "spec.md").write_text("# User Session\n\n## API Design\n\nDetails.")

        # Reference with different case
        ref = SpecReference(project="auth", spec="user-session", section="api design")
        result = resolve_reference(ref, workspace_root, manifest)

        assert result.exists is True
        assert result.error is None

    def test_resolve_reference_section_without_spec_md(self, workspace_with_projects):
        """Test section reference when spec.md doesn't exist."""
        workspace_root, manifest, shared = workspace_with_projects

        # user-session spec exists (from fixture) but has no spec.md
        ref = SpecReference(project="auth", spec="user-session", section="Overview")
        result = resolve_reference(ref, workspace_root, manifest)

        # Should still succeed (spec exists, we just can't validate the section)
        assert result.exists is True
        assert result.error is None


class TestValidateReferencesInSpec:
    """Tests for validate_references_in_spec function."""

    def test_validates_all_md_files(self, tmp_path):
        """Test validates references in all markdown files."""
        from ldf.models.workspace import WorkspaceManifest

        # Create workspace
        manifest_data = {
            "version": "1.0",
            "name": "test",
            "projects": {"explicit": []},
            "shared": {"path": ".ldf-shared/"},
        }
        manifest = WorkspaceManifest.from_dict(manifest_data)

        # Create spec with references
        spec_path = tmp_path / "spec"
        spec_path.mkdir()
        (spec_path / "requirements.md").write_text("Depends on @auth:login")
        (spec_path / "design.md").write_text("Uses @billing:payment")

        results = validate_references_in_spec(spec_path, tmp_path, manifest)

        assert len(results) == 2


class TestValidateAllWorkspaceReferences:
    """Tests for validate_all_workspace_references function."""

    def test_returns_empty_if_no_manifest(self, tmp_path):
        """Test returns empty dict if no workspace manifest."""
        result = validate_all_workspace_references(tmp_path)
        assert result == {}

    def test_returns_empty_on_manifest_error(self, tmp_path):
        """Test returns empty dict on manifest parse error."""
        manifest = tmp_path / "ldf-workspace.yaml"
        manifest.write_text("invalid: yaml: [[[")

        result = validate_all_workspace_references(tmp_path)
        assert result == {}

    def test_validates_workspace_references(self, tmp_path):
        """Test validates references across workspace."""
        # Create workspace manifest
        manifest = tmp_path / "ldf-workspace.yaml"
        manifest.write_text("""
version: "1.0"
name: test-workspace
projects:
  explicit:
    - path: services/auth
      alias: auth
    - path: services/billing
      alias: billing
shared:
  path: .ldf-shared/
""")

        # Create projects with cross-references
        auth_spec = tmp_path / "services" / "auth" / ".ldf" / "specs" / "login"
        auth_spec.mkdir(parents=True)
        (auth_spec / "requirements.md").write_text("Depends on @billing:payment")

        billing_spec = tmp_path / "services" / "billing" / ".ldf" / "specs" / "payment"
        billing_spec.mkdir(parents=True)

        result = validate_all_workspace_references(tmp_path)

        assert "auth" in result
        assert len(result["auth"]) == 1

    def test_skips_projects_without_specs(self, tmp_path):
        """Test skips projects that don't have specs directory."""
        manifest = tmp_path / "ldf-workspace.yaml"
        manifest.write_text("""
version: "1.0"
name: test-workspace
projects:
  explicit:
    - path: services/empty
      alias: empty
""")

        # Create project without specs
        project = tmp_path / "services" / "empty" / ".ldf"
        project.mkdir(parents=True)
        # No specs directory

        result = validate_all_workspace_references(tmp_path)
        assert result == {}


class TestBuildDependencyGraph:
    """Tests for build_dependency_graph function."""

    def test_builds_graph_from_references(self, tmp_path):
        """Test builds dependency graph from cross-references."""
        # Create workspace
        manifest = tmp_path / "ldf-workspace.yaml"
        manifest.write_text("""
version: "1.0"
name: test-workspace
projects:
  explicit:
    - path: services/auth
      alias: auth
    - path: services/billing
      alias: billing
    - path: services/api
      alias: api
shared:
  path: .ldf-shared/
""")

        # auth depends on billing
        auth_spec = tmp_path / "services" / "auth" / ".ldf" / "specs" / "login"
        auth_spec.mkdir(parents=True)
        (auth_spec / "requirements.md").write_text("Uses @billing:payment")

        # billing depends on api
        billing_spec = tmp_path / "services" / "billing" / ".ldf" / "specs" / "payment"
        billing_spec.mkdir(parents=True)
        (billing_spec / "requirements.md").write_text("Calls @api:endpoints")

        # api has no deps
        api_spec = tmp_path / "services" / "api" / ".ldf" / "specs" / "endpoints"
        api_spec.mkdir(parents=True)

        graph = build_dependency_graph(tmp_path)

        assert "auth" in graph
        assert "billing" in graph["auth"]


class TestDetectCircularDependencies:
    """Tests for detect_circular_dependencies function."""

    def test_no_cycles(self):
        """Test detecting no cycles in acyclic graph."""
        graph = {
            "a": {"b"},
            "b": {"c"},
            "c": set(),
        }

        cycles = detect_circular_dependencies(graph)
        assert cycles == []

    def test_simple_cycle(self):
        """Test detecting simple A -> B -> A cycle."""
        graph = {
            "a": {"b"},
            "b": {"a"},
        }

        cycles = detect_circular_dependencies(graph)
        assert len(cycles) > 0

    def test_longer_cycle(self):
        """Test detecting longer A -> B -> C -> A cycle."""
        graph = {
            "a": {"b"},
            "b": {"c"},
            "c": {"a"},
        }

        cycles = detect_circular_dependencies(graph)
        assert len(cycles) > 0
        # Should find a cycle containing a, b, c
        cycle = cycles[0]
        assert "a" in cycle
        assert "b" in cycle
        assert "c" in cycle

    def test_empty_graph(self):
        """Test empty graph has no cycles."""
        graph = {}
        cycles = detect_circular_dependencies(graph)
        assert cycles == []

    def test_isolated_nodes(self):
        """Test graph with isolated nodes."""
        graph = {
            "a": set(),
            "b": set(),
        }

        cycles = detect_circular_dependencies(graph)
        assert cycles == []
