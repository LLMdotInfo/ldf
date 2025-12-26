# Project File Structure Reference

Complete guide to LDF project organization and file purposes.

---

## Table of Contents

- [Project Root](#project-root)
- [.ldf Directory](#ldf-directory)
- [Spec Structure](#spec-structure)
- [Configuration Files](#configuration-files)
- [Question-Packs & Answerpacks](#question-packs--answerpacks)
- [Agent Integration](#agent-integration)
- [File Naming Conventions](#file-naming-conventions)

---

## Project Root

Basic LDF project structure:

```
my-project/
├── .ldf/                  # LDF configuration and specs
├── .agent/                # AI assistant integration (optional)
├── AGENT.md               # AI assistant instructions
├── src/                   # Your application code
├── tests/                 # Your test files
├── .gitignore             # Should include .ldf/answerpacks/ if sensitive
└── README.md              # Your project documentation
```

### Key Files at Root

#### `AGENT.md`
**Purpose:** Instructions for AI coding assistants (Claude Code, Cursor, etc.)

**Created by:** `ldf init`

**Contains:**
- Project overview
- LDF methodology explanation
- Active guardrails list
- Slash commands available
- Architecture standards
- Testing requirements

**When to edit:**
- Customize AI behavior for your project
- Add project-specific guidelines
- Update tech stack information

**Example content:**
```markdown
# Project: my-saas-app

## Overview
Multi-tenant SaaS application with RLS...

## LDF Methodology
This project uses LDF (LLM Development Framework)...

## Active Guardrails
1. Testing Coverage (80% minimum)
2. Security Basics (OWASP Top 10)
...

## Tech Stack
- Python 3.11 + FastAPI
- PostgreSQL 15 with RLS
- Redis for caching
```

---

## .ldf Directory

Core LDF configuration and data:

```
.ldf/
├── config.yaml            # Project configuration
├── guardrails.yaml        # Active guardrails
├── specs/                 # Feature specifications
│   ├── user-auth/
│   ├── checkout-flow/
│   └── admin-dashboard/
├── answerpacks/           # Question-pack answers
│   ├── user-auth/
│   ├── checkout-flow/
│   └── admin-dashboard/
├── templates/             # Spec templates
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
├── macros/                # Enforcement macros
│   ├── clarify-first.md
│   └── spec-guidelines.md
└── question-packs/        # Domain question templates
    ├── core/
    │   ├── security.yaml
    │   ├── testing.yaml
    │   ├── api-design.yaml
    │   └── data-model.yaml
    └── optional/
        ├── billing.yaml
        ├── multi-tenancy.yaml
        ├── provisioning.yaml
        └── webhooks.yaml
```

---

## Spec Structure

Each spec lives in its own directory under `.ldf/specs/`:

```
.ldf/specs/user-auth/
├── requirements.md        # Phase 1: What to build
├── design.md              # Phase 2: How to build
└── tasks.md               # Phase 3: Implementation steps
```

### requirements.md

**Phase:** 1 (Requirements)

**Purpose:** Define WHAT to build

**Contains:**
- Overview (1-2 paragraphs)
- User stories (As a... I want... So that...)
- Acceptance criteria (testable, measurable)
- Question-pack answer summaries
- Guardrail coverage matrix
- Outstanding questions
- References

**Created by:** `ldf create-spec <name>`

**When to edit:** During requirements gathering, before design

**Example structure:**
```markdown
# user-auth - Requirements

## Overview
Email/password authentication system with JWT tokens...

## User Stories

### US-1: User Registration
**As a** new user...

## Question-Pack Answers

### Security
- Auth method: JWT with 15-min expiry...

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| ...

## Outstanding Questions
None

## References
- JWT RFC 7519
```

**Validation:** `ldf lint user-auth`

---

### design.md

**Phase:** 2 (Design)

**Purpose:** Define HOW to build

**Contains:**
- Architecture overview (ASCII diagrams)
- Component definitions (classes, modules, services)
- Data models (database schemas, relationships)
- API contracts (endpoints, request/response formats)
- Guardrail implementation mapping

**Created by:** Manual (after requirements approved)

**When to edit:** After requirements approved, before tasks

**Example structure:**
```markdown
# user-auth - Design

## Architecture Overview
```
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│   Client    │────▶│  AuthService │────▶│   DB     │
└─────────────┘     └──────────────┘     └──────────┘
```

## Components

### AuthService
- `register(email, password) → JWT`
- `login(email, password) → JWT`
- `verify_token(token) → User`

## Data Models

### users table
...

## API Contracts

### POST /auth/register
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
...
```

**Validation:** `ldf lint user-auth`

---

### tasks.md

**Phase:** 3 (Tasks)

**Purpose:** Break into implementation steps

**Contains:**
- Numbered task list (by phase)
- Task dependencies
- Guardrail checklist per task
- Testing requirements per task

**Created by:** Manual (after design approved)

**When to edit:** After design approved, update during implementation

**Example structure:**
```markdown
# user-auth - Tasks

## Phase 1: Setup

- [ ] **Task 1.1:** Create database migration
  - [ ] Add users table
  - [ ] Add indexes on email
  - **Guardrails:** 7 (Database Migrations)
  - **Dependencies:** None

- [ ] **Task 1.2:** Set up models
  - [ ] Create User model
  - [ ] Add password hashing
  - **Guardrails:** 2 (Security), 6 (Data Validation)
  - **Dependencies:** Task 1.1

## Phase 2: Core Logic

- [ ] **Task 2.1:** Implement AuthService
  - [ ] register() method
  - [ ] login() method
  - **Guardrails:** 2 (Security), 3 (Error Handling)
  - **Dependencies:** Task 1.2
...
```

**Validation:** `ldf lint user-auth`

**Progress tracking:** Check off items as completed

---

## Configuration Files

### .ldf/config.yaml

**Purpose:** Project-level LDF configuration

**Created by:** `ldf init`

**Contains:**
- Project name and version
- Preset selection
- Enabled question-packs
- MCP server configuration
- Default settings

**Example:**
```yaml
project:
  name: my-saas-app
  version: 1.0.0

ldf:
  version: 1.0.0
  preset: saas

question_packs:
  core:
    - security
    - testing
    - api-design
    - data-model
  optional:
    - billing
    - multi-tenancy

mcp_servers:
  enabled: true
  servers:
    - spec_inspector
    - coverage_reporter

defaults:
  coverage_target: 80
  strict_mode: false
```

**When to edit:**
- Change project metadata
- Add/remove question-packs
- Enable/disable MCP servers
- Adjust default settings

---

### .ldf/guardrails.yaml

**Purpose:** Active guardrails for this project

**Created by:** `ldf init`

**Contains:**
- 8 core guardrails (always)
- Preset-specific guardrails (if applicable)
- Custom guardrails (if added)

**Example:**
```yaml
core:
  - id: 1
    name: Testing Coverage
    description: Minimum 80% coverage, 90% for critical paths
    severity: error

  - id: 2
    name: Security Basics
    description: OWASP Top 10 prevention
    severity: error

  # ... 6 more core guardrails

preset:  # Only if preset selected
  saas:
    - id: 9
      name: Multi-Tenancy (RLS)
      description: Row-Level Security with tenant_id
      severity: error

    - id: 10
      name: Tenant Isolation
      description: Cannot access other tenant's data
      severity: error

    # ... 3 more SaaS guardrails

custom:  # If you added custom guardrails
  - id: 101
    name: Performance Budget
    description: p95 < 200ms for all endpoints
    severity: warning
```

**When to edit:**
- Add custom guardrails (via `ldf customization`)
- Adjust severity levels
- Add enforcement rules

---

## Question-Packs & Answerpacks

### Question-Packs (.ldf/question-packs/)

**Purpose:** Template questions for decision-making

**Structure:**
```
.ldf/question-packs/
├── core/
│   ├── security.yaml         # Always included
│   ├── testing.yaml          # Always included
│   ├── api-design.yaml       # Always included
│   └── data-model.yaml       # Always included
└── optional/
    ├── billing.yaml          # Payment processing
    ├── multi-tenancy.yaml    # SaaS apps
    ├── provisioning.yaml     # Async jobs
    └── webhooks.yaml         # Event delivery
```

**Example (security.yaml):**
```yaml
name: Security
category: core
questions:
  - id: auth_method
    question: What authentication method will be used?
    type: choice
    options:
      - JWT
      - Session cookies
      - OAuth 2.0
      - API keys
    required: true

  - id: password_storage
    question: How will passwords be stored?
    type: text
    required: true
    hint: "e.g., bcrypt cost 12, argon2id"
```

**When to edit:**
- Add custom questions
- Create domain-specific packs
- Adjust for team needs

---

### Answerpacks (.ldf/answerpacks/)

**Purpose:** Store answers to question-packs for each spec

**Structure:**
```
.ldf/answerpacks/
└── user-auth/
    ├── security.yaml
    ├── testing.yaml
    ├── api-design.yaml
    └── data-model.yaml
```

**Example (user-auth/security.yaml):**
```yaml
spec: user-auth
pack: security
answers:
  auth_method: JWT
  password_storage: bcrypt cost 12
  session_duration: 15 minutes
  refresh_token_duration: 7 days
  rate_limiting: 5 login attempts per 15 minutes per IP

rationale:
  auth_method: |
    JWT chosen for stateless authentication, enabling horizontal scaling.
    Refresh tokens in database for revocation capability.

  password_storage: |
    bcrypt cost 12 provides good security/performance balance.
    Cost can be increased later as hardware improves.
```

**When to edit:**
- Answer questions during requirements phase
- Update as decisions change
- Add rationale for complex decisions

**Note:** May contain sensitive information - consider adding to .gitignore

---

## Agent Integration

### .agent Directory

**Purpose:** AI assistant integration files

**Structure:**
```
.agent/
├── commands/              # Slash commands for AI
│   ├── create-spec.md
│   ├── implement-task.md
│   └── review-spec.md
└── mcp.json               # MCP server configuration (optional)
```

### .agent/mcp.json

**Purpose:** Configure MCP servers for Claude Code and other AI tools

**Created by:** `ldf mcp-config > .agent/mcp.json`

**Example:**
```json
{
  "mcpServers": {
    "spec_inspector": {
      "command": "ldf",
      "args": ["mcp", "serve", "spec_inspector"]
    },
    "coverage_reporter": {
      "command": "ldf",
      "args": ["mcp", "serve", "coverage_reporter"]
    }
  }
}
```

**When to edit:**
- Enable/disable specific MCP servers
- Configure server-specific options

---

## File Naming Conventions

### Spec Names

**Format:** `lowercase-with-hyphens`

**Examples:**
- ✅ `user-auth`
- ✅ `checkout-flow`
- ✅ `admin-dashboard`
- ❌ `UserAuth` (no PascalCase)
- ❌ `user_auth` (no underscores)
- ❌ `user auth` (no spaces)

**Why:** Consistent, URL-friendly, works across all platforms

---

### User Story IDs

**Format:** `US-<number>`

**Examples:**
- `US-1`, `US-2`, `US-3`
- `US-10`, `US-11`, `US-12`

**Reference:** `[US-1]`, `[US-1..3]`, `[US-1, US-2, US-5]`

---

### Acceptance Criteria IDs

**Format:** `AC-<story>.<number>`

**Examples:**
- `AC-1.1`, `AC-1.2` (for US-1)
- `AC-2.1`, `AC-2.2` (for US-2)

**Reference:** `[AC-1.1]`, `[AC-1.1-1.3]`, `[AC-1.1, AC-1.3]`

---

### Task IDs

**Format:** `Task <phase>.<number>`

**Examples:**
- `Task 1.1`, `Task 1.2` (Phase 1)
- `Task 2.1`, `Task 2.2` (Phase 2)

**Reference:** `[T-1.1]`, `[T-1.1, T-2.3]`

**In tasks.md:**
```markdown
- [ ] **Task 1.1:** Create database migration
- [ ] **Task 1.2:** Set up models
- [ ] **Task 2.1:** Implement service layer
```

---

### Design Section IDs

**Format:** `Section <number>.<number>` or `S<number>.<number>`

**Examples:**
- `Section 1.1`, `S1.1` (Architecture subsection)
- `Section 2.1`, `S2.1` (Components subsection)

**Reference:** `[S1.1]`, `[S2.1, S2.3]`

---

## .gitignore Recommendations

```gitignore
# LDF sensitive data (optional)
.ldf/answerpacks/          # May contain sensitive decisions
.ldf/custom/               # Custom guardrails might be proprietary

# LDF generated files (optional)
.ldf/specs/*/coverage.json # Coverage data regenerated by tests

# Always ignore
.agent/mcp.json            # May contain local paths
```

**Note:** Most LDF files should be version controlled. Only ignore if:
- Contains sensitive business logic
- Contains credentials or secrets
- Is regenerated from other sources

---

## Directory Size Guidelines

**Typical project:**
```
.ldf/                      # 500 KB - 5 MB total
├── config.yaml            # 1-2 KB
├── guardrails.yaml        # 2-5 KB
├── specs/                 # 100 KB - 2 MB (grows with features)
│   └── user-auth/
│       ├── requirements.md  # 5-15 KB
│       ├── design.md        # 10-30 KB
│       └── tasks.md         # 5-20 KB
├── answerpacks/           # 50 KB - 500 KB
├── templates/             # 20 KB - 50 KB
├── macros/                # 10 KB - 30 KB
└── question-packs/        # 50 KB - 200 KB
```

**Large project (100+ specs):**
- `.ldf/` directory: 10-50 MB
- Consider archiving completed specs
- Use git LFS for large binary assets if any

---

## Related Documentation

- **[Command Reference](commands.md)** - Commands that work with these files
- **[First Spec Tutorial](../tutorials/01-first-spec.md)** - Creating your first spec
- **[Customization Guide](../customization.md)** - Customizing structure
- **[Troubleshooting](troubleshooting.md)** - File-related issues

---

**Questions about file structure?** See [FAQ](troubleshooting.md#faq) or [ask in discussions](https://github.com/LLMdotInfo/ldf/discussions).
