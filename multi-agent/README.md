# Multi-Agent Workflow

Use multiple AI agents to review specs and code from different perspectives. Each agent has unique strengths - use one as your primary development tool, and others for review.

## Why Multi-Agent?

| Agent | Strength | Best For |
|-------|----------|----------|
| **Your Primary Tool** | Implementation, context retention | Primary development, code generation |
| **ChatGPT** | Pattern recognition, alternatives | Spec review, code audit, security |
| **Gemini** | Edge cases, gap analysis | Architecture review, completeness |

**Supported primary tools:** Claude Code, Gemini CLI, Codex CLI, Cursor, or any MCP-compatible assistant.

Using multiple agents catches issues that a single agent might miss due to training biases or blind spots.

## Available Prompts

### ChatGPT Prompts
| Prompt | When to Use |
|--------|-------------|
| [spec-review.md](prompts/chatgpt/spec-review.md) | After drafting requirements or design |
| [code-audit.md](prompts/chatgpt/code-audit.md) | After implementation, before merge |
| [security.md](prompts/chatgpt/security.md) | For security-sensitive features |
| [pre-launch.md](prompts/chatgpt/pre-launch.md) | Before production release |

### Gemini Prompts
| Prompt | When to Use |
|--------|-------------|
| [gap-analysis.md](prompts/gemini/gap-analysis.md) | After requirements, find what's missing |
| [edge-cases.md](prompts/gemini/edge-cases.md) | Before implementation, identify corner cases |
| [architecture.md](prompts/gemini/architecture.md) | After design, validate architecture |

## Workflow: Manual (Recommended)

The manual workflow is recommended for most teams. It provides full control and doesn't require API keys.

### Step 1: Generate Audit Request

```bash
ldf audit --type spec-review --spec user-auth
```

This generates an audit request in `audit-request.md` format.

### Step 2: Send to External Agent

1. Open ChatGPT or Gemini
2. Paste the relevant prompt file (e.g., `prompts/chatgpt/spec-review.md`)
3. Paste the audit request content
4. Submit and wait for response

### Step 3: Process Response

1. Copy the response
2. Create an `audit-response.md` file using the template
3. Triage issues (valid vs invalid)
4. Create action items

### Step 4: Import Feedback

```bash
ldf audit --import audit-response.md --spec user-auth
```

This updates the spec with audit findings.

### Step 5: Address Issues

1. Update specs based on valid issues
2. Re-audit if critical issues were found
3. Close the audit when complete

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  1. Primary AI drafts spec                                  │
│  2. Run: ldf audit --type spec-review --spec [name]         │
│  3. LDF generates audit-request.md                          │
│  4. User copies to ChatGPT/Gemini with prompt               │
│  5. External agent returns structured feedback              │
│  6. User saves feedback as audit-response.md                │
│  7. Run: ldf audit --import audit-response.md               │
│  8. Primary AI incorporates feedback                        │
│  9. Repeat until approved                                   │
└─────────────────────────────────────────────────────────────┘
```

## When to Audit

| Phase | Audit Type | Agent | Trigger |
|-------|------------|-------|---------|
| Requirements | spec-review | ChatGPT | Draft complete |
| Requirements | gap-analysis | Gemini | Before approval |
| Design | architecture | Gemini | Draft complete |
| Design | security | ChatGPT | If security-sensitive |
| Pre-Implementation | edge-cases | Gemini | After design approval |
| Implementation | code-audit | ChatGPT | Before merge |
| Pre-Launch | pre-launch | ChatGPT | Before release |
| Pre-Launch | full | Both | Comprehensive review |

## Audit Templates

| Template | Purpose |
|----------|---------|
| [audit-request.md](templates/audit-request.md) | Structure for sending specs/code to agents |
| [audit-response.md](templates/audit-response.md) | Structure for processing agent feedback |

## Best Practices

### DO
- Run spec-review after every major requirements change
- Run security-check for auth, payment, PII features
- Run architecture review for new services
- Document all audit findings, even if deferred
- Re-audit after significant spec changes

### DON'T
- Skip audits to save time (they catch expensive bugs)
- Accept all findings without review (agents make mistakes)
- Use automation without understanding the prompts
- Ignore "low priority" security findings

## Audit Tracking

Track audits in your spec metadata:

```markdown
## Audit History

| Date | Type | Agent | Result | Issues |
|------|------|-------|--------|--------|
| 2024-01-15 | spec-review | ChatGPT | NEEDS_REVISION | 3 high, 2 medium |
| 2024-01-16 | spec-review | ChatGPT | APPROVE | 0 critical |
| 2024-01-18 | architecture | Gemini | APPROVE | 1 medium |
```

## Automated Workflow (Optional)

For teams wanting API automation, see [automation/README.md](automation/README.md).

**Prerequisites:**
- OpenAI API key (for ChatGPT)
- Google AI API key (for Gemini)
- Configuration in `.ldf/config.yaml`

**Usage:**
```bash
# Automated spec review with ChatGPT
ldf audit --type spec-review --spec user-auth --api --agent chatgpt

# Gap analysis with Gemini
ldf audit --type gap-analysis --spec user-auth --api --agent gemini

# Full audit (all types) with auto-import
ldf audit --type full --api --agent chatgpt --auto-import

# This will:
# 1. Generate audit request
# 2. Send to the specified API
# 3. Parse response
# 4. Save to .ldf/audit-history/
# 5. Auto-import if --auto-import flag is set
```

## FAQ

### Which agent should I use first?
Start with ChatGPT for spec-review, then Gemini for gap-analysis. They catch different issues.

### How long does a review take?
Manual: 10-15 minutes per spec. Automated: 2-3 minutes per spec.

### What if agents disagree?
Review both perspectives. If they disagree on something important, that's valuable signal - investigate further.

### Can I use other agents?
Yes! Create custom prompts in `prompts/[agent-name]/`. The workflow is agent-agnostic.

### Should I audit every spec?
For production features: yes. For prototypes or experiments: use judgment.

## Related

- [LDF Getting Started](../docs/getting-started.md)
- [Spec Templates](../framework/templates/)
- [Guardrails Reference](../framework/guardrails/)
