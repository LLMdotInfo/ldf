"""Tests for ldf/audit_api.py - API integration for automated audits."""

from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from ldf.audit_api import (
    AuditConfig,
    AuditResponse,
    ChatGPTAuditor,
    GeminiAuditor,
    load_api_config,
    get_auditor,
    save_audit_response,
    _resolve_env_var,
)


class TestAuditConfig:
    """Tests for AuditConfig dataclass."""

    def test_audit_config_creation(self):
        """Test creating an AuditConfig."""
        config = AuditConfig(
            provider="chatgpt",
            api_key="test-key",
            model="gpt-4",
            timeout=60,
            max_tokens=2048,
        )
        assert config.provider == "chatgpt"
        assert config.api_key == "test-key"
        assert config.model == "gpt-4"
        assert config.timeout == 60
        assert config.max_tokens == 2048

    def test_audit_config_defaults(self):
        """Test AuditConfig default values."""
        config = AuditConfig(
            provider="gemini",
            api_key="test-key",
            model="gemini-pro",
        )
        assert config.timeout == 120
        assert config.max_tokens == 4096


class TestAuditResponse:
    """Tests for AuditResponse dataclass."""

    def test_audit_response_success(self):
        """Test successful AuditResponse."""
        response = AuditResponse(
            success=True,
            provider="chatgpt",
            audit_type="spec-review",
            spec_name="test-spec",
            content="## Findings\n\nNo issues found.",
            timestamp="2024-01-15T10:00:00",
        )
        assert response.success is True
        assert response.provider == "chatgpt"
        assert response.errors == []
        assert response.usage == {}

    def test_audit_response_failure(self):
        """Test failed AuditResponse."""
        response = AuditResponse(
            success=False,
            provider="gemini",
            audit_type="security",
            spec_name=None,
            content="",
            timestamp="2024-01-15T10:00:00",
            errors=["API error: rate limit exceeded"],
        )
        assert response.success is False
        assert len(response.errors) == 1
        assert "rate limit" in response.errors[0]


class TestResolveEnvVar:
    """Tests for environment variable resolution."""

    def test_resolve_env_var_simple(self, monkeypatch):
        """Test resolving a simple env var."""
        monkeypatch.setenv("TEST_API_KEY", "secret123")
        result = _resolve_env_var("${TEST_API_KEY}")
        assert result == "secret123"

    def test_resolve_env_var_embedded(self, monkeypatch):
        """Test resolving embedded env var."""
        monkeypatch.setenv("API_KEY", "abc123")
        result = _resolve_env_var("Bearer ${API_KEY}")
        assert result == "Bearer abc123"

    def test_resolve_env_var_missing(self, monkeypatch):
        """Test resolving missing env var returns empty."""
        monkeypatch.delenv("NONEXISTENT_VAR", raising=False)
        result = _resolve_env_var("${NONEXISTENT_VAR}")
        assert result == ""

    def test_resolve_env_var_no_var(self):
        """Test string without env var is unchanged."""
        result = _resolve_env_var("plain-string")
        assert result == "plain-string"

    def test_resolve_env_var_empty(self):
        """Test empty string returns empty."""
        result = _resolve_env_var("")
        assert result == ""


class TestLoadApiConfig:
    """Tests for loading API configuration."""

    def test_load_api_config_no_config_file(self, tmp_path):
        """Test loading config when no file exists."""
        configs = load_api_config(tmp_path)
        assert configs == {}

    def test_load_api_config_no_audit_api_section(self, tmp_path):
        """Test loading config without audit_api section."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        config_file = ldf_dir / "config.yaml"
        config_file.write_text("framework_version: '0.1.0'\n")

        configs = load_api_config(tmp_path)
        assert configs == {}

    def test_load_api_config_chatgpt(self, tmp_path, monkeypatch):
        """Test loading ChatGPT config."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        config_file = ldf_dir / "config.yaml"
        config_file.write_text("""
audit_api:
  chatgpt:
    api_key: ${OPENAI_API_KEY}
    model: gpt-4o
    timeout: 180
""")

        configs = load_api_config(tmp_path)
        assert "chatgpt" in configs
        assert configs["chatgpt"].api_key == "sk-test123"
        assert configs["chatgpt"].model == "gpt-4o"
        assert configs["chatgpt"].timeout == 180

    def test_load_api_config_gemini(self, tmp_path, monkeypatch):
        """Test loading Gemini config."""
        monkeypatch.setenv("GOOGLE_API_KEY", "AIza-test")

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        config_file = ldf_dir / "config.yaml"
        config_file.write_text("""
audit_api:
  gemini:
    api_key: ${GOOGLE_API_KEY}
    model: gemini-pro
""")

        configs = load_api_config(tmp_path)
        assert "gemini" in configs
        assert configs["gemini"].api_key == "AIza-test"
        assert configs["gemini"].model == "gemini-pro"

    def test_load_api_config_both_providers(self, tmp_path, monkeypatch):
        """Test loading config for both providers."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("GOOGLE_API_KEY", "AIza-test")

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        config_file = ldf_dir / "config.yaml"
        config_file.write_text("""
audit_api:
  chatgpt:
    api_key: ${OPENAI_API_KEY}
    model: gpt-4
  gemini:
    api_key: ${GOOGLE_API_KEY}
    model: gemini-pro
