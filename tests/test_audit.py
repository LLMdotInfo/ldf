"""Tests for ldf.audit module."""

import pytest
from pathlib import Path

from ldf.audit import run_audit, _build_audit_request, _redact_content, _generate_audit_request


class TestRedaction:
    """Tests for content redaction."""

    def test_redacts_api_keys(self):
        """Test that API key patterns are redacted."""
        content = 'api_key = "sk-1234567890abcdef1234567890abcdef"'
        redacted = _redact_content(content)
        assert "sk-1234567890" not in redacted
        assert "REDACTED" in redacted

    def test_redacts_prefixed_api_keys(self):
        """Test that prefixed API keys (sk-, pk-) are redacted."""
        content = "**API Key:** sk-test-12345678901234567890"
        redacted = _redact_content(content)
        assert "sk-test-12345678901234567890" not in redacted
        assert "[API_KEY_REDACTED]" in redacted

    def test_redacts_bearer_tokens(self):
        """Test that Bearer tokens are redacted."""
        content = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        redacted = _redact_content(content)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted
        assert "Bearer [REDACTED]" in redacted

    def test_redacts_password_values(self):
        """Test that password values are redacted."""
        content = 'password: "mysecretpassword123"'
        redacted = _redact_content(content)
        assert "mysecretpassword123" not in redacted
        assert "[REDACTED]" in redacted

    def test_redacts_aws_keys(self):
        """Test that AWS keys are redacted."""
        content = "AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE"
        redacted = _redact_content(content)
        assert "AKIAIOSFODNN7EXAMPLE" not in redacted

    def test_redacts_env_var_references(self):
        """Test that secret env var references are redacted."""
        content = "Use ${SECRET_TOKEN} for authentication"
        redacted = _redact_content(content)
        assert "${SECRET_TOKEN}" not in redacted
        assert "[ENV_VAR_REDACTED]" in redacted

    def test_preserves_normal_content(self):
        """Test that normal content is not redacted."""
        content = """# Feature Requirements

## Overview

This feature handles user authentication.

## User Stories

### US-1: Login Flow

Users can log in with email and password.
"""
        redacted = _redact_content(content)
        assert "Feature Requirements" in redacted
        assert "user authentication" in redacted
        assert "Login Flow" in redacted


class TestBuildAuditRequest:
    """Tests for _build_audit_request function."""

    def test_includes_spec_content(self, temp_project_with_specs: Path, monkeypatch):
        """Test that audit request includes spec content."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("spec-review", specs, include_secrets=True)

        assert "feature-a" in content
        assert "feature-b" in content
        assert "Requirements" in content

    def test_redacts_by_default(self, temp_project_with_specs: Path, monkeypatch):
        """Test that secrets are redacted by default."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("spec-review", specs, include_secrets=False)

        # The test spec has "sk-test-12345678901234567890" which should be redacted
        assert "sk-test-12345678901234567890" not in content

    def test_includes_secrets_when_flag_set(self, temp_project_with_specs: Path, monkeypatch):
        """Test that secrets are included when flag is set."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("spec-review", specs, include_secrets=True)

        # When include_secrets=True, the content should be present
        assert "sk-test-12345678901234567890" in content

    def test_includes_correct_instructions(self, temp_project_with_specs: Path, monkeypatch):
        """Test that audit type determines instructions."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        spec_review = _build_audit_request("spec-review", specs, include_secrets=False)
        assert "Completeness of requirements" in spec_review

        security = _build_audit_request("security", specs, include_secrets=False)
        assert "OWASP Top 10" in security

    def test_truncates_long_content(self, temp_project: Path, monkeypatch):
        """Test that long spec content is truncated."""
        spec_dir = temp_project / ".ldf" / "specs" / "long-spec"
        spec_dir.mkdir(parents=True)

        # Create a spec with very long content (using text that won't trigger redaction)
        long_content = "# Requirements\n\n" + "This is a long requirement. " * 300
        (spec_dir / "requirements.md").write_text(long_content)
        (spec_dir / "design.md").write_text("# Design")
        (spec_dir / "tasks.md").write_text("# Tasks")

        monkeypatch.chdir(temp_project)

        content = _build_audit_request("spec-review", [spec_dir], include_secrets=False)

        assert "... (truncated)" in content


class TestRunAudit:
    """Tests for run_audit function."""

    def test_requires_type_or_import(self, temp_project: Path, monkeypatch, capsys):
        """Test that audit requires --type or --import."""
        monkeypatch.chdir(temp_project)

        run_audit(None, None, False)

        captured = capsys.readouterr()
        assert "Specify --type or --import" in captured.out

    def test_import_nonexistent_file(self, temp_project: Path, monkeypatch, capsys):
        """Test importing a nonexistent file shows error."""
        monkeypatch.chdir(temp_project)

        run_audit(None, "/nonexistent/path.md", False)

        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_import_feedback_saves_to_history(
        self, temp_project: Path, temp_feedback_file: Path, monkeypatch
    ):
        """Test that imported feedback is saved to audit history."""
        monkeypatch.chdir(temp_project)

        run_audit(None, str(temp_feedback_file), False)

        audit_dir = temp_project / ".ldf" / "audit-history"
        assert audit_dir.exists()
        feedback_files = list(audit_dir.glob("feedback-*.md"))
        assert len(feedback_files) == 1


