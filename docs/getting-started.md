# Getting Started with LDF

LDF (LLM Development Framework) is a spec-driven development methodology that ensures quality through structured requirements, guardrails, and multi-agent validation.

## Prerequisites

- Python 3.10+ (for CLI and MCP servers)
- Node.js 18+ (optional, for TypeScript projects)
- VS Code (optional, for extension)

## Installation

### 1. Install LDF CLI

```bash
pip install ldf
```

Verify installation:
```bash
ldf --version
```

### 2. Initialize a Project

The easiest way to get started is with the interactive setup:

```bash
ldf init
```

The CLI guides you through:

1. **Project path** - Where to create your project (default: `./my-project`)
2. **Preset selection** - Choose guardrails for your domain:
   - `saas` - Multi-tenant apps with RLS, tenant isolation, billing
   - `fintech` - Financial apps with ledger accuracy, compliance
   - `healthcare` - HIPAA-compliant with PHI handling
   - `api-only` - Developer APIs with rate limits, versioning
   - `custom` - Core guardrails only
3. **Question packs** - Core packs always included, domain packs pre-selected based on preset
4. **MCP servers** - AI integration (spec-inspector, coverage-reporter)
5. **Pre-commit hooks** - Optional validation on commits

```
$ ldf init

Enter project path: ./my-saas-app

Select guardrail preset:
❯ saas - Multi-tenant SaaS applications (+5 guardrails)
  fintech - Financial applications (+7 guardrails)
  healthcare - HIPAA-compliant (+6 guardrails)
  api-only - Pure API services (+4 guardrails)
  custom - Core guardrails only

Core packs (always included):
  ✓ security - Authentication, authorization, secrets
  ✓ testing - Coverage requirements, testing strategies
  ✓ api-design - REST patterns, versioning, errors
  ✓ data-model - Database schema, migrations

Select domain packs: [space to toggle, enter to confirm]
  [x] billing - Payment processing, subscriptions
  [x] multi-tenancy - RLS, tenant isolation
  [ ] provisioning - Async jobs, queues
  [ ] webhooks - Event delivery, signatures

✓ Created .ldf/ directory structure
✓ Created CLAUDE.md
```

This creates:
```
my-saas-app/
├── .ldf/
│   ├── config.yaml          # Project configuration
│   ├── guardrails.yaml      # Active guardrails
│   ├── specs/               # Feature specifications
│   ├── answerpacks/         # Question-pack answers
│   ├── templates/           # Spec templates
│   └── macros/              # Enforcement macros
├── .claude/commands/        # Slash commands
└── CLAUDE.md                # AI assistant instructions
```

### Non-Interactive Setup

For CI/CD or scripting:

```bash
# Create project at specific path with preset
ldf init --path ./my-project --preset saas -y

# Use defaults for everything
ldf init -y

# Also install pre-commit hooks
ldf init --preset saas --hooks -y
```

## Your First Spec

### 1. Create a Spec

```bash
ldf create-spec user-authentication
```

This creates:
```
.ldf/specs/user-authentication/
├── requirements.md      # User stories and acceptance criteria
├── design.md           # (created later) Architecture and components
└── tasks.md            # (created later) Implementation checklist
```

### 2. Write Requirements

Open `.ldf/specs/user-authentication/requirements.md` and define:

```markdown
# user-authentication - Requirements

## Overview

User authentication for the application using email/password with optional MFA.

## User Stories

### US-1: Email/Password Login

**As a** registered user
**I want to** log in with my email and password
**So that** I can access my account

**Acceptance Criteria:**
- [ ] AC-1.1: User can enter email and password
- [ ] AC-1.2: Valid credentials grant access
- [ ] AC-1.3: Invalid credentials show error (no email enumeration)
- [ ] AC-1.4: Account locks after 5 failed attempts

## Question-Pack Answers

### Security
- Authentication: Email/password with bcrypt (cost 12)
- Session: JWT in HttpOnly cookie, 15min access / 7day refresh
- MFA: Optional TOTP via authenticator app

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1] | [TBD] | [TBD] | Alice | TODO |
| 2. Security Basics | [US-1] | [TBD] | [TBD] | Alice | TODO |
...
```

### 3. Validate with Lint

```bash
ldf lint user-authentication
```

The linter checks:
- Question-pack answers exist
- Guardrail coverage matrix is complete
- No missing sections

### 4. Get External Review (Optional)

```bash
ldf audit --type spec-review --spec user-authentication
```

This generates an audit request you can send to ChatGPT or Gemini for review.

### 5. Create Design

Once requirements are approved, create design.md:

```markdown
# user-authentication - Design

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Client    │────▶│  Auth API    │────▶│  Database  │
└─────────────┘     └──────────────┘     └────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   JWT Store  │
                    └──────────────┘
```

## Components

### AuthService

**Purpose:** Handle authentication logic