""")

        configs = load_api_config(tmp_path)
        assert len(configs) == 2
        assert "chatgpt" in configs
        assert "gemini" in configs

    def test_load_api_config_missing_api_key(self, tmp_path, monkeypatch):
        """Test config not loaded if API key is empty."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        config_file = ldf_dir / "config.yaml"
        config_file.write_text("""
audit_api:
  chatgpt:
    api_key: ${OPENAI_API_KEY}
    model: gpt-4
""")

        configs = load_api_config(tmp_path)
        assert "chatgpt" not in configs


class TestGetAuditor:
    """Tests for getting auditor instances."""

    def test_get_auditor_chatgpt(self, tmp_path, monkeypatch):
        """Test getting ChatGPT auditor."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

        configs = {
            "chatgpt": AuditConfig(
                provider="chatgpt",
                api_key="sk-test",
                model="gpt-4",
            )
        }

        auditor = get_auditor("chatgpt", configs)
        assert isinstance(auditor, ChatGPTAuditor)

    def test_get_auditor_gemini(self):
        """Test getting Gemini auditor."""
        configs = {
            "gemini": AuditConfig(
                provider="gemini",
                api_key="AIza-test",
                model="gemini-pro",
            )
        }

        auditor = get_auditor("gemini", configs)
        assert isinstance(auditor, GeminiAuditor)

    def test_get_auditor_not_configured(self):
        """Test getting auditor when not configured."""
        auditor = get_auditor("chatgpt", {})
        assert auditor is None

    def test_get_auditor_unknown_provider(self):
        """Test getting auditor for unknown provider."""
        configs = {
            "unknown": AuditConfig(
                provider="unknown",
                api_key="test",
                model="test-model",
            )
        }
        auditor = get_auditor("unknown", configs)
        assert auditor is None


class TestSaveAuditResponse:
    """Tests for saving audit responses."""

    def test_save_audit_response_success(self, tmp_path):
        """Test saving a successful audit response."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        response = AuditResponse(
            success=True,
            provider="chatgpt",
            audit_type="spec-review",
            spec_name="user-auth",
            content="## Findings\n\nNo issues found.",
            timestamp="2024-01-15T10:00:00",
            usage={"total_tokens": 1500},
        )

        saved_path = save_audit_response(response, tmp_path)

        assert saved_path.exists()
        assert "spec-review" in saved_path.name
        assert "user-auth" in saved_path.name
        assert "chatgpt" in saved_path.name

        content = saved_path.read_text()
        assert "# Audit Response: spec-review" in content
        assert "**Provider:** chatgpt" in content
        assert "**Spec:** user-auth" in content
        assert "**Status:** Success" in content
        assert "## Findings" in content

    def test_save_audit_response_failure(self, tmp_path):
        """Test saving a failed audit response."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        response = AuditResponse(
            success=False,
            provider="gemini",
            audit_type="security",
            spec_name=None,
            content="",
            timestamp="2024-01-15T10:00:00",
            errors=["API error: timeout", "Retry failed"],
        )

        saved_path = save_audit_response(response, tmp_path)

        assert saved_path.exists()
        content = saved_path.read_text()
        assert "**Status:** Failed" in content
        assert "## Errors" in content
        assert "API error: timeout" in content
        assert "Retry failed" in content

    def test_save_audit_response_no_spec_name(self, tmp_path):
        """Test saving response without spec name."""
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()

        response = AuditResponse(
            success=True,
            provider="chatgpt",
            audit_type="full",
            spec_name=None,
            content="Full audit results",
            timestamp="2024-01-15T10:00:00",
        )

        saved_path = save_audit_response(response, tmp_path)

        assert saved_path.exists()
        content = saved_path.read_text()
        assert "**Spec:** all" in content


class TestChatGPTAuditor:
    """Tests for ChatGPT auditor."""

    def test_provider_name(self):
        """Test ChatGPT auditor provider name."""
        config = AuditConfig(
            provider="chatgpt",
            api_key="test",
            model="gpt-4",
        )
        auditor = ChatGPTAuditor(config)
        assert auditor.provider_name == "chatgpt"


class TestGeminiAuditor:
    """Tests for Gemini auditor."""

    def test_provider_name(self):
        """Test Gemini auditor provider name."""
        config = AuditConfig(
            provider="gemini",
            api_key="test",
            model="gemini-pro",
        )
        auditor = GeminiAuditor(config)
        assert auditor.provider_name == "gemini"


class TestSystemPrompts:
    """Tests for audit type system prompts."""

    def test_chatgpt_system_prompts(self):
        """Test ChatGPT system prompts for different audit types."""
        config = AuditConfig(
            provider="chatgpt",
            api_key="test",
            model="gpt-4",
        )
        auditor = ChatGPTAuditor(config)

        # Test various audit types have appropriate prompts
        prompt = auditor._get_system_prompt("spec-review")
        assert "requirements" in prompt.lower()

        prompt = auditor._get_system_prompt("security")
        assert "security" in prompt.lower() or "OWASP" in prompt

        prompt = auditor._get_system_prompt("gap-analysis")
        assert "missing" in prompt.lower() or "gap" in prompt.lower()

        prompt = auditor._get_system_prompt("full")
        assert "comprehensive" in prompt.lower()

    def test_gemini_system_prompts(self):
        """Test Gemini system prompts for different audit types."""
        config = AuditConfig(
            provider="gemini",
            api_key="test",
            model="gemini-pro",
        )
        auditor = GeminiAuditor(config)

        # Test various audit types have appropriate prompts
        prompt = auditor._get_system_prompt("edge-cases")
        assert "edge" in prompt.lower() or "boundary" in prompt.lower()

        prompt = auditor._get_system_prompt("architecture")
        assert "architecture" in prompt.lower() or "design" in prompt.lower()
