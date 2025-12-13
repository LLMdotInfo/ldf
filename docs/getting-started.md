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

```bash
cd your-project
ldf init
```

This creates:
```
.ldf/
├── config.yaml          # Project configuration
├── specs/               # Feature specifications
└── answerpacks/         # Question-pack answers
```

### Interactive Setup

The `ldf init` command asks:
1. **Preset**: Choose guardrail preset (core, saas, fintech, healthcare, api-only)
2. **Question-packs**: Select domain-specific question packs
3. **MCP servers**: Configure AI assistant integration

For non-interactive setup:
```bash
ldf init --preset saas -y
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

Configure MCP servers in `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "spec-inspector": {
      "command": "python",
      "args": ["path/to/ldf/mcp-servers/spec-inspector/server.py"],
      "env": {
        "LDF_ROOT": ".",
        "SPECS_DIR": ".ldf/specs"
      }
    },
    "coverage-reporter": {
      "command": "python",
      "args": ["path/to/ldf/mcp-servers/coverage-reporter/server.py"],
      "env": {
        "PROJECT_ROOT": "."
      }
    }
  }
}
```

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
cp path/to/ldf/integrations/ci-cd/github-actions.yaml .github/workflows/ldf.yaml
```

This enables:
- **Spec linting** on every PR (`ldf lint --all`)
- **Answerpack completeness** checking (no template markers)
- **Guardrail matrix validation** (all guardrails covered)
- **Optional automated audits** with OpenAI

### GitLab CI

```bash
cp path/to/ldf/integrations/ci-cd/gitlab-ci.yaml .gitlab-ci.yml
```

See [CI/CD Integrations](../integrations/ci-cd/README.md) for full configuration options.

## Next Steps

- [Concepts](concepts.md) - Learn the philosophy behind LDF
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
