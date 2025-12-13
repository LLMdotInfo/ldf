# LDF Concepts

Understanding the philosophy and methodology behind LDF.

## Core Principle: Spec-First Development

**No code without approved specifications.**

This isn't about bureaucracy - it's about:
1. **Clarity**: Everyone understands what we're building
2. **Quality**: Catch issues before they become bugs
3. **Efficiency**: Less rework, faster delivery
4. **Knowledge**: Specs serve as documentation

## The Three Phases

### Phase 1: Requirements

**Goal:** Define WHAT we're building

**Contents:**
- User stories in "As a... I want to... So that..." format
- Acceptance criteria (measurable, testable)
- Question-pack answers (domain-specific decisions)
- Guardrail coverage matrix

**Output:** `requirements.md`

**Approval Gate:** Spec review by external agent or team

### Phase 2: Design

**Goal:** Define HOW we're building it

**Contents:**
- Architecture overview
- Component definitions
- Data models
- API contracts
- Guardrail mapping

**Output:** `design.md`

**Approval Gate:** Architecture review

### Phase 3: Tasks

**Goal:** Define the implementation steps

**Contents:**
- Numbered task list
- Dependencies between tasks
- Guardrail checklist per task
- Testing requirements

**Output:** `tasks.md`

**Approval Gate:** Ready for implementation

## Guardrails

Guardrails are constraints that ensure quality. They're not optional - they're requirements.

### Core Guardrails (Always Enabled)

| ID | Name | Description |
|----|------|-------------|
| 1 | Testing Coverage | Minimum 80% coverage, 90% for critical paths |
| 2 | Security Basics | OWASP Top 10 prevention |
| 3 | Error Handling | Consistent error responses, no swallowed exceptions |
| 4 | Logging & Observability | Structured logging, correlation IDs |
| 5 | API Design | Versioning, pagination, error format |
| 6 | Data Validation | Input validation at boundaries |
| 7 | Database Migrations | Reversible, separate from backfills |
| 8 | Documentation | API docs, README, inline comments |

### Domain Presets

Additional guardrails for specific domains:

**SaaS Preset:**
- Multi-tenancy isolation
- RLS enforcement
- Subscription billing
- Audit logging

**Fintech Preset:**
- Double-entry ledger
- Money precision (NUMERIC)
- Idempotency
- Reconciliation

**Healthcare Preset:**
- HIPAA compliance
- PHI handling
- Access logging
- Consent management

### Guardrail Coverage Matrix

Every spec must include a matrix showing how each guardrail is addressed:

```markdown
| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing | [US-1] | [S3.1] | [T-4.1] | Alice | DONE |
| 2. Security | [US-2] | [S4.1] | [T-5.1] | Bob | TODO |
```

## Question-Packs

Question-packs ensure critical decisions are made early.

### How They Work

1. When creating a spec, LDF identifies relevant question-packs
2. You answer questions before writing requirements
3. Answers are captured in answerpacks (YAML)
4. Linter verifies all critical questions are answered

### Example Question-Pack (Security)

```yaml
domain: security
critical: true
questions:
  authentication:
    - question: "What authentication method will be used?"
      options:
        - "Username/password with bcrypt"
        - "OAuth 2.0 / OpenID Connect"
        - "API keys"
        - "Service JWT"
      follow_ups:
        - "What is the session duration?"
        - "Is MFA required?"
```

### When to Use Each Pack

| Pack | Use When |
|------|----------|
| security | Always |
| testing | Always |
| api-design | Building APIs |
| data-model | Database changes |
| billing | Payment/subscription features |
| multi-tenancy | Multi-tenant systems |
| provisioning | External service integration |
| webhooks | Event-driven features |

## Multi-Agent Workflow

LDF supports using multiple AI agents for review and validation.

### Agent Roles

| Agent | Strength | Use For |
|-------|----------|---------|
| Your Primary Tool | Implementation, context | Primary development |
| ChatGPT | Patterns, alternatives | Spec review, code audit |
| Gemini | Edge cases, gaps | Architecture, completeness |

**Supported primary tools:** Claude Code, Gemini CLI, Codex CLI, Cursor, or any MCP-compatible assistant.

### Why Multiple Agents?

1. **Different perspectives**: Each model has unique strengths
2. **Catch blind spots**: What one misses, another catches
3. **Validation**: Independent review reduces errors
4. **Quality**: Multiple passes improve output

### Audit Triggers

| Phase | Audit Type | Agent |
|-------|------------|-------|
| Requirements complete | spec-review | ChatGPT |
| Requirements complete | gap-analysis | Gemini |
| Design complete | architecture | Gemini |
| Security feature | security-check | ChatGPT |
| Before implementation | edge-cases | Gemini |
| Code complete | code-audit | ChatGPT |

## MCP Integration

MCP (Model Context Protocol) servers provide real-time access to spec status and coverage.

### Token Efficiency

| Operation | Without MCP | With MCP | Savings |
|-----------|-------------|----------|---------|
| Get spec status | ~5,000 tokens | ~200 tokens | 96% |
| List tasks | ~3,000 tokens | ~150 tokens | 95% |
| Check coverage | ~10,000 tokens | ~200 tokens | 98% |

### Available Servers

1. **spec-inspector**: Spec status, guardrails, tasks
2. **coverage-reporter**: Test coverage metrics
3. **db-inspector**: Database schema, RLS policies (optional)

## Best Practices

### DO

- Write specs before code
- Answer all question-pack questions
- Complete guardrail matrix before approval
- Run lint before requesting review
- Get external audit for significant features
- Update specs when requirements change
- Mark tasks complete as you go

### DON'T

- Skip phases to save time
- Leave guardrails marked N/A without justification
- Ignore audit findings
- Let specs get out of sync with code
- Over-engineer the spec process for small changes

## When LDF is Overkill

Not everything needs full spec treatment:

**Use full LDF for:**
- New features
- Significant changes
- Security-sensitive code
- External-facing APIs
- Database migrations

**Lighter touch for:**
- Bug fixes (link to issue)
- Refactoring (describe in commit)
- Documentation updates
- Config changes
- Dependency updates

## Measuring Success

### Spec Quality Metrics

- **Completion Rate**: % of specs that reach implementation
- **Rework Rate**: Changes after design approval
- **Bug Escape Rate**: Issues found post-implementation
- **Coverage Score**: Average guardrail coverage

### Project Health Indicators

| Indicator | Healthy | Warning | Critical |
|-----------|---------|---------|----------|
| Specs in draft | < 20% | 20-40% | > 40% |
| Test coverage | > 80% | 60-80% | < 60% |
| Guardrail gaps | 0 | 1-2 | > 2 |
| Audit response time | < 24h | 24-48h | > 48h |

## Evolution of LDF

LDF is designed to evolve with your project:

1. **Start Simple**: Core guardrails only
2. **Add Domain Presets**: As complexity grows
3. **Custom Question-Packs**: For your specific domain
4. **Automated Audits**: When volume justifies
5. **CI/CD Integration**: For continuous validation

The goal is appropriate rigor, not maximum process.
