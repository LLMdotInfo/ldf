# Answerpacks Guide

Answerpacks capture your design decisions before implementation. They ensure critical questions are answered upfront, preventing costly changes later.

## What Are Answerpacks?

Answerpacks are YAML files containing your answers to question-pack questions. Each feature spec has its own answerpack directory with one file per question pack used.

**Location:** `.ldf/answerpacks/{feature-name}/`

**Purpose:**
- Document design decisions before coding
- Ensure critical questions aren't overlooked
- Provide context for AI assistants
- Enable validation through linting

## Directory Structure

When you create a spec with `ldf create-spec user-auth`, the following structure is created:

```
.ldf/
├── specs/
│   └── user-auth/
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
└── answerpacks/
    └── user-auth/          # Answers for this feature
        ├── security.yaml   # Security decisions
        ├── testing.yaml    # Testing strategy
        ├── api-design.yaml # API patterns
        └── data-model.yaml # Database decisions
```

## YAML Format

Each answerpack file follows this structure:

```yaml
# .ldf/answerpacks/user-auth/security.yaml
pack: security
feature: user-auth
answered_at: "2024-01-15T10:30:00Z"

answers:
  authentication:
    method: "JWT"
    rationale: "Stateless, works with microservices architecture"
    provider: "Custom implementation with jose library"
    token_expiry: "15 minutes for access, 7 days for refresh"

  authorization:
    strategy: "RBAC"
    roles:
      - admin
      - user
      - guest
    rationale: "Simple role hierarchy sufficient for current requirements"

  secrets_management:
    storage: "AWS Secrets Manager"
    rotation: "90 days for API keys, on-demand for user passwords"
    rationale: "Native AWS integration, automatic rotation support"

  mfa:
    required: false
    method: null
    rationale: "Not required for MVP, will add in v2"
```

## Field Descriptions

### Required Fields

| Field | Description |
|-------|-------------|
| `pack` | Name of the question pack this answers |
| `feature` | Name of the feature/spec |
| `answers` | Dictionary of category → question answers |

### Answer Structure

Each answer should include:

| Field | Description |
|-------|-------------|
| Main value | The actual answer (string, list, boolean, etc.) |
| `rationale` | Why this decision was made |
| Supporting fields | Additional context as needed |

## Complete Example

Here's a complete answerpack for a user authentication feature:

```yaml
# .ldf/answerpacks/user-auth/security.yaml
pack: security
feature: user-auth
answered_at: "2024-01-15T10:30:00Z"

answers:
  authentication:
    method: "JWT"
    provider: "Custom"
    token_expiry:
      access: "15 minutes"
      refresh: "7 days"
    storage: "HttpOnly cookies for web, secure storage for mobile"
    rationale: |
      JWT chosen for stateless auth compatible with microservices.
      Short access token expiry limits damage from token theft.
      Refresh tokens enable persistent sessions without long-lived access.

  authorization:
    strategy: "RBAC"
    roles:
      - name: "admin"
        description: "Full system access"
        permissions: ["*"]
      - name: "user"
        description: "Standard user access"
        permissions: ["read:own", "write:own"]
      - name: "guest"
        description: "Read-only public content"
        permissions: ["read:public"]
    enforcement: "Middleware + database RLS"
    rationale: |
      RBAC provides clear permission boundaries.
      Combined with database RLS for defense in depth.

  password_requirements:
    min_length: 12
    require_uppercase: true
    require_lowercase: true
    require_number: true
    require_special: false
    rationale: "NIST guidelines recommend length over complexity"

  rate_limiting:
    login_attempts: "5 per 15 minutes per IP"
    password_reset: "3 per hour per email"
    api_general: "100 requests per minute per user"
    rationale: "Balance security with usability"

  input_validation:
    email: "RFC 5322 validation + domain verification"
    password: "Unicode allowed, normalize with NFKC"
    username: "Alphanumeric + underscore, 3-30 chars"
    rationale: "Strict validation prevents injection attacks"
```