class TestAuditGeneration:
    """Tests for audit request generation."""

    def test_generates_audit_file(self, temp_project_with_specs: Path, monkeypatch):
        """Test that audit generates output file with -y flag."""
        monkeypatch.chdir(temp_project_with_specs)

        run_audit("spec-review", None, False, include_secrets=False, skip_confirm=True)

        output_file = temp_project_with_specs / "audit-request-spec-review.md"
        assert output_file.exists()

    def test_no_specs_shows_warning(self, temp_project: Path, monkeypatch, capsys):
        """Test that no specs shows warning."""
        monkeypatch.chdir(temp_project)

        run_audit("spec-review", None, False, skip_confirm=True)

        captured = capsys.readouterr()
        assert "No specs found" in captured.out

    def test_specs_dir_not_found(self, tmp_path: Path, monkeypatch, capsys):
        """Test that missing specs dir shows error."""
        monkeypatch.chdir(tmp_path)

        run_audit("spec-review", None, False, skip_confirm=True)

        captured = capsys.readouterr()
        assert "specs/ not found" in captured.out or "Run 'ldf init' first" in captured.out

    def test_spec_not_found_by_name(self, temp_project: Path, monkeypatch, capsys):
        """Test that specifying a nonexistent spec shows error."""
        monkeypatch.chdir(temp_project)

        run_audit("spec-review", None, False, skip_confirm=True, spec_name="nonexistent-spec")

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_specific_spec_audit(self, temp_project_with_specs: Path, monkeypatch):
        """Test that specific spec can be audited."""
        monkeypatch.chdir(temp_project_with_specs)

        run_audit("spec-review", None, False, skip_confirm=True, spec_name="feature-a")

        output_file = temp_project_with_specs / "audit-request-spec-review.md"
        assert output_file.exists()
        content = output_file.read_text()
        assert "feature-a" in content
        # feature-b should not be in specific spec audit
        assert "feature-b" not in content


class TestAuditConfirmation:
    """Tests for audit confirmation prompts."""

    def test_export_cancelled_by_user(self, temp_project_with_specs: Path, monkeypatch, capsys):
        """Test that user can cancel export."""
        monkeypatch.chdir(temp_project_with_specs)
        monkeypatch.setattr("ldf.audit.Confirm.ask", lambda *a, **kw: False)

        run_audit("spec-review", None, False, include_secrets=False, skip_confirm=False)

        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    def test_export_confirmed(self, temp_project_with_specs: Path, monkeypatch, capsys):
        """Test that user can confirm export."""
        monkeypatch.chdir(temp_project_with_specs)
        monkeypatch.setattr("ldf.audit.Confirm.ask", lambda *a, **kw: True)

        run_audit("spec-review", None, False, include_secrets=False, skip_confirm=False)

        captured = capsys.readouterr()
        assert "Generated:" in captured.out

    def test_secrets_warning_displayed(self, temp_project_with_specs: Path, monkeypatch, capsys):
        """Test that secrets warning is displayed when including secrets."""
        monkeypatch.chdir(temp_project_with_specs)
        monkeypatch.setattr("ldf.audit.Confirm.ask", lambda *a, **kw: True)

        run_audit("spec-review", None, False, include_secrets=True, skip_confirm=False)

        captured = capsys.readouterr()
        assert "SECRETS INCLUDED" in captured.out

    def test_redaction_note_displayed(self, temp_project_with_specs: Path, monkeypatch, capsys):
        """Test that redaction note is displayed when not including secrets."""
        monkeypatch.chdir(temp_project_with_specs)
        monkeypatch.setattr("ldf.audit.Confirm.ask", lambda *a, **kw: True)

        run_audit("spec-review", None, False, include_secrets=False, skip_confirm=False)

        captured = capsys.readouterr()
        assert "redacted" in captured.out.lower()


class TestApiMode:
    """Tests for API automation mode."""

    def test_api_mode_requires_agent(self, temp_project_with_specs: Path, monkeypatch, capsys):
        """Test that API mode requires --agent parameter."""
        monkeypatch.chdir(temp_project_with_specs)

        run_audit("spec-review", None, True, skip_confirm=True)

        captured = capsys.readouterr()
        assert "--api requires --agent" in captured.out
        assert "chatgpt or gemini" in captured.out

    def test_api_mode_unconfigured_provider(self, temp_project_with_specs: Path, monkeypatch, capsys):
        """Test that API mode shows error for unconfigured provider."""
        monkeypatch.chdir(temp_project_with_specs)

        run_audit("spec-review", None, True, agent="chatgpt", skip_confirm=True)

        captured = capsys.readouterr()
        assert "not configured" in captured.out
        assert "config.yaml" in captured.out


class TestAllAuditTypes:
    """Tests for all audit type instructions."""

    def test_code_audit_instructions(self, temp_project_with_specs: Path, monkeypatch):
        """Test code-audit audit type instructions."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("code-audit", specs, include_secrets=False)

        assert "Code quality" in content
        assert "Security vulnerabilities" in content

    def test_pre_launch_instructions(self, temp_project_with_specs: Path, monkeypatch):
        """Test pre-launch audit type instructions."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("pre-launch", specs, include_secrets=False)

        assert "Production readiness" in content
        assert "Rollback procedures" in content

    def test_gap_analysis_instructions(self, temp_project_with_specs: Path, monkeypatch):
        """Test gap-analysis audit type instructions."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("gap-analysis", specs, include_secrets=False)

        assert "Missing requirements" in content
        assert "Guardrail coverage gaps" in content

    def test_edge_cases_instructions(self, temp_project_with_specs: Path, monkeypatch):
        """Test edge-cases audit type instructions."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("edge-cases", specs, include_secrets=False)

        assert "Boundary conditions" in content
        assert "Error handling paths" in content

    def test_architecture_instructions(self, temp_project_with_specs: Path, monkeypatch):
        """Test architecture audit type instructions."""
        monkeypatch.chdir(temp_project_with_specs)
        specs_dir = temp_project_with_specs / ".ldf" / "specs"
        specs = list(specs_dir.iterdir())

        content = _build_audit_request("architecture", specs, include_secrets=False)

        assert "Component coupling" in content
        assert "Scalability concerns" in content
