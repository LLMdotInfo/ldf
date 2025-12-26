# LDF Workflow Diagrams

Visual representations of LDF processes and workflows.

---

## Table of Contents

- [The Three-Phase Workflow](#the-three-phase-workflow)
- [Multi-Agent Review Flow](#multi-agent-review-flow)
- [MCP Server Architecture](#mcp-server-architecture)
- [Project Initialization Decision Tree](#project-initialization-decision-tree)
- [When to Use LDF Decision Tree](#when-to-use-ldf-decision-tree)
- [Guardrail Coverage Flow](#guardrail-coverage-flow)
- [Answerpack Generation Flow](#answerpack-generation-flow)

---

## The Three-Phase Workflow

The core LDF methodology: Requirements → Design → Tasks

```
┌─────────────────────────────────────────────────────────────────┐
│                         PHASE 1: REQUIREMENTS                    │
│                                                                  │
│  1. Answer Question-Packs                                       │
│     ├─ security.yaml → answerpacks/feature/security.yaml       │
│     ├─ testing.yaml  → answerpacks/feature/testing.yaml        │
│     └─ ...                                                       │
│                                                                  │
│  2. Write User Stories                                          │
│     "As a [role] I want to [capability] So that [benefit]"     │
│                                                                  │
│  3. Define Acceptance Criteria                                  │
│     - [ ] AC-1.1: Testable, measurable criterion               │
│     - [ ] AC-1.2: Another specific criterion                   │
│                                                                  │
│  4. Create Guardrail Matrix                                     │
│     Show how each of 8 guardrails will be addressed            │
│                                                                  │
│  Output: requirements.md                                         │
│                                                                  │
│  Gate: ✋ APPROVAL REQUIRED before proceeding                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         PHASE 2: DESIGN                          │
│                                                                  │
│  1. Architecture Overview                                       │
│     ASCII diagrams showing system components                    │
│                                                                  │
│  2. Component Definitions                                       │
│     Classes, modules, services with interfaces                  │
│                                                                  │
│  3. Data Models                                                 │
│     Database schemas, fields, relationships                     │
│                                                                  │
│  4. API Contracts                                               │
│     Endpoints, request/response formats                         │
│                                                                  │
│  5. Guardrail Mapping                                           │
│     Map each guardrail to specific design sections              │
│                                                                  │
│  Output: design.md                                              │
│                                                                  │
│  Gate: ✋ APPROVAL REQUIRED before proceeding                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         PHASE 3: TASKS                           │
│                                                                  │
│  1. Break Down Implementation                                   │
│     Phase 1: Setup                                              │
│       - [ ] Task 1.1: Create database migration                │
│       - [ ] Task 1.2: Set up models                            │
│     Phase 2: Core Logic                                         │
│       - [ ] Task 2.1: Implement service layer                  │
│       - [ ] Task 2.2: Add validation                           │
│     Phase 3: API                                                │
│       - [ ] Task 3.1: Create endpoints                         │
│       - [ ] Task 3.2: Add error handling                       │
│     Phase 4: Testing                                            │
│       - [ ] Task 4.1: Unit tests                               │
│       - [ ] Task 4.2: Integration tests                        │
│                                                                  │
│  2. Add Dependencies                                            │
│     Task 2.1 depends on Task 1.1, etc.                         │
│                                                                  │
│  3. Guardrail Checklists                                        │
│     Each task maps to specific guardrails                       │
│                                                                  │
│  Output: tasks.md                                               │
│                                                                  │
│  Status: ✅ READY FOR IMPLEMENTATION                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent Review Flow

How to get external AI review of your specifications

```
┌──────────────┐
│   You write  │
│requirements.md│
└───────┬──────┘
        │
        ├──────────────────┐
        │                  │
        v                  v
┌──────────────┐    ┌──────────────┐
│   ChatGPT    │    │    Gemini    │
│ Spec Review  │    │ Gap Analysis │
└───────┬──────┘    └───────┬──────┘
        │                   │
        v                   v
  ┌─────────┐         ┌─────────┐
  │Feedback │         │Feedback │
  │   #1    │         │   #2    │
  └────┬────┘         └────┬────┘
       │                   │
       └─────────┬─────────┘
                 │
                 v
          ┌──────────────┐
          │  ldf audit   │
          │  --import    │
          └──────┬───────┘
                 │
                 v
          ┌──────────────┐
          │   Refine     │
          │requirements.md│
          └──────┬───────┘
                 │
                 v
          ┌──────────────┐
          │   Proceed    │
          │  to Design   │
          └──────────────┘
```

**Commands:**

```bash
# Generate audit request
ldf audit --type spec-review

# Copy output to ChatGPT or Gemini

# Import feedback
ldf audit --import feedback.md
```

---

## MCP Server Architecture

How Model Context Protocol reduces token usage by 90%

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant (Claude Code)                │
│                                                              │
│  "What's the status of user-auth spec?"                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ MCP Protocol
                  │ (200 tokens)
                  v
┌─────────────────────────────────────────────────────────────┐
│                     spec_inspector MCP Server                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Get Spec     │  │ List Tasks   │  │ Check        │     │
│  │ Status       │  │              │  │ Guardrails   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Reads
                  v
┌─────────────────────────────────────────────────────────────┐
│                    Your Project Files                        │
│                                                              │
│  .ldf/                                                       │
│  ├── config.yaml                                            │
│  ├── guardrails.yaml                                        │
│  └── specs/user-auth/                                       │
│      ├── requirements.md                                    │
│      ├── design.md                                          │
│      └── tasks.md                                           │
└─────────────────────────────────────────────────────────────┘

Without MCP: AI reads entire files (5,000 tokens)
With MCP:    Server returns summary (200 tokens)
Savings:     96% fewer tokens
```

**Setup:**

```bash
pip install llm-ldf[mcp]
ldf mcp-config > .agent/mcp.json
```

---

## Project Initialization Decision Tree

Choosing the right initialization approach

```
                    Start New Project
                           │
                           v
                  Do you have existing code?
                     /              \
                   Yes               No
                   │                 │
                   v                 v
            ┌───────────┐      ┌──────────┐
            │ldf convert│      │ ldf init │
            │  analyze  │      └────┬─────┘
            └─────┬─────┘           │
                  │                 │
                  v                 v
            ┌───────────┐    Choose preset?
            │ Send to AI│      /    |    \
            │  for spec │   SaaS Fintech Healthcare
            │ generation│     │     │      │
            └─────┬─────┘     v     v      v
                  │         (Each adds domain
                  │          specific guardrails)
                  v                 │
            ┌───────────┐           │
            │ldf convert│           │
            │  import   │           │
            └─────┬─────┘           │
                  │                 │
                  └────────┬────────┘
                           │
                           v
                    ┌──────────────┐
                    │ Ready to     │
                    │ create specs │
                    └──────────────┘
```

**Commands:**

```bash
# New project without code
ldf init --preset saas

# Existing project
ldf convert analyze > prompt.md
# Send prompt.md to AI, save response
ldf convert import response.md
```

---

## When to Use LDF Decision Tree

Determining if a change needs full LDF workflow

```
                    New Change Needed
                           │
                           v
                  What type of change?
                   /        |        \
                  /         |         \
              Bug Fix   Small Task   New Feature
                │          │              │
                v          v              v
          Link to      Document       Use Full
          GitHub      in commit        LDF Spec
          Issue        message        Process
                │          │              │
                v          v              v
              SKIP      SKIP         Requirements
              LDF       LDF               │
                                          v
                                      Design
                                          │
                                          v
                                      Tasks
                                          │
                                          v
                                    Implement

Additional considerations:

Security-sensitive?  ────────► Always use LDF
Public API?         ────────► Always use LDF
Database migration? ────────► Always use LDF
>200 lines of code? ────────► Probably use LDF
Team collaboration? ────────► Probably use LDF
```

**Use LDF for:**
- ✅ New features
- ✅ Security-sensitive changes
- ✅ Public APIs
- ✅ Database schema changes
- ✅ Changes >200 LOC

**Skip LDF for:**
- ❌ Bug fixes (link to issue)
- ❌ Documentation updates
- ❌ Config changes
- ❌ Small refactorings

---

## Guardrail Coverage Flow

How to complete the guardrail coverage matrix

```
                    Start Spec
                        │
                        v
              ┌─────────────────┐
              │  8 Core         │
              │  Guardrails     │
              │  ├─ Testing     │
              │  ├─ Security    │
              │  ├─ Errors      │
              │  ├─ Logging     │
              │  ├─ API Design  │
              │  ├─ Validation  │
              │  ├─ DB Migrations│
              │  └─ Docs        │
              └────────┬────────┘
                       │
                       v
              Is preset active?
                  /        \
                Yes         No
                │            │
                v            │
        Add preset guardrails│
        ├─ SaaS: +5          │
        ├─ Fintech: +7       │
        ├─ Healthcare: +6    │
        └─ API-only: +4      │
                │            │
                └─────┬──────┘
                      │
                      v
        For each guardrail, answer:
        1. Is it applicable? (Yes/N/A)
        2. Where in requirements?
        3. Where in design?
        4. Which tasks cover it?
        5. Who owns it?
        6. What's status?
                      │
                      v
              ┌──────────────┐
              │  Complete    │
              │  Coverage    │
              │  Matrix      │
              └──────────────┘
```

**Example matrix:** See [Guardrail Examples](guardrail-examples.md)

---

## Answerpack Generation Flow

How question-packs become answerpacks

```
Start spec creation
        │
        v
┌───────────────┐
│ Clarify-First │
│    Macro      │
└───────┬───────┘
        │
        v
Identify relevant
question-packs based
on feature type
        │
        ├─── Always: security, testing
        ├─── If API: api-design
        ├─── If DB: data-model
        └─── Optional: billing, multi-tenancy, etc.
        │
        v
For each pack:
        │
        ├─── Load questions from
        │    .ldf/question-packs/{pack}.yaml
        │
        v
User answers questions
(or AI answers with user review)
        │
        v
Answers saved to:
.ldf/answerpacks/{feature}/{pack}.yaml
        │
        v
Summary included in
requirements.md under
"Question-Pack Answers"
        │
        v
ldf lint validates:
├─ All critical questions answered
├─ No [TBD] markers
└─ Answerpacks exist for declared packs
```

**Files involved:**

```
.ldf/
├── question-packs/
│   ├── core/
│   │   ├── security.yaml        # Template
│   │   ├── testing.yaml         # Template
│   │   └── ...
│   └── optional/
│       └── ...
└── answerpacks/
    └── user-auth/
        ├── security.yaml        # Your answers
        ├── testing.yaml         # Your answers
        └── ...
```

---

## Status Tracking Flow

How spec status progresses through phases

```
┌─────────────┐
│ Create Spec │
│  ldf create │
└──────┬──────┘
       │
       v
┌──────────────────────┐
│ Status: requirements │  ← You are here after create-spec
│ Phase: 1             │
│ Files: 1/3 (33%)     │
└──────┬───────────────┘
       │
       │ Edit requirements.md
       │ Run ldf lint
       v
┌──────────────────────┐
│ Status: ready for    │  ← After requirements validated
│         design       │
│ Phase: 1 (complete)  │
│ Files: 1/3 (33%)     │
└──────┬───────────────┘
       │
       │ Create design.md
       │ Run ldf lint
       v
┌──────────────────────┐
│ Status: ready for    │  ← After design validated
│         tasks        │
│ Phase: 2 (complete)  │
│ Files: 2/3 (67%)     │
└──────┬───────────────┘
       │
       │ Create tasks.md
       │ Run ldf lint
       v
┌──────────────────────┐
│ Status: ready for    │  ← All three phases complete
│     implementation   │
│ Phase: 3 (complete)  │
│ Files: 3/3 (100%)    │
└──────┬───────────────┘
       │
       │ Implement tasks
       │ Check off task items
       v
┌──────────────────────┐
│ Status: in progress  │  ← During implementation
│ Tasks: 5/12 (42%)    │
└──────┬───────────────┘
       │
       │ Complete all tasks
       v
┌──────────────────────┐
│ Status: complete     │  ← Feature finished
│ Tasks: 12/12 (100%)  │
└──────────────────────┘
```

**Check status:**

```bash
ldf status
```

---

## CI/CD Integration Flow

How LDF fits into your pipeline

```
Developer commits
       │
       v
┌──────────────┐
│ Git Push     │
└──────┬───────┘
       │
       v
┌─────────────────────────────────┐
│ GitHub Actions / GitLab CI       │
│                                  │
│ 1. Install LDF                   │
│    pip install llm-ldf               │
│                                  │
│ 2. Lint all specs                │
│    ldf lint --all --format ci    │
│                                  │
│ 3. Check coverage (optional)     │
│    ldf coverage --fail-under 80  │
│                                  │
│ 4. Run automated audit (optional)│
│    ldf audit --api --type security│
└─────────┬───────────────────────┘
          │
          ├─── Pass ─────> ✅ Build continues
          │
          └─── Fail ─────> ❌ Build fails
                              │
                              v
                         Block merge/deploy
```

**Setup:**

See [CI/CD Integration](/integrations/ci-cd/README.md)

---

## Preset Selection Decision Tree

Choosing the right guardrail preset

```
START → What are you building?
           │
           ├─── Multi-tenant SaaS app?
           │         │
           │         Yes ──> Use "saas" preset
           │                 ├─ Row-Level Security
           │                 ├─ Tenant Isolation
           │                 ├─ Audit Logging
           │                 ├─ Subscription Checks
           │                 └─ Tenant Data Separation
           │
           ├─── Financial/Payment app?
           │         │
           │         Yes ──> Use "fintech" preset
           │                 ├─ Double-Entry Ledger
           │                 ├─ Money Precision
           │                 ├─ Idempotency
           │                 ├─ Reconciliation
           │                 ├─ PCI Compliance
           │                 ├─ Transaction Rollback
           │                 └─ Audit Trail
           │
           ├─── Healthcare app with PHI?
           │         │
           │         Yes ──> Use "healthcare" preset
           │                 ├─ HIPAA Compliance
           │                 ├─ PHI Handling
           │                 ├─ Access Logging
           │                 ├─ Consent Management
           │                 ├─ Data Encryption
           │                 └─ Audit Trail
           │
           ├─── API-only service?
           │         │
           │         Yes ──> Use "api-only" preset
           │                 ├─ Rate Limiting
           │                 ├─ API Versioning
           │                 ├─ OpenAPI Docs
           │                 └─ Webhook Signatures
           │
           └─── None of the above?
                     │
                     Yes ──> Use "custom" (core only)
                             └─ 8 core guardrails only
```

**Apply preset:**

```bash
ldf init --preset saas
```

---

## Workflow Timing Examples

**Small Feature** (GET /hello endpoint):
```
Requirements: 15 minutes
Design:       10 minutes
Tasks:        10 minutes
Total Spec:   35 minutes
Implementation: 30 minutes
```

**Medium Feature** (User authentication):
```
Requirements: 60 minutes
Design:       45 minutes
Tasks:        30 minutes
Total Spec:   135 minutes (2.25 hours)
Implementation: 4-6 hours
```

**Large Feature** (Multi-tenant billing):
```
Requirements: 3 hours
Design:       4 hours
Tasks:        2 hours
Total Spec:   9 hours
Implementation: 20-30 hours
```

**ROI:** Spec time prevents bugs, reduces rework, enables AI assistance. Typical ROI: 3-5x time saved vs. ad-hoc development.

---

## Related Documentation

- **[Guardrail Examples](guardrail-examples.md)** - Real coverage matrices
- **[First Spec Tutorial](../tutorials/01-first-spec.md)** - Step-by-step walkthrough
- **[Concepts Guide](../concepts.md)** - Philosophy and methodology
- **[Multi-Agent Workflow](../multi-agent-workflow.md)** - Using ChatGPT/Gemini

---

**Need more visuals?** Request diagrams via [GitHub Issues](https://github.com/LLMdotInfo/ldf/issues) with label `documentation`.
