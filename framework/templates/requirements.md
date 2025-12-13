# {Feature Name} - Requirements

## Overview
[Brief description of feature and its business purpose]

## Question-Pack Answers
**Domains covered:** [List applicable domains from: security, testing, api-design, data-model, billing, multi-tenancy, provisioning, webhooks]
**Answerpack location:** `.ldf/answerpacks/{feature}/*.yaml`

### Key Decisions from Question Packs
- **Security:** [Summary or "N/A"]
- **Testing:** [Summary or "N/A"]
- **API Design:** [Summary or "N/A"]
- **Data Model:** [Summary or "N/A"]
- **[Domain Pack]:** [Add rows for any domain packs used]

### Outstanding Questions / Blocked Items
- [List any questions that couldn't be answered, with assigned owner]
- [Or write "None - all questions resolved"]

## Guardrail Coverage Matrix
**Reference:** `.ldf/guardrails.yaml`

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|---------|-------------|-------|--------|
| 1. Testing Coverage | [Link to US/AC] | [Design section] | [Task #s] | [Name] | TODO |
| 2. Security Basics | | | | | TODO |
| 3. Error Handling | | | | | TODO |
| 4. Logging & Observability | | | | | TODO |
| 5. API Design | | | | | TODO |
| 6. Data Validation | | | | | TODO |
| 7. Database Migrations | | | | | TODO |
| 8. Documentation | | | | | TODO |

**Note:** Mark as "N/A - [reason]" if guardrail not applicable to this feature.
Add rows for any preset-specific guardrails (saas, fintech, healthcare).

## User Stories

### US-1: {Story Title}
**As a** [role]
**I want to** [action]
**So that** [benefit]

**WHEN** [condition/event]
**THE SYSTEM SHALL** [expected behavior]

**WHEN** [error condition]
**THE SYSTEM SHALL** [error handling behavior]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### US-2: {Story Title}
[Repeat format for additional stories]

## Non-Functional Requirements

### Performance
- Response time: < Xms (p95)
- Throughput: X requests/second
- Concurrent users: X

### Security
- Authentication: Required/Optional
- Authorization: [RBAC/ABAC/Custom]
- Data encryption: At rest / In transit / Both
- Sensitive data: [handling requirements]

### Scalability
- Expected growth: [metrics]
- Scaling strategy: Horizontal/Vertical

## Dependencies

### External Services
- [Service Name]: [purpose]

### Database Changes
- New tables: [list]
- Modified tables: [list]

### API Changes
- New endpoints: [list]
- Modified endpoints: [list]

## Open Questions
1. [Question 1]
2. [Question 2]

---
**Status:** Draft | Approved | Implemented
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
