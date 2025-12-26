# 5-Minute Quickstart

Get LDF running and create your first spec in under 5 minutes.

> **Prerequisites**: Python 3.10+, basic terminal familiarity
> **New to programming?** Use the [complete beginner guide](installation/) instead.

---

## Step 1: Install LDF (30 seconds)

```bash
pip install llm-ldf
```

**Verify:**
```bash
ldf --version
# Expected: ldf version 1.0.0
```

---

## Step 2: Initialize a Project (15 seconds)

```bash
# Create and enter project directory
mkdir my-ldf-project && cd my-ldf-project

# Initialize with defaults
ldf init -y
```

**What happened:**
- Created `.ldf/` directory with configuration
- Set up 8 core guardrails
- Created spec templates and question-packs

---

## Step 3: Create a Spec (10 seconds)

```bash
ldf create-spec user-auth
```

**What happened:**
- Created `.ldf/specs/user-auth/`
- Generated `requirements.md` template

---

## Step 4: Edit Requirements (2 minutes)

Open `.ldf/specs/user-auth/requirements.md` and add:

```markdown
# user-auth - Requirements

## Overview
Email/password authentication with JWT tokens.

## User Stories

### US-1: User Registration

**As a** new user
**I want to** register with email and password
**So that** I can create an account

**Acceptance Criteria:**
- [ ] AC-1.1: Email validation (RFC 5322 format)
- [ ] AC-1.2: Password minimum 12 characters
- [ ] AC-1.3: Password hashed with bcrypt (cost 12)
- [ ] AC-1.4: Returns 201 with JWT token on success

### US-2: User Login

**As a** registered user
**I want to** log in with email and password
**So that** I can access my account

**Acceptance Criteria:**
- [ ] AC-2.1: Returns 200 with JWT token on success
- [ ] AC-2.2: Returns 401 on invalid credentials
- [ ] AC-2.3: Account lockout after 5 failed attempts

## Question-Pack Answers

### Security
- **Auth method:** JWT with 15-minute expiry, refresh tokens
- **Password storage:** bcrypt cost 12
- **Rate limiting:** 5 login attempts per 15 minutes per IP

### Testing
- **Coverage target:** 90% (authentication is critical)
- **Test types:** Unit, integration, security tests

### API Design
- **Endpoints:** POST /auth/register, POST /auth/login
- **Error format:** RFC 7807 Problem Details

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1, US-2: 90% target] | TBD | TBD | Dev | TODO |
| 2. Security Basics | [Security QP: bcrypt, JWT, rate limit] | TBD | TBD | Security | TODO |
| 3. Error Handling | [AC-2.2: 401, AC-1.4: validation errors] | TBD | TBD | Dev | TODO |
| 4. Logging & Observability | [Log all auth attempts with IP] | TBD | TBD | Ops | TODO |
| 5. API Design | [API Design QP: RFC 7807 errors] | TBD | TBD | Dev | TODO |
| 6. Data Validation | [AC-1.1: Email format, AC-1.2: Password] | TBD | TBD | Dev | TODO |
| 7. Database Migrations | [users table with indexes] | TBD | TBD | DB | TODO |
| 8. Documentation | [OpenAPI specs for both endpoints] | TBD | TBD | TechWriter | TODO |
```

**Save** and continue.

---

## Step 5: Validate (10 seconds)

```bash
ldf lint user-auth
```

**Expected output:**
```
✓ requirements.md: valid
Status: ✅ READY FOR DESIGN PHASE
```

---

## Step 6: Check Status (5 seconds)

```bash
ldf status
```

**Output:**
```
Specs: 1 total
user-auth   requirements   valid   8/8   0/0
```

---

## ✅ Done! What's Next?

You've created a valid LDF spec in ~5 minutes.

### Immediate Next Steps

**Option 1: Complete the Spec**
Create `design.md` and `tasks.md` to complete the three-phase workflow.

**Option 2: Try Multi-Agent Review**
```bash
ldf audit --type spec-review
```
Copy the output to ChatGPT or Gemini for AI feedback.

