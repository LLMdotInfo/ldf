# Customization Guide

LDF is designed to be customizable. You can add your own guardrails, question-packs, and presets to match your team's requirements.

## Table of Contents

- [Guardrails](#guardrails)
- [Question-Packs](#question-packs)
- [Presets](#presets)
- [Configuration](#configuration)
- [Team Templates](#team-templates)
- [Generating Documentation](#generating-documentation)
- [Best Practices](#best-practices)

---

## Guardrails

Guardrails are constraints that are validated at every phase of development.

### Location

```
.ldf/
├── guardrails.yaml       # Your project's active guardrails
```

Or in the bundled framework (installed with the package):

```
ldf/_framework/guardrails/
├── core.yaml             # 8 universal guardrails
└── presets/
    ├── saas.yaml         # SaaS-specific guardrails
    ├── fintech.yaml      # Financial guardrails
    ├── healthcare.yaml   # HIPAA guardrails
    └── api-only.yaml     # API-focused guardrails
```

### Guardrail Structure

Custom guardrails are added under the `custom:` key in `.ldf/guardrails.yaml`:

```yaml
# .ldf/guardrails.yaml
preset: saas                        # Optional: extend a preset (saas, fintech, healthcare, api-only)

custom:
  - id: 9                           # Unique ID (start at 9 for custom)
    name: "Audit Logging"           # Display name
    description: "All mutations must be logged to audit table"
    severity: high                  # critical, high, medium, low
    enabled: true                   # Toggle on/off
    config:                         # Optional configuration
      include_reads: false
      retention_days: 90
```

### Severity Levels

| Severity | Lint Behavior | Description |
|----------|---------------|-------------|
| `critical` | Error (blocks) | Must be addressed before approval |
| `high` | Error (blocks) | Should be addressed before approval |
| `medium` | Warning | Should be addressed but won't block |
| `low` | Info | Nice to have |

### Adding Custom Guardrails

1. **Edit your project's guardrails:**

```yaml
# .ldf/guardrails.yaml
preset: saas                        # Optional: load a preset's guardrails

custom:
  # Add custom guardrails (core guardrails are always loaded)
  - id: 9
    name: "Rate Limiting"
    description: "All public endpoints must have rate limiting"
    severity: high
    enabled: true

  - id: 10
    name: "Correlation IDs"
    description: "All requests must include X-Correlation-ID header"
    severity: medium
    enabled: true
```

2. **Update spec templates to include your guardrails:**

The guardrail coverage matrix in requirements.md should include all active guardrails.

### Disabling Core Guardrails

Use the `disabled:` list or `overrides:` section:

```yaml
# .ldf/guardrails.yaml

# Option 1: Disable by ID or name
disabled:
  - 8                               # Documentation guardrail (by ID)
  - "Documentation"                 # Or by name

# Option 2: Override with enabled: false
overrides:
  "8":                              # Guardrail ID as string key
    enabled: false
```

---

## Question-Packs

Question-packs are domain-specific questions that must be answered before writing requirements.

### Location

```
ldf/_framework/question-packs/
└── core/                   # Core packs (always available)
    ├── security.yaml
    ├── testing.yaml
    ├── api-design.yaml
    └── data-model.yaml
```

You can also create custom question-packs in your project:

```
.ldf/question-packs/
├── billing.yaml           # Custom pack
└── compliance.yaml        # Custom pack
```

### Question-Pack Structure

```yaml
# ldf/_framework/question-packs/core/security.yaml
domain: security
version: "1.0"
critical: true                      # Must be answered before proceeding

questions:
  authentication:
    - question: "What authentication method will be used?"
      critical: true
      options:
        - "Session-based (cookies)"
        - "JWT tokens"
        - "OAuth 2.0"
        - "API keys"
      follow_ups:
        - "Where are tokens/sessions stored?"
        - "What is the token expiration policy?"

    - question: "Is MFA required?"
      critical: true
      options:
        - "Required for all users"
        - "Optional (user choice)"
        - "Required for admin/privileged users only"
        - "Not applicable"

  authorization:
    - question: "How is authorization enforced?"
      critical: true
      examples:
        - "Role-based (RBAC)"
        - "Attribute-based (ABAC)"
        - "Row-level security (RLS)"
```

### Creating Custom Question-Packs

1. **Create a YAML file:**

```yaml
# .ldf/question-packs/compliance.yaml
domain: compliance
version: "1.0"
critical: true

questions:
  data_retention:
    - question: "What is the data retention policy?"
      critical: true
      options:
        - "7 days"
        - "30 days"
        - "1 year"
        - "Indefinite"
      follow_ups:
        - "How is data purged after retention period?"
        - "Are there legal hold requirements?"

  audit_requirements:
    - question: "What audit logging is required?"
      critical: true
      examples:
        - "All CRUD operations"
        - "Authentication events only"
        - "Financial transactions"
```

2. **Reference in your config:**

```yaml
# .ldf/config.yaml
question_packs:
  - security
  - testing
  - api-design
  - compliance           # Your custom pack
```

### Answerpacks

Answerpacks are the filled-out responses to question-packs, stored per-spec:

```
.ldf/answerpacks/
└── user-auth/
    ├── security.yaml    # Filled security answers
    ├── testing.yaml     # Filled testing answers
    └── compliance.yaml  # Filled compliance answers
```

---

## Presets

Presets are bundles of guardrails and question-packs for specific domains.

### Choosing the Right Preset

```
What type of application are you building?
│
├─ Multi-tenant SaaS (customers each have isolated data)
│   └─ → ✅ saas preset
│       Adds: Multi-tenancy isolation, RLS, tenant billing, audit logging
│
├─ Financial application (payments, accounting, trading)
│   └─ → ✅ fintech preset
│       Adds: Ledger integrity, money precision, idempotency, reconciliation
│
├─ Healthcare application (patient data, medical records)
│   └─ → ✅ healthcare preset
│       Adds: HIPAA compliance, PHI handling, consent management, encryption
│
├─ Developer API (public or internal API service)
│   └─ → ✅ api-only preset
│       Adds: Rate limiting, API versioning, deprecation handling
│
└─ Something else / unsure
    └─ → ✅ custom preset (core guardrails only)
        Use: Core 8 guardrails, add custom ones as needed
```

**Multiple domains?** Start with the most critical (e.g., healthcare for medical fintech), then add custom guardrails.

### Available Presets

| Preset | Guardrails Added |
|--------|------------------|
| `saas` | Multi-tenancy isolation, billing integration, audit logging |
| `fintech` | Ledger integrity, money precision, compliance, idempotency |
| `healthcare` | HIPAA compliance, PHI handling, consent management, encryption |
| `api-only` | Rate limiting, API versioning, deprecation handling |

### Creating Custom Presets

```yaml
# ldf/_framework/guardrails/presets/my-preset.yaml
name: my-preset
description: "Custom preset for my organization"
extends: core                       # Start with core guardrails

guardrails:
  - id: 9
    name: "Custom Rule 1"
    description: "..."
    severity: high
    enabled: true

question_packs:
  - security
  - testing
```

Use it:

```bash
ldf init --preset my-preset
```

---

## Configuration

### Project Configuration

```yaml
# .ldf/config.yaml
version: "1.0"

project:
  name: "my-project"
  type: "api"                       # api, web, mobile, library

# Note: Guardrails are configured in .ldf/guardrails.yaml, not here

question_packs:
  - security
  - testing
  - api-design
  - billing

coverage:
  default_threshold: 80             # Default coverage threshold
  critical_threshold: 90            # Coverage for critical paths
  critical_services:
    - auth
    - billing
    - ledger

lint:
  strict: false                     # Treat warnings as errors
  ignore_patterns:
    - "*.draft.md"                  # Ignore draft files
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LDF_SPECS_DIR` | Location of specs directory | `.ldf/specs` |
| `LDF_CONFIG_FILE` | Path to config file | `.ldf/config.yaml` |
| `LDF_GUARDRAILS_FILE` | Path to guardrails file | `.ldf/guardrails.yaml` |

### AI Assistant Integration

Your `AGENT.md` should reference LDF:

```markdown
# Project Instructions

This project uses LDF (spec-driven development).

## Commands

- `/project:create-spec {name}` - Create new spec
- `/project:implement-task {spec} {task}` - Implement a task
- `/project:review-spec {spec}` - Review spec for approval

## Rules

1. NO code without approved spec (requirements → design → tasks)
2. Every task must pass guardrail checklist
3. Tests required before task completion
```

---

## Team Templates

Team templates allow organizations to package and share pre-configured LDF setups across projects.

### What's in a Template

A template can include:
- `.ldf/config.yaml` - Project configuration
- `.ldf/guardrails.yaml` - Custom guardrails
- `.ldf/question-packs/` - Custom question packs
- `.ldf/templates/` - Spec templates
- `.ldf/macros/` - Enforcement macros
- `template.yaml` - Template metadata

**What's NOT included (by design):**
- `.ldf/specs/` - Each project creates its own specs
- `.ldf/answerpacks/` - May contain PII or secrets
- Any executable files (.sh, .py outside macros)

### Creating a Template

1. **Set up a reference project:**

```bash
ldf init --preset saas
# Customize guardrails, add question-packs, etc.
```

2. **Create template metadata:**

```yaml
# template.yaml (in project root)
name: acme-saas-template
version: "1.0.0"
ldf_version: "1.0.0"
description: "ACME Corp standard SaaS project template"
components:
  - guardrails
  - question-packs
  - templates
```

3. **Verify before publishing:**

```bash
ldf template verify ./my-template/
# Or verify a zip file
ldf template verify ./my-template.zip
```

**Verification checks:**
- `template.yaml` exists with required fields
- No specs or answerpacks included
- All YAML files parse correctly
- No potential secrets detected

4. **Package and distribute:**

```bash
# Create a zip (exclude specs/answerpacks)
zip -r acme-template.zip . -x ".ldf/specs/*" -x ".ldf/answerpacks/*" -x ".git/*"

# Share via:
# - Internal package registry
# - Shared network drive
# - Git repository
```

### Using a Template

```bash
# Initialize new project from template
ldf init --from /path/to/acme-template.zip

# Or from a directory
ldf init --from /path/to/acme-template/

# Force overwrite existing .ldf
ldf init --from template.zip --force
```

After import, the project's `.ldf/config.yaml` tracks the template source:

```yaml
template:
  name: acme-saas-template
  version: "1.0.0"
  source: /path/to/acme-template.zip
  applied_at: "2024-01-15T10:30:00"
```

---

## Generating Documentation

Use `ldf export-docs` to generate documentation for your project's LDF configuration:

```bash
# Generate markdown documentation
ldf export-docs

# Output to specific file
ldf export-docs -o docs/ldf-framework.md

# Include only specific sections
ldf export-docs --include guardrails --include packs
```

This generates documentation showing:
- Active guardrails with descriptions
- Configured question packs and their questions
- Preset information
- Custom configuration

Useful for:
- Onboarding new team members
- Compliance documentation
- Project audits

---

## Best Practices

### Guardrails

1. **Start with core** - The 8 core guardrails cover most projects
2. **Add incrementally** - Only add guardrails you'll actually enforce
3. **Use severity wisely** - Reserve `critical` for truly blocking issues
4. **Document justifications** - When marking guardrails N/A, explain why

### Question-Packs

1. **Required = blocking** - Only mark questions as required if they're truly essential
2. **Provide examples** - Help AI assistants give better answers
3. **Group logically** - Organize questions by topic
4. **Update as you learn** - Add questions based on past issues

### Presets

1. **One preset per project** - Don't combine multiple presets
2. **Extend, don't replace** - Use `extends: core` to keep base guardrails
3. **Share across team** - Put custom presets in a shared location