```yaml
# .ldf/answerpacks/user-auth/testing.yaml
pack: testing
feature: user-auth
answered_at: "2024-01-15T10:45:00Z"

answers:
  coverage_targets:
    overall: 85
    critical_paths: 95
    rationale: "Auth is security-critical, needs higher coverage"

  frameworks:
    unit: "pytest"
    integration: "pytest + httpx"
    e2e: "playwright"
    rationale: "Standard Python testing stack"

  test_data:
    strategy: "Factory pattern with Faker"
    fixtures: "pytest fixtures with transaction rollback"
    rationale: "Isolated tests, realistic data"

  critical_test_cases:
    - "Valid login returns tokens"
    - "Invalid password returns 401"
    - "Expired token returns 401"
    - "Rate limiting blocks after threshold"
    - "Password reset flow complete"
    - "Session invalidation on password change"
```

## How Answerpacks Integrate with Specs

### In Requirements

The `requirements.md` should reference answerpacks:

```markdown
## Question-Pack Answers

See `.ldf/answerpacks/user-auth/` for detailed design decisions.

### Security Summary
- **Authentication:** JWT with 15-minute access tokens
- **Authorization:** RBAC with admin/user/guest roles
- **Rate Limiting:** 5 login attempts per 15 minutes

### Testing Summary
- **Coverage Target:** 85% overall, 95% critical paths
- **Frameworks:** pytest, httpx, playwright
```

### In Design

The `design.md` should map decisions to implementation:

```markdown
## Authentication Flow

Based on security answerpack decisions:

1. Login endpoint receives credentials
2. Validate against user store (see data-model answerpack)
3. Generate JWT access token (15 min expiry)
4. Generate refresh token (7 day expiry)
5. Store refresh token hash in database
6. Return tokens via HttpOnly cookies
```

## Linter Validation

The `ldf lint` command validates answerpacks:

### Checks Performed

1. **Directory exists** - Warns if `.ldf/answerpacks/{spec}/` missing
2. **Files present** - Warns if directory empty
3. **No placeholders** - Errors if `[TODO`, `[PLACEHOLDER`, or `YOUR_` found
4. **Critical questions** - Errors if critical question pack has no file

### Fixing Linter Errors

```bash
# Run linter to see issues
ldf lint user-auth

# Example output:
# WARNING: Answerpack missing: .ldf/answerpacks/user-auth/billing.yaml
# ERROR: Template marker found in security.yaml: [TODO: decide on MFA]
```

To fix:
1. Create missing answerpack files
2. Replace `[TODO]` markers with actual decisions
3. Add rationale for each decision

## Best Practices

### Do

- Answer questions **before** writing requirements
- Include rationale for every decision
- Be specific (e.g., "15 minutes" not "short")
- Update answerpacks when decisions change
- Reference answerpacks in spec documents

### Don't

- Leave placeholder text in files
- Skip questions - mark as N/A with rationale if not applicable
- Copy answers between features without review
- Forget to update when requirements change

## Creating Answerpacks

### Interactive (Recommended)

Use the `/project:create-spec` command which guides you through questions:

```
/project:create-spec user-auth

# Claude will:
# 1. Load question packs from .ldf/question-packs/
# 2. Ask each question interactively
# 3. Create answerpack files with your responses
# 4. Generate requirements.md with answers summary
```

### Manual

Create files manually following the YAML format above:

```bash
# Create directory
mkdir -p .ldf/answerpacks/user-auth

# Create answerpack file
cat > .ldf/answerpacks/user-auth/security.yaml << 'EOF'
pack: security
feature: user-auth
answered_at: "2024-01-15T10:30:00Z"

answers:
  authentication:
    method: "JWT"
    rationale: "Stateless auth for microservices"
EOF
```

## Troubleshooting

### "Answerpack directory not found"

Create the directory and add at least one answerpack file:

```bash
mkdir -p .ldf/answerpacks/{feature-name}
```

### "Template markers found"

Search for and replace placeholders:

```bash
grep -r "TODO\|PLACEHOLDER\|YOUR_" .ldf/answerpacks/
```

### "Critical question pack missing"

Create the missing answerpack file. Core packs (security, testing, api-design, data-model) should always have answers for features that touch those areas.