**Option 3: Use with AI Coding Assistant**
The generated `AGENT.md` file contains instructions for Claude Code, Cursor, or other AI assistants. They can help you:
- Complete design and tasks phases
- Generate implementation code
- Write tests

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `ldf init [--preset saas]` | Initialize project (optionally with preset) |
| `ldf create-spec <name>` | Create new spec |
| `ldf lint <name>` | Validate spec |
| `ldf lint --all` | Validate all specs |
| `ldf status` | Project overview |
| `ldf audit` | Generate review request |
| `ldf doctor` | Check installation |

---

## Presets for Specific Domains

Reinitialize with domain-specific guardrails:

**SaaS (Multi-tenant apps):**
```bash
ldf init --preset saas
# Adds: Row-Level Security, Tenant Isolation, Audit Logging, Subscription Checks
```

**Fintech (Financial apps):**
```bash
ldf init --preset fintech
# Adds: Double-Entry Ledger, Money Precision, Idempotency, Reconciliation
```

**Healthcare (HIPAA-compliant):**
```bash
ldf init --preset healthcare
# Adds: HIPAA Compliance, PHI Handling, Access Logging, Consent Management
```

**API-only (Developer APIs):**
```bash
ldf init --preset api-only
# Adds: Rate Limiting, API Versioning, OpenAPI Docs, Webhook Signatures
```

---

## Optional: Install Extras

### MCP Servers (90% token savings with AI assistants)
```bash
pip install llm-ldf[mcp]
ldf mcp-config > .agent/mcp.json
```

**Use with:** Claude Code, other MCP-compatible AI tools

### Automation (API-based audits)
```bash
pip install llm-ldf[automation]
```

**Use with:** ChatGPT API, Gemini API for automated spec review

### S3 Support (Coverage upload)
```bash
pip install llm-ldf[s3]
```

**Use with:** `ldf coverage --upload s3://bucket/path`

---

## IDE Integration

### VS Code
1. Install [LDF extension](https://github.com/LLMdotInfo/ldf-vscode) from marketplace
2. Features: Spec tree view, guardrail coverage, task progress
3. Open project: `code .`

### Other IDEs
- Use `.ldf/` folder structure
- Edit markdown files normally
- Run `ldf lint` from terminal

---

## Learn More

- **[Detailed Tutorial](tutorials/01-first-spec.md)** - Full walkthrough for beginners
- **[Concepts Guide](concepts.md)** - Philosophy and methodology
- **[Examples](../examples/)** - Real-world specs (Python, TypeScript, Go)
- **[Customization](customization.md)** - Custom guardrails and question-packs

---

## Troubleshooting

### "ldf: command not found"
**macOS/Linux:**
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

**Windows:**
Add Python Scripts folder to PATH (see [Windows Installation](installation/windows.md#troubleshooting))

### "pip install llm-ldf" fails
```bash
# Use --user flag
pip install --user ldf

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install llm-ldf
```

### Lint errors
- Ensure all 8 guardrails in coverage matrix
- Mark N/A guardrails with reason: `N/A - No database used`
- No [TBD] or [TODO] placeholders in answerpack references

---

## Quick Reference: Project Structure

```
my-ldf-project/
├── .ldf/
│   ├── config.yaml              # Project settings
│   ├── guardrails.yaml          # Active guardrails
│   ├── specs/
│   │   └── user-auth/
│   │       ├── requirements.md  # Phase 1
│   │       ├── design.md        # Phase 2 (create next)
│   │       └── tasks.md         # Phase 3 (create last)
│   ├── answerpacks/             # Question-pack answers
│   ├── templates/               # Spec templates
│   └── question-packs/          # Domain questions
├── .agent/
│   └── commands/                # Slash commands for AI
└── AGENT.md                     # AI assistant instructions
```

---

**That's it!** You're ready to use LDF. For deeper learning, continue to the [tutorial series](tutorials/01-first-spec.md).