**Interface:**
\`\`\`python
class AuthService:
    async def login(self, email: str, password: str) -> AuthResult
    async def logout(self, session_id: str) -> bool
    async def verify_mfa(self, user_id: str, code: str) -> bool
\`\`\`

## Data Model

### users Table

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| mfa_secret | VARCHAR(255) | NULL |
| failed_attempts | INT | DEFAULT 0 |
| locked_until | TIMESTAMP | NULL |

## Guardrail Mapping

| Guardrail | Implementation | Section |
|-----------|---------------|---------|
| 2. Security | bcrypt, JWT HttpOnly | AuthService |
...
```

### 6. Create Tasks

Finally, create tasks.md. LDF supports two task formats - use either consistently:

**Checklist Format (Official Template):**
```markdown
# user-authentication - Tasks

## Phase 1: Setup

- [ ] **Task 1.1:** Create AuthService class
  - [ ] Create class structure
  - [ ] Add type hints
  - [ ] Write docstrings

- [ ] **Task 1.2:** Add users table migration
  - [ ] Create migration file
  - [ ] Define schema
  - [ ] Test up/down

## Phase 2: Core Implementation

- [ ] **Task 2.1:** Implement login endpoint
  - [ ] Validate input
  - [ ] Hash password comparison
  - [ ] Generate JWT

- [ ] **Task 2.2:** Add password validation
  - [ ] Minimum length check
  - [ ] Complexity requirements
```

**Heading Format (Alternative):**
```markdown
# user-authentication - Tasks

## Phase 1: Setup

### Task 1.1: Create AuthService class
- [ ] Create class structure
- [ ] Add type hints
- [ ] Write docstrings

### Task 1.2: Add users table migration
- [ ] Create migration file
- [ ] Define schema
```

**Key Requirements:**
- Heading format: "Task" keyword OPTIONAL, colon REQUIRED
- Checklist format: "Task" keyword REQUIRED, colon REQUIRED
- Task IDs: Use `1.1` (two-level) or `1.1.1` (subtask)

See [Task Format Guide](task-format.md) for all supported formats and details.

### 7. Implement

Now you can implement! Use `ldf lint` to validate as you go.

## IDE Integration

### VS Code Extension

Install the LDF VS Code extension for:
- Spec tree view with status indicators
- Guardrail coverage visualization
- Task progress tracking
- Snippets for common patterns

### MCP Servers for AI Assistants

Generate and configure MCP servers using the LDF CLI:

```bash
# Generate MCP configuration for your project
mkdir -p .claude && ldf mcp-config > .claude/mcp.json
```

This creates `.claude/mcp.json` with the correct paths to LDF's MCP servers configured for your project. The servers provide:

- **spec-inspector**: Query spec status, guardrail coverage, task progress
- **coverage-reporter**: Test coverage metrics per service/guardrail

See [MCP Setup Guide](../mcp-servers/MCP_SETUP.md) for advanced configuration options.

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│  1. ldf create-spec [name]          # Create spec           │
│  2. Write requirements.md           # Define user stories   │
│  3. ldf lint [name]                 # Validate spec         │
│  4. ldf audit --type spec-review    # Get external review   │
│  5. Write design.md                 # Define architecture   │
│  6. Write tasks.md                  # Create task list      │
│  7. Implement tasks                 # Write code            │
│  8. ldf coverage                    # Check test coverage   │
│  9. Mark tasks complete             # Update tasks.md       │
└─────────────────────────────────────────────────────────────┘
```

## CI/CD Integration

Set up automated spec validation in your CI pipeline to catch issues before merge.

### GitHub Actions

```bash
mkdir -p .github/workflows
cp $(pip show ldf | grep Location | cut -d' ' -f2)/../integrations/ci-cd/github-actions.yaml .github/workflows/ldf.yaml
```

Or copy from the LDF repository:
```bash
# If you cloned LDF
cp /path/to/ldf/integrations/ci-cd/github-actions.yaml .github/workflows/ldf.yaml
```

This enables:
- **Spec linting** on every PR (`ldf lint --all`)
- **Answerpack completeness** checking (no template markers)
- **Guardrail matrix validation** (all guardrails covered)
- **Optional automated audits** with OpenAI

### GitLab CI

```bash
# Copy from LDF repository
cp /path/to/ldf/integrations/ci-cd/gitlab-ci.yaml .gitlab-ci.yml
```

See [CI/CD Integrations](../integrations/ci-cd/README.md) for full configuration options.

## Next Steps

- [Concepts](concepts.md) - Learn the philosophy behind LDF
- [Answerpacks Guide](answerpacks.md) - How to capture design decisions
- [Glossary](glossary.md) - Technical terms explained (RLS, PHI, HIPAA, etc.)
- [Customization](customization.md) - Configure guardrails and question-packs
- [Multi-Agent Workflow](multi-agent-workflow.md) - Use multiple AI agents
- [Examples](../examples/) - See complete example projects

## Troubleshooting

### "No specs found"
- Ensure `.ldf/specs/` directory exists
- Check `SPECS_DIR` configuration

### "Lint failed"
- Run `ldf lint --verbose` for details
- Check guardrail coverage matrix is complete

### "MCP server not starting"
- Verify Python 3.10+ is installed
- Check MCP SDK: `pip install mcp`
- Run server manually to see errors
