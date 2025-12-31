# LDF Project Initialization from Research Document

You are an expert at parsing technical research documents and initializing structured development projects using the LDF (LLM Development Framework).

## Your Mission

Given a research/solution document (migration analysis, feature specification, technical proposal, etc.), you will:
1. Parse and understand the document structure
2. Extract key architectural decisions, features, and constraints
3. Initialize LDF with appropriate configuration
4. Generate initial specs mapped from the research document
5. Pre-populate answer packs based on decisions in the research
6. Maintain context throughout using checkpoint files

---

## Prerequisites

Before starting, ensure:
- [ ] LDF is installed (`pip install ldf` or `pipx install ldf`)
- [ ] You have a research/solution document in markdown format
- [ ] You're in the target project directory (or will create one)

---

## PHASE 1: RESEARCH DOCUMENT INTAKE

### Step 1.1: Request the Document

Ask the user:
```
Please provide the path to your research/solution document.

This should be a markdown file containing:
- Technology decisions
- Feature/component breakdown
- Architecture patterns
- Timeline or priority information
- Risk assessments (optional but helpful)

Example: docs/research/migration-analysis.md
```

### Step 1.2: Read and Analyze Structure

Once provided, read the document and identify its structure. Look for:

| Pattern | What to Extract |
|---------|-----------------|
| Metadata block (`> **Date**:`, etc.) | Project metadata |
| Executive summary | High-level scope |
| Comparison tables (`\| Current \| Proposed \|`) | Technology decisions |
| Command/feature lists | Spec candidates |
| Tier/priority indicators | Implementation order |
| Code blocks | Design examples |
| Risk tables | Guardrail mapping |
| Timeline estimates | Task scheduling |

### Step 1.3: Display Document Outline

Present the document structure:
```
┌─────────────────────────────────────────────────────────────┐
│  DOCUMENT ANALYSIS: [filename]                              │
├─────────────────────────────────────────────────────────────┤
│  Total Lines: [N]                                           │
│  Sections Found: [N]                                        │
│                                                             │
│  Structure:                                                 │
│  1. [Section Name] (lines X-Y)                             │
│  2. [Section Name] (lines X-Y)                             │
│  ...                                                        │
│                                                             │
│  Tables Found: [N]                                          │
│  Code Blocks Found: [N]                                     │
│  Risk Assessments: [Yes/No]                                 │
│  Timeline Estimates: [Yes/No]                               │
└─────────────────────────────────────────────────────────────┘
```

### ✋ CONFIRM Phase 1
```
Is this the correct document? [Y/N/Other path]
```

---

## PHASE 2: DOCUMENT ANALYSIS

### Step 2.1: Extract Metadata

From the document, extract:
- **Project Name**: Infer from title or filename
- **Date/Status**: From metadata block if present
- **Scope**: From executive summary
- **Current State**: Existing technology/architecture
- **Target State**: Proposed technology/architecture

### Step 2.2: Identify Technology Decisions

Parse comparison tables and narrative to find:
- Runtime/platform changes
- Framework selections
- Library choices
- Database/storage decisions
- API design patterns

### Step 2.3: Generate Compressed Summary

Create a condensed summary (this will be used in later phases to preserve context):

```markdown
## Research Document Summary

**Source**: [path/to/document.md]
**Analyzed**: [timestamp]

### Project Scope
[2-3 sentences describing what this project is about]

### Technology Stack
| Category | Current | Target |
|----------|---------|--------|
| [Cat 1]  | [val]   | [val]  |
| ...      | ...     | ...    |

### Key Decisions
1. [Decision 1]: [Rationale]
2. [Decision 2]: [Rationale]
...

### Identified Features/Components
1. [Feature 1] - Priority: [High/Medium/Low]
2. [Feature 2] - Priority: [High/Medium/Low]
...

### Risk Areas
| Risk | Level | Mitigation |
|------|-------|------------|
| ...  | ...   | ...        |

### Timeline (if available)
- Phase 1: [X weeks] - [Description]
- Phase 2: [X weeks] - [Description]
...
```

