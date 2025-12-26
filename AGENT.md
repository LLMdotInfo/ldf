# Project Instructions for Claude Code

## Project Overview
**Name:** ldf
**Framework:** LDF (LLM Development Framework)
**Preset:** custom
**Initialized:** 2025-12-25

---

## Development Methodology

This project uses **LDF** - a spec-driven development approach with three phases:

### Phase 1: Requirements
- **Location:** `.ldf/specs/{feature}/requirements.md`
- **Template:** `.ldf/templates/requirements.md`
- **Command:** `/project:create-spec {feature-name}`

### Phase 2: Design
- **Location:** `.ldf/specs/{feature}/design.md`
- **Template:** `.ldf/templates/design.md`

### Phase 3: Tasks
- **Location:** `.ldf/specs/{feature}/tasks.md`
- **Template:** `.ldf/templates/tasks.md`

**CRITICAL RULE:** Do NOT write code until all three phases are approved.

---

## Guardrails

This project enforces the following guardrails (see `.ldf/guardrails.yaml`):

### Core Guardrails (Always Active)
1. **Testing Coverage** - Minimum 80% coverage
2. **Security Basics** - OWASP Top 10 prevention
3. **Error Handling** - Consistent error responses
4. **Logging & Observability** - Structured logging, correlation IDs
5. **API Design** - Versioning, pagination, error format
6. **Data Validation** - Input validation at boundaries
7. **Database Migrations** - Reversible, separate from backfills
8. **Documentation** - API docs, inline comments

### Preset Guardrails (custom)
See `.ldf/guardrails.yaml` for additional guardrails from the custom preset.

---

## Question Packs

Before writing requirements, answer questions from these packs:
- `security`
- `testing`
- `api-design`
- `data-model`

Answers are captured in `.ldf/answerpacks/{feature}/`.

---

## Custom Commands

### `/project:create-spec {feature-name}`
Create a new feature specification:
1. Load relevant question-packs
2. Ask clarifying questions (clarify-first macro)
3. Generate requirements.md
4. Wait for approval
5. Generate design.md
6. Wait for approval
7. Generate tasks.md
8. Ready for implementation

### `/project:implement-task {spec-name} {task-number}`
Implement a specific task:
1. Load spec context
2. Check dependencies
3. Run task-guardrails macro
4. Implement code + tests
5. Update task status

### `/project:review-spec {spec-name}`
Review spec for completeness:
1. Run coverage-gate macro
2. Validate guardrail coverage matrix
3. Check answerpacks populated
4. Report issues

---

## Validation

```bash
ldf lint                  # Validate all specs
ldf lint {spec-name}    # Validate single spec
ldf audit --type spec-review  # Generate audit for other AI
```

---

## Notes for Claude

- **Read specs first:** Always check `.ldf/specs/` before coding
- **Respect phases:** Don't skip requirements → design → tasks
- **Use macros:** Run clarify-first, coverage-gate, task-guardrails
- **Test after changes:** Verify coverage meets thresholds
- **Commit incrementally:** Commit after each completed task
- **Update progress:** Mark tasks complete in tasks.md

**Development Flow:** Plan → Design → Task → Implement → Test → Commit
