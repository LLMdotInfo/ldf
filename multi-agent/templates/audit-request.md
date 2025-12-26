# Audit Request Template

Use this template when sending specs or code to an external AI agent for review.

---

## Audit Request

**Request ID:** [generated or manual]
**Date:** [YYYY-MM-DD]
**Requested By:** [your name]
**Audit Type:** [SPEC_REVIEW | CODE_AUDIT | SECURITY_CHECK | GAP_ANALYSIS | EDGE_CASES | ARCHITECTURE]

### Context

**Project:** [project name]
**Feature:** [feature name]
**Spec Location:** [path to spec]
**Current Phase:** [REQUIREMENTS | DESIGN | IMPLEMENTATION | PRE_LAUNCH]

### What to Review

[Brief description of what you want reviewed]

### Specific Concerns

Please pay special attention to:
1. [Specific area of concern]
2. [Another area]
3. [Third area if applicable]

### Guardrails in Scope

The following guardrails apply to this feature:
- [ ] Guardrail 1: [name]
- [ ] Guardrail 2: [name]
- [ ] Guardrail 3: [name]

### Constraints

- **Technology Stack:** [languages, frameworks]
- **Deployment Target:** [cloud provider, on-prem]
- **Scale Requirements:** [expected load]
- **Compliance:** [any regulations: GDPR, HIPAA, SOC2]

### Attachments

#### Requirements Document
```markdown
[Paste or attach requirements.md content]
```

#### Design Document
```markdown
[Paste or attach design.md content]
```

#### Code to Review
```[language]
[Paste relevant code sections]
```

### Expected Output Format

Please follow the response format specified in the corresponding prompt:
- Spec Review: [link to spec-review.md output format]
- Code Audit: [link to code-audit.md output format]
- Security Check: [link to security-check.md output format]
- Gap Analysis: [link to gap-analysis.md output format]
- Edge Cases: [link to edge-cases.md output format]
- Architecture: [link to architecture.md output format]

### Timeline

**Response Needed By:** [date]
**Priority:** [LOW | MEDIUM | HIGH | CRITICAL]

---

## Usage Instructions

1. Copy this template
2. Fill in all sections
3. Attach the relevant spec/code content
4. Include the appropriate prompt file (e.g., `chatgpt/spec-review.md`)
5. Send to the audit agent
6. Process the response using `audit-response.md` template

## Example: Spec Review Request

```markdown
## Audit Request

**Request ID:** AUDIT-2024-001
**Date:** 2024-01-15
**Requested By:** Jane Developer
**Audit Type:** SPEC_REVIEW

### Context

**Project:** Customer Portal
**Feature:** Password Reset
**Spec Location:** .ldf/specs/password-reset/requirements.md
**Current Phase:** REQUIREMENTS

### What to Review

Review the password reset feature requirements for completeness
and security considerations.

### Specific Concerns

Please pay special attention to:
1. Security implications of the reset flow
2. Edge cases around account states (locked, disabled)
3. Rate limiting to prevent abuse

### Guardrails in Scope

- [x] Guardrail 2: Security Basics
- [x] Guardrail 3: Error Handling
- [x] Guardrail 7: Authentication

### Constraints

- **Technology Stack:** Python/FastAPI, React
- **Deployment Target:** AWS
- **Scale Requirements:** 10k users, ~100 resets/day
- **Compliance:** SOC2

### Attachments

#### Requirements Document
[content of requirements.md]

### Timeline

**Response Needed By:** 2024-01-17
**Priority:** MEDIUM
```
