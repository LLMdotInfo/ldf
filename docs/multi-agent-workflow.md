# Multi-Agent Workflow

LDF supports using multiple AI agents to review your specs and code from different perspectives. This catches issues that a single agent might miss.

## Overview

| Agent | Strength | Use For |
|-------|----------|---------|
| **Your Primary Tool** | Context retention, implementation | Development, code generation |
| **ChatGPT** | Pattern recognition, alternatives | Spec review, code audit, security |
| **Gemini** | Edge cases, thoroughness | Gap analysis, architecture review |

## Quick Start

### 1. Generate an Audit Request

```bash
ldf audit --type spec-review --spec user-auth
```

This creates a structured audit request with your spec content.

### 2. Send to External Agent

1. Open ChatGPT or Gemini
2. Paste the prompt from `multi-agent/prompts/chatgpt/spec-review.md`
3. Paste the generated audit request
4. Submit for review

### 3. Import Feedback

Save the response and import it:

```bash
ldf audit --import audit-response.md --spec user-auth
```

## Available Audit Types

| Type | Command | Best Agent |
|------|---------|------------|
| Spec Review | `ldf audit --type spec-review` | ChatGPT |
| Code Audit | `ldf audit --type code-audit` | ChatGPT |
| Security | `ldf audit --type security` | ChatGPT |
| Pre-Launch | `ldf audit --type pre-launch` | ChatGPT |
| Gap Analysis | `ldf audit --type gap-analysis` | Gemini |
| Edge Cases | `ldf audit --type edge-cases` | Gemini |
| Architecture | `ldf audit --type architecture` | Gemini |
| Full (All Types) | `ldf audit --type full` | Both |

## When to Audit

| Phase | Recommended Audit |
|-------|-------------------|
| After drafting requirements | spec-review, gap-analysis |
| After design complete | architecture |
| Before implementation | edge-cases |
| Before merge | code-audit |
| Security-sensitive features | security |
| Before production release | pre-launch, full |

## Detailed Documentation

For comprehensive documentation including:
- Detailed workflow diagrams
- Audit templates
- Best practices
- Automated workflow (API integration)
- FAQ

See the [Multi-Agent README](../multi-agent/README.md).

## Prompts Reference

### ChatGPT Prompts
- [spec-review.md](../multi-agent/prompts/chatgpt/spec-review.md) - Review requirements and design specs
- [code-audit.md](../multi-agent/prompts/chatgpt/code-audit.md) - Review implementation code
- [security.md](../multi-agent/prompts/chatgpt/security.md) - Security-focused review
- [pre-launch.md](../multi-agent/prompts/chatgpt/pre-launch.md) - Production readiness review

### Gemini Prompts
- [gap-analysis.md](../multi-agent/prompts/gemini/gap-analysis.md) - Find missing requirements
- [edge-cases.md](../multi-agent/prompts/gemini/edge-cases.md) - Identify corner cases
- [architecture.md](../multi-agent/prompts/gemini/architecture.md) - Validate architecture decisions

## Security Best Practices

### API Key Management

Always use environment variables for API keys:

| Service | Environment Variable |
|---------|---------------------|
| OpenAI/ChatGPT | `OPENAI_API_KEY` |
| Google Gemini | `GOOGLE_AI_API_KEY` |

**Important**: Never store API keys in `.ldf/config.yaml` - this file may be committed to version control and could expose your credentials.
