# Automated Multi-Agent Workflow

Optional API automation for sending audit requests to ChatGPT and Gemini programmatically.

## When to Use Automation

**Use automation when:**
- You run many audits per day
- You want CI/CD integration
- You prefer CLI-based workflows
- You have API keys available

**Use manual workflow when:**
- Occasional audits
- No API budget
- Learning the audit process
- Sensitive content (avoid API)

## Setup

### 1. Install Dependencies

```bash
pip install openai google-generativeai
```

### 2. Configure API Keys

Create `.ldf/config.yaml`:

```yaml
# API Configuration (DO NOT commit this file!)
automation:
  openai:
    api_key: ${OPENAI_API_KEY}  # From environment
    model: gpt-4o
    max_tokens: 4000

  google:
    api_key: ${GOOGLE_AI_API_KEY}  # From environment
    model: gemini-pro
    max_tokens: 4000
```

Or set environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_AI_API_KEY="AIza..."
```

### 3. Add to .gitignore

```gitignore
# API keys
.ldf/config.yaml
*.env
```

## Usage

### Command Line

```bash
# Spec review with ChatGPT
ldf audit --type spec-review --spec user-auth --api --agent chatgpt

# Gap analysis with Gemini
ldf audit --type gap-analysis --spec user-auth --api --agent gemini

# Full audit (both agents)
ldf audit --type full --spec user-auth --api

# Auto-import results
ldf audit --type spec-review --spec user-auth --api --auto-import
```

### Python API

```python
from multi_agent.automation import ChatGPTAuditor, GeminiAuditor

# ChatGPT audit
auditor = ChatGPTAuditor()
result = await auditor.audit_spec(
    spec_content="...",
    prompt_type="spec-review"
)

# Gemini audit
auditor = GeminiAuditor()
result = await auditor.audit_spec(
    spec_content="...",
    prompt_type="gap-analysis"
)
```

## Response Format

Both clients return a standardized `AuditResult`:

```python
@dataclass
class AuditResult:
    request_id: str
    audit_type: str
    agent: str
    timestamp: datetime
    assessment: str  # APPROVE | NEEDS_REVISION | REJECT
    risk_level: str  # LOW | MEDIUM | HIGH | CRITICAL
    issues: list[AuditIssue]
    raw_response: str
```

## Cost Considerations

| Agent | Model | Cost (approx) | Speed |
|-------|-------|---------------|-------|
| ChatGPT | gpt-4o | ~$0.03-0.10 per audit | 10-30s |
| Gemini | gemini-pro | ~$0.01-0.03 per audit | 5-15s |

Estimate 5-10 audits per feature = $0.50-2.00 per feature.

## Error Handling

```python
try:
    result = await auditor.audit_spec(content, prompt_type)
except RateLimitError:
    # Back off and retry
except APIError as e:
    # Log and fall back to manual
except ContentFilterError:
    # Content was blocked, use manual workflow
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Spec Audit
on:
  pull_request:
    paths:
      - '.ldf/specs/**'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install LDF
        run: pip install ldf

      - name: Run Spec Audit
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          for spec in $(git diff --name-only origin/main -- '.ldf/specs/*/requirements.md'); do
            spec_name=$(dirname $spec | xargs basename)
            ldf audit --type spec-review --spec $spec_name --api --output json
          done

      - name: Check Results
        run: |
          if grep -q '"assessment": "REJECT"' audit-results/*.json; then
            echo "Spec audit failed"
            exit 1
          fi
```

## Limitations

1. **Context Length**: Large specs may need chunking
2. **Rate Limits**: OpenAI: 10k TPM, Google: varies
3. **Consistency**: Different runs may give different results
4. **Hallucination**: Always verify agent findings
5. **Privacy**: Spec content sent to third-party APIs

## Security Considerations

- Never commit API keys
- Use environment variables or secrets manager
- Review what data is sent to APIs
- Consider self-hosted models for sensitive content
- Audit logs should not contain sensitive spec content

## Files

| File | Purpose |
|------|---------|
| `openai_client.py` | ChatGPT API wrapper |
| `google_client.py` | Gemini API wrapper |
| `config.example.yaml` | Configuration template |

## Troubleshooting

### "Rate limit exceeded"
Wait and retry. Consider using exponential backoff.

### "Content filtered"
The spec contains content the API flagged. Use manual workflow.

### "Invalid API key"
Check environment variable is set correctly.

### "Timeout"
Increase timeout in config or use smaller spec chunks.
