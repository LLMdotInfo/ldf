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

Add to your `.ldf/config.yaml`:

```yaml
# API Configuration for automated audits
audit_api:
  chatgpt:
    api_key: ${OPENAI_API_KEY}  # From environment
    model: gpt-4
    timeout: 120
    max_tokens: 4096

  gemini:
    api_key: ${GOOGLE_API_KEY}  # From environment
    model: gemini-pro
    timeout: 120
    max_tokens: 4096
```

Set environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
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

# Full audit (all types sequentially)
ldf audit --type full --api --agent chatgpt

# Security audit with Gemini
ldf audit --type security --api --agent gemini

# Auto-import results (displays response inline)
ldf audit --type spec-review --spec user-auth --api --agent chatgpt --auto-import
```

### Python API

```python
from ldf.audit_api import run_api_audit, load_api_config, AuditResponse
import asyncio

# Load configuration from .ldf/config.yaml
configs = load_api_config()

# Run a ChatGPT audit
response: AuditResponse = asyncio.run(
    run_api_audit(
        provider="chatgpt",
        audit_type="spec-review",
        prompt="Your audit request content here...",
        spec_name="user-auth"  # optional
    )
)

if response.success:
    print(f"Audit complete: {response.content}")
    print(f"Tokens used: {response.usage.get('total_tokens', 'N/A')}")
else:
    print(f"Audit failed: {response.errors}")
```

## Response Format

Both providers return a standardized `AuditResponse`:

```python
@dataclass
class AuditResponse:
    success: bool
    provider: str  # "chatgpt" or "gemini"
    audit_type: str
    spec_name: str | None
    content: str  # Raw markdown response from the AI
    timestamp: str
    errors: list[str]  # Empty if success=True
    usage: dict[str, Any]  # Token usage (provider-specific)
```

Responses are automatically saved to `.ldf/audit-history/` with filename format:
`{audit_type}-{spec_name}-{provider}-{timestamp}.md`

## Cost Considerations

| Agent | Model | Cost (approx) | Speed |
|-------|-------|---------------|-------|
| ChatGPT | gpt-4o | ~$0.03-0.10 per audit | 10-30s |
| Gemini | gemini-pro | ~$0.01-0.03 per audit | 5-15s |

Estimate 5-10 audits per feature = $0.50-2.00 per feature.

## Error Handling

The `AuditResponse` object indicates success or failure:

```python
response = asyncio.run(run_api_audit(provider, audit_type, prompt))

if not response.success:
    for error in response.errors:
        if "timed out" in error:
            # Increase timeout in config
            pass
        elif "Rate limit" in error:
            # Back off and retry
            pass
        elif "not configured" in error:
            # Check .ldf/config.yaml
            pass
        else:
            # Log and fall back to manual workflow
            print(f"API error: {error}")
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
        run: pip install 'ldf[automation]'

      - name: Run Spec Audit
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          for spec in $(git diff --name-only origin/main -- '.ldf/specs/*/requirements.md'); do
            spec_name=$(dirname $spec | xargs basename)
            ldf audit --type spec-review --spec $spec_name --api --agent chatgpt
          done

      - name: Check Audit History
        run: |
          # Review saved audit responses in .ldf/audit-history/
          ls -la .ldf/audit-history/
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

## Implementation Files

| File | Purpose |
|------|---------|
| `ldf/audit_api.py` | API integration module (ChatGPT + Gemini) |
| `ldf/audit.py` | CLI integration and audit request generation |
| `.ldf/config.yaml` | Project configuration (add audit_api section) |
| `.ldf/audit-history/` | Saved audit responses |

## Troubleshooting

### "Rate limit exceeded"
Wait and retry. Consider using exponential backoff.

### "Content filtered"
The spec contains content the API flagged. Use manual workflow.

### "Invalid API key"
Check environment variable is set correctly.

### "Timeout"
Increase timeout in config or use smaller spec chunks.