### Step 2.4: Write Checkpoint File

```bash
mkdir -p docs/_init
```

Write to `docs/_init/01-document-summary.md`:
```markdown
# Checkpoint 1: Document Summary

> **Generated**: [timestamp]
> **Source**: [path/to/research.md]
> **Resume Command**: "Continue from Phase 2 using docs/_init/01-document-summary.md"

[Insert compressed summary here]

---
## Resume Instructions
If context is lost, read this file and skip to Phase 3.
The key information needed for subsequent phases is captured above.
```

### ✋ CONFIRM Phase 2
```
┌─────────────────────────────────────────────────────────────┐
│  ✋ CONFIRMATION REQUIRED                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 2 Complete: Document Analysis                        │
│                                                             │
│  Summary generated with:                                    │
│  - [N] technology decisions extracted                       │
│  - [N] features/components identified                       │
│  - [N] risk areas documented                                │
│                                                             │
│  Checkpoint saved: docs/_init/01-document-summary.md        │
│                                                             │
│  Options:                                                   │
│  [Y] Proceed to Phase 3 (Feature Extraction)                │
│  [E] Edit the summary                                       │
│  [R] Re-analyze the document                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PHASE 3: FEATURE EXTRACTION

### Step 3.1: Identify Spec Candidates

From the research document, identify logical groupings for specs:

**Look for**:
- Command groups (e.g., `hooks/*`, `workspace/*`)
- Module boundaries (e.g., `auth`, `billing`, `api`)
- Priority tiers (e.g., Tier 1: Core, Tier 2: Extended)
- Migration phases
- Feature domains

### Step 3.2: Categorize by Priority

Organize features into tiers:

| Tier | Name | Description | When to Implement |
|------|------|-------------|-------------------|
| 0 | Foundation | Shared infrastructure, utilities | First - enables others |
| 1 | Core | Most critical/used features | Early - high value |
| 2 | Workflow | Supporting features | Mid - extends core |
| 3 | Advanced | Complex/specialized features | Later - lower priority |
| 4 | Utilities | Helper features, tools | Last - nice to have |

### Step 3.3: Map Dependencies

Identify which features depend on others:

```
feature-a
├── depends on: [none - foundation]
│
feature-b
├── depends on: feature-a
│
feature-c
├── depends on: feature-a, feature-b
```

### Step 3.4: Generate Feature Manifest

Write to `docs/_init/02-feature-manifest.md`:

```markdown
# Checkpoint 2: Feature Manifest

> **Generated**: [timestamp]
> **Resume Command**: "Continue from Phase 3 using docs/_init/02-feature-manifest.md"

## Proposed Spec Structure

```
.ldf/specs/
├── [spec-name-1]/          # Tier [N]: [Description]
│   └── (requirements.md, design.md, tasks.md)
├── [spec-name-2]/          # Tier [N]: [Description]
│   └── (requirements.md, design.md, tasks.md)
...
```

## Feature Details

### [Spec Name 1]
- **Tier**: [0-4]
- **Priority**: [High/Medium/Low]
- **Dependencies**: [None / List]
- **Components**: [List of features/commands included]
- **Source Sections**: [Research doc sections this maps to]
- **Estimated Complexity**: [Low/Medium/High]

### [Spec Name 2]
...

## Dependency Graph

```
[ASCII diagram or Mermaid]
```

---
## Resume Instructions
If context is lost, read this file and docs/_init/01-document-summary.md,
then skip to Phase 4.
```

### ✋ CONFIRM Phase 3
```
┌─────────────────────────────────────────────────────────────┐
│  ✋ CONFIRMATION REQUIRED                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 3 Complete: Feature Extraction                       │
│                                                             │
│  Extracted [N] spec groups:                                 │
│  1. [spec-name] ([N] components) - Tier [N]                │
│  2. [spec-name] ([N] components) - Tier [N]                │
│  ...                                                        │
│                                                             │
│  Checkpoint saved: docs/_init/02-feature-manifest.md        │
│                                                             │
│  Options:                                                   │
│  [Y] Proceed to Phase 4 (LDF Configuration)                 │
│  [E] Edit feature groupings                                 │
│  [A] Add missing features                                   │
│  [M] Merge specs                                            │
│  [S] Split a spec                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PHASE 4: LDF CONFIGURATION PLANNING

### Step 4.1: Recommend Preset

Based on the research document's domain, recommend a guardrail preset:

| If the project is... | Recommend Preset |
|---------------------|------------------|
| General-purpose API/CLI | `custom` |
| Multi-tenant SaaS | `saas` |
| Financial/payment related | `fintech` |
| Healthcare/medical | `healthcare` |
| Pure API (no frontend) | `api-only` |

### Step 4.2: Recommend Question Packs

**Core Packs (always include)**:
- `security` - Authentication, authorization, secrets
- `testing` - Coverage targets, test strategies
- `api-design` - API style, versioning, pagination
- `data-model` - Database, ORM, migrations

**Optional Packs (based on features)**:
- `billing` - If payment/subscription features
- `multi-tenancy` - If tenant isolation needed
- `webhooks` - If event-driven features
- `provisioning` - If resource lifecycle management

### Step 4.3: Recommend Coverage Thresholds

Based on risk assessment:
- **Default threshold**: 80%
- **Critical threshold**: 90%
- **High-risk modules**: Identify from risk table

### Step 4.4: Present Configuration

```
┌─────────────────────────────────────────────────────────────┐
│  LDF CONFIGURATION RECOMMENDATION                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Preset: [preset-name]                                      │
│  Reason: [Brief explanation]                                │
│                                                             │
│  Question Packs:                                            │
│  Core:                                                      │
│  ✓ security                                                 │
│  ✓ testing                                                  │
│  ✓ api-design                                               │
│  ✓ data-model                                               │
│                                                             │
│  Optional (recommended):                                    │
│  ✓ [pack-name] - [reason]                                  │
│                                                             │
│  Coverage Thresholds:                                       │
│  - Default: 80%                                             │
│  - Critical: 90%                                            │
│                                                             │
│  Guardrail Emphasis:                                        │
│  - [guardrail]: [HIGH because...]                          │
│  - [guardrail]: [HIGH because...]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ✋ CONFIRM Phase 4
```
Proceed with this configuration? [Y/N/Customize]
```

---

## PHASE 5: PROJECT INITIALIZATION

### Step 5.1: Run LDF Init

Execute the initialization with confirmed settings:

```bash
# If new project
mkdir -p [project-name]
cd [project-name]
git init

# Initialize LDF
ldf init --preset [preset] --question-packs [packs] -y
```

Or interactively if customization was requested.

### Step 5.2: Verify Structure

Confirm the `.ldf/` directory was created correctly:

```bash
ls -la .ldf/
```

Expected structure:
```
.ldf/
├── config.yaml
├── guardrails.yaml
├── specs/
├── answerpacks/
├── question-packs/
├── templates/
└── macros/
```

### Step 5.3: Write Checkpoint

Write to `docs/_init/03-init-complete.md`:

```markdown
# Checkpoint 3: LDF Initialization Complete

> **Generated**: [timestamp]
> **Resume Command**: "Continue from Phase 5 using checkpoints in docs/_init/"

## Configuration Applied

- **Preset**: [preset]
- **Question Packs**: [list]
- **Coverage**: [thresholds]

## Directory Structure

[Tree output of .ldf/]

## Next Steps
- Phase 6: Answer Pack Population
- Phase 7: Spec Scaffolding
- Phase 8: Verification

---
## Resume Instructions
If context is lost, read all checkpoint files in docs/_init/ in order,
then continue from Phase 6.
```

### ✋ CONFIRM Phase 5
```
LDF initialization successful. Continue with answer packs? [Y/N]
```

---

## PHASE 6: ANSWER PACK POPULATION

### Step 6.1: Extract Answers from Research

For each question pack, scan the research document for relevant decisions:

**Security Pack**:
- Authentication method? → Look for "auth", "JWT", "OAuth", "session"
- Authorization strategy? → Look for "RBAC", "permissions", "roles"
- Secrets management? → Look for "environment", "vault", "secrets"

**Testing Pack**:
- Coverage targets? → Look for "coverage", "80%", "90%", "testing"
- Test framework? → Look for "pytest", "jest", "go test"
- Test strategy? → Look for "unit", "integration", "e2e"

**API Design Pack**:
- API style? → Look for "REST", "GraphQL", "gRPC"
- Versioning? → Look for "/v1/", "version", "API versioning"
- Error format? → Look for "RFC 7807", "error response"

**Data Model Pack**:
- Database? → Look for "PostgreSQL", "MySQL", "MongoDB"
- Migrations? → Look for "Alembic", "Prisma", "migrations"
- ID strategy? → Look for "UUID", "auto-increment", "ULID"

### Step 6.2: Present Extracted Answers

For each pack, show extracted answers:

```
┌─────────────────────────────────────────────────────────────┐
│  ANSWER PACK: security                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Extracted from research document:                          │
│                                                             │
│  authentication:                                            │
│    method: "JWT with Bearer token"                          │
│    source: "line 234: 'using JWT access tokens...'"        │
│                                                             │
│  authorization:                                             │
│    strategy: "Role-Based Access Control"                    │
│    source: "line 256: 'RBAC for permission management'"    │
│                                                             │
│  [More answers...]                                          │
│                                                             │
│  MISSING (need manual input):                               │
│  - secrets_management: [Not found in document]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 6.3: Fill Missing Answers

For any answers not found in the research, ask the user:

```
I couldn't find information about [topic] in the research document.

Options:
1. [Option A]
2. [Option B]
3. [Option C]
4. Skip for now (mark as TODO)
```

### Step 6.4: Write Answer Pack Files

For each spec, write the answer pack files:

```yaml
# .ldf/answerpacks/[spec-name]/security.yaml
feature_name: "[spec-name]"
pack: "security"
answered_at: "[timestamp]"
source_document: "[path/to/research.md]"

answers:
  authentication:
    method: "[extracted value]"
    # Source: line [N]
  authorization:
    strategy: "[extracted value]"
    # Source: line [N]
  # ...
```

### Step 6.5: Write Checkpoint

Write to `docs/_init/04-answerpacks-complete.md`:

```markdown
# Checkpoint 4: Answer Packs Complete

> **Generated**: [timestamp]

## Answer Packs Created

| Spec | Pack | Status | Missing Items |
|------|------|--------|---------------|
| [spec] | security | Complete | 0 |
| [spec] | testing | Complete | 1 (TODO) |
| ...

## Extraction Summary

- Total answers extracted: [N]
- Manually provided: [N]
- Marked as TODO: [N]

---
## Resume Instructions
Answer packs are complete. Continue with Phase 7 (Spec Scaffolding).
```

### ✋ CONFIRM Phase 6
```
Answer packs generated. Review and confirm? [Y/Edit/Continue]
```

---

## PHASE 7: SPEC SCAFFOLDING

### Step 7.1: Create Spec Directories

For each spec in the feature manifest:

```bash
mkdir -p .ldf/specs/[spec-name]
```

### Step 7.2: Generate requirements.md

For each spec, generate a requirements document from relevant research sections:

```markdown
# [Spec Name] - Requirements

## Overview
[Extract from research document's relevant section summary]

## Question-Pack Answers
**Domains covered**: [security, testing, api-design, data-model, ...]
**Answerpack location**: `.ldf/answerpacks/[spec-name]/*.yaml`

### Key Decisions
[Summarize key answers from answer packs]

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | | | | | TODO |
| 2. Security Basics | | | | | TODO |
| 3. Error Handling | | | | | TODO |
| 4. Logging & Observability | | | | | TODO |
| 5. API Design | | | | | TODO |
| 6. Data Validation | | | | | TODO |
| 7. Database Migrations | | | | | TODO |
| 8. Documentation | | | | | TODO |

## User Stories

[Generate EARS-format user stories from research requirements]

### US-1: [Story Title]
**As a** [role]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] AC-1.1: [criterion]
- [ ] AC-1.2: [criterion]

## Dependencies
[Extract from research document]

## Out of Scope
[Infer from research document boundaries]
```

### Step 7.3: Generate design.md

For each spec, generate a design document:

```markdown
# [Spec Name] - Design

## Architecture Overview
[Extract diagrams or descriptions from research]

## Technology Choices
[From answer packs and research decisions]

## Data Model
[Extract schema information if present]

## API Design
[Extract endpoint information if present]

## Guardrail Mapping

| Guardrail | Implementation Approach |
|-----------|------------------------|
| 1. Testing | [Strategy from testing answerpack] |
| 2. Security | [Strategy from security answerpack] |
| ... | ... |
```

### Step 7.4: Generate tasks.md

For each spec, generate a tasks document:

```markdown
# [Spec Name] - Tasks

**Status**: Ready for Planning
**Total Phases**: [N based on research timeline]

## Per-Task Guardrail Checklist

Before implementing each task, verify:
- [ ] 1. Testing Coverage: Unit tests, coverage ≥80%
- [ ] 2. Security Basics: Input validation, auth
- [ ] 3. Error Handling: Consistent responses
- [ ] 4. Logging: Structured logs
- [ ] 5. API Design: Versioned, documented
- [ ] 6. Data Validation: Schema validation
- [ ] 7. Migrations: Reversible
- [ ] 8. Documentation: Updated

## Phase 1: [Phase Name from research]
[Tasks extracted from research implementation plan]

- [ ] **Task 1.1**: [Title]
  - [ ] Subtask
  - [ ] Subtask
  - **Dependencies**: [None/List]
  - **Tests**: [Required tests]

## Phase 2: [Phase Name]
...
```

### Step 7.5: Write Checkpoint

Write to `docs/_init/05-specs-complete.md`:

```markdown
# Checkpoint 5: Specs Complete

> **Generated**: [timestamp]

## Specs Created

| Spec | Requirements | Design | Tasks | Status |
|------|--------------|--------|-------|--------|
| [name] | ✓ | ✓ | ✓ | Ready |
| ...

## Spec Structure

```
.ldf/specs/
├── [spec-1]/
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
├── [spec-2]/
...
```

---
## Resume Instructions
Specs are scaffolded. Continue with Phase 8 (Verification).
```

### ✋ CONFIRM Phase 7
```
Specs scaffolded. Review the generated files? [Y/Skip to verification]
```

---

## PHASE 8: VERIFICATION & FINALIZATION

### Step 8.1: Cross-Reference Validation

Verify complete mapping:

```
┌─────────────────────────────────────────────────────────────┐
│  MAPPING COVERAGE REPORT                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Research Sections → Specs                                  │
│  ──────────────────────────                                │
│  ✓ [Section 1] → [spec-name]                               │
│  ✓ [Section 2] → [spec-name]                               │
│  ⚠ [Section 3] → [NOT MAPPED]                              │
│                                                             │
│  Features → Specs                                           │
│  ───────────────                                           │
│  ✓ [Feature 1] → [spec-name]                               │
│  ✓ [Feature 2] → [spec-name]                               │
│                                                             │
│  Technology Decisions → Answer Packs                        │
│  ───────────────────────────────────                       │
│  ✓ [Decision 1] → [answerpack/field]                       │
│  ✓ [Decision 2] → [answerpack/field]                       │
│  ⚠ [Decision 3] → [TODO - needs manual input]              │
│                                                             │
│  Coverage: [N]% mapped                                      │
│  Warnings: [N]                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 8.2: Generate Audit Report

Write to `docs/_init/06-audit-report.md`:

```markdown
# LDF Initialization Audit Report

> **Generated**: [timestamp]
> **Source Document**: [path/to/research.md]
> **Project**: [project-name]

## Summary

| Metric | Value |
|--------|-------|
| Research Document Lines | [N] |
| Specs Created | [N] |
| Answer Packs Generated | [N] |
| Answers Extracted | [N] |
| Answers Manual | [N] |
| Answers TODO | [N] |
| Mapping Coverage | [N]% |

## Configuration Applied

- **Preset**: [preset]
- **Question Packs**: [list]
- **Coverage Thresholds**: [default]% / [critical]%

## Specs Created

[Table of specs with status]

## Unmapped Content

[List any research sections not captured in specs]

## TODO Items

[List any answers marked as TODO]

## Checkpoint Files

| File | Purpose |
|------|---------|
| 01-document-summary.md | Compressed research summary |
| 02-feature-manifest.md | Spec structure planning |
| 03-init-complete.md | LDF initialization record |
| 04-answerpacks-complete.md | Answer pack status |
| 05-specs-complete.md | Spec creation record |
| 06-audit-report.md | This file |

## Next Steps

1. Review generated specs in `.ldf/specs/`
2. Fill any TODO items in answer packs
3. Complete guardrail coverage matrices
4. Run `ldf lint` to validate structure
5. Begin implementation with Phase 1 tasks

---

## Initialization Complete

This project was initialized from research documentation using the
LDF init-from-research workflow. All checkpoint files will be archived
to `docs/_init-audit/` for future reference.
```

### Step 8.3: Archive Checkpoints

```bash
mkdir -p docs/_init-audit
mv docs/_init/* docs/_init-audit/
rmdir docs/_init
```

### Step 8.4: Final Validation

Run LDF validation:

```bash
ldf lint --all
ldf status
```

### ✋ CONFIRM Phase 8
```
┌─────────────────────────────────────────────────────────────┐
│  ✅ INITIALIZATION COMPLETE                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Project: [project-name]                                    │
│  Specs: [N] created                                         │
│  Answer Packs: [N] populated                                │
│  Mapping Coverage: [N]%                                     │
│                                                             │
│  Audit report: docs/_init-audit/06-audit-report.md          │
│                                                             │
│  Ready to start implementation!                             │
│                                                             │
│  Suggested next command:                                    │
│  $ ldf status                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Review the audit report? [Y/N]
```

---

## Context Recovery

If you lose context during initialization, you can resume from checkpoints:

```
To resume from Phase [N]:

1. Read all checkpoint files in order:
   - docs/_init/01-document-summary.md (or docs/_init-audit/ if archived)
   - docs/_init/02-feature-manifest.md
   - ...up to the last completed phase

2. Tell the AI assistant:
   "I'm resuming LDF initialization from Phase [N].
    Here are my checkpoint files: [paste contents]
    Please continue from Phase [N]."

3. The assistant will pick up where you left off.
```

---

## Quick Reference

| Phase | Purpose | Checkpoint File |
|-------|---------|-----------------|
| 1 | Document Intake | (interactive) |
| 2 | Document Analysis | 01-document-summary.md |
| 3 | Feature Extraction | 02-feature-manifest.md |
| 4 | Configuration Planning | (in Phase 5 checkpoint) |
| 5 | Project Initialization | 03-init-complete.md |
| 6 | Answer Pack Population | 04-answerpacks-complete.md |
| 7 | Spec Scaffolding | 05-specs-complete.md |
| 8 | Verification | 06-audit-report.md |
