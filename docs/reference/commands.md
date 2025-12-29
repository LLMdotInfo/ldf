# CLI Command Reference

Quick reference for all LDF commands.

---

## Table of Contents

- [Quick Command Overview](#quick-command-overview)
- [Project Initialization](#project-initialization)
- [Spec Management](#spec-management)
- [Validation & Linting](#validation--linting)
- [Coverage & Quality](#coverage--quality)
- [Multi-Agent Workflow](#multi-agent-workflow)
- [MCP Integration](#mcp-integration)
- [Hooks & Git Integration](#hooks--git-integration)
- [Templates & Presets](#templates--presets)
- [Diagnostics & Maintenance](#diagnostics--maintenance)
- [Workspace Management](#workspace-management)
- [Common Workflows](#common-workflows)

---

## Quick Command Overview

| Command | Purpose | Frequency |
|---------|---------|-----------|
| `ldf init` | Initialize LDF in project | Once per project |
| `ldf create-spec <name>` | Create new spec | Per feature |
| `ldf lint <name>` | Validate single spec | After editing |
| `ldf lint --all` | Validate all specs | Before commits |
| `ldf status` | Show project overview | Anytime |
| `ldf doctor` | Check installation | When troubleshooting |

---

## Project Initialization

### `ldf init`

Initialize LDF in a project directory.

**Usage:**
```bash
ldf init                           # Interactive mode (recommended)
ldf init -y                        # Non-interactive (use defaults)
ldf init --preset saas             # With domain preset
ldf init --path ./my-project       # Specify path
ldf init --from template.zip       # From team template
ldf init --repair                  # Repair incomplete setup
```

**Options:**
- `--preset <name>` - Choose guardrail preset: `saas`, `fintech`, `healthcare`, `api-only`, `custom`
- `--question-packs <packs>` - Comma-separated list of packs to include
- `--mcp-servers` - Enable MCP servers for AI integration
- `--path <dir>` - Project directory (default: current directory)
- `--from <file>` - Initialize from team template ZIP
- `-y, --yes` - Skip prompts, use defaults
- `--force` - Overwrite existing LDF setup
- `--repair` - Fix incomplete initialization

**Examples:**
```bash
# Interactive setup (beginner-friendly)
ldf init

# Quick setup with SaaS preset
ldf init --preset saas -y

# Setup with specific question-packs
ldf init --question-packs security,testing,billing

# Setup from team template
ldf init --from /path/to/team-template.zip

# Repair broken setup
ldf init --repair
```

**What it creates:**
```
.ldf/
├── config.yaml
├── guardrails.yaml
├── specs/
├── answerpacks/
├── templates/
├── question-packs/
└── macros/
.agent/commands/
AGENT.md
```

---

## Spec Management

### `ldf create-spec`

Create a new feature specification.

**Usage:**
```bash
ldf create-spec <name>                  # Create spec
ldf create-spec user-auth               # Example
ldf create-spec checkout-flow           # Multi-word (use hyphens)
```

**Creates:**
```
.ldf/specs/<name>/
└── requirements.md
```

**Next steps:**
1. Edit `requirements.md`
2. Run `ldf lint <name>`
3. Create `design.md`
4. Create `tasks.md`

---

### `ldf list-specs`

List all specs in the project.

**Usage:**
```bash
ldf list-specs                          # List all specs
```

**Output:**
```
Specs in this project:
  • user-auth (requirements)
  • checkout-flow (design)
  • admin-dashboard (complete)
```

---

## Validation & Linting

### `ldf lint`

Validate specifications against guardrails.

**Usage:**
```bash
ldf lint <spec-name>                    # Validate one spec
ldf lint user-auth                      # Example
ldf lint --all                          # Validate all specs
ldf lint --all --format ci              # CI-friendly output
ldf lint --all --format sarif           # SARIF format for IDEs
ldf lint user-auth --fix                # Auto-fix common issues
```

**Options:**
- `<spec-name>` - Name of spec to validate
- `--all` - Validate all specs in project
- `--format <fmt>` - Output format: `rich` (default), `ci`, `sarif`, `json`, `text`
- `--fix` - Automatically fix common issues
- `--strict` - Fail on warnings (not just errors)

**Output formats:**

**rich** (default terminal):
```
Linting spec: user-auth
✓ requirements.md: valid
✓ design.md: valid
✓ tasks.md: valid
Status: ✅ COMPLETE
```

**ci** (for CI/CD):
```
[INFO] Linting spec: user-auth
[OK] requirements.md
[OK] design.md
[OK] tasks.md
EXIT_CODE: 0
```

**sarif** (for IDEs):
```json
{
  "version": "2.1.0",
  "runs": [...]
}
```

**Exit codes:**
- `0` - Success, no errors
- `1` - Validation errors found
- `2` - Invalid command usage

---

## Coverage & Quality

### `ldf coverage`

Show test coverage metrics.

**Usage:**
```bash
ldf coverage                            # Show current coverage
ldf coverage --spec user-auth           # Coverage for one spec
ldf coverage --compare baseline.json    # Compare with baseline
ldf coverage --upload s3://bucket/path  # Upload to S3
ldf coverage --fail-under 80            # Fail if below threshold
```

**Options:**
- `--spec <name>` - Show coverage for specific spec
- `--compare <file>` - Compare with previous coverage snapshot
- `--upload <url>` - Upload coverage report (requires `ldf[s3]`)
- `--fail-under <pct>` - Exit 1 if coverage below percentage
- `--format <fmt>` - Output format: `rich`, `json`, `text`

**Example output:**
```
Test Coverage Report
====================

Overall: 87.5% (target: 80%)

By Spec:
  user-auth:       92% ✓
  checkout-flow:   81% ✓
  admin-dashboard: 78% ✗ (below 80%)

By Guardrail:
  1. Testing Coverage:     87.5%
  2. Security Basics:      90.0%
  3. Error Handling:       85.0%
```

---

### `ldf preflight`

Run all pre-launch checks.

**Usage:**
```bash
ldf preflight                           # Run all checks
ldf preflight --strict                  # Strict mode (fail on warnings)
ldf preflight --skip-tests              # Skip test execution
```

**Checks:**
- All specs validated (`ldf lint --all`)
- Test coverage meets targets
- No outstanding TODO items in critical paths
- All guardrails addressed
- Documentation complete

**Exit codes:**
- `0` - All checks pass
- `1` - One or more checks failed

---

## Multi-Agent Workflow

### `ldf audit`

Generate or import audit requests for AI review.

**Usage:**
```bash
# Generate audit request
ldf audit --type spec-review            # Spec review
ldf audit --type code-audit             # Code review
ldf audit --type security               # Security audit
ldf audit --type gap-analysis           # Gap analysis
ldf audit --agent chatgpt               # For ChatGPT
ldf audit --agent gemini                # For Gemini

# Import feedback
ldf audit --import feedback.md          # Import feedback file
ldf audit --import feedback.md --dry-run # Preview changes

# API-based (requires ldf[automation])
ldf audit --api --type security         # Automated API audit
```

**Audit types:**
- `spec-review` - Review requirements/design/tasks
- `code-audit` - Review implemented code
- `security` - Security-focused review
- `pre-launch` - Comprehensive pre-launch check
- `gap-analysis` - Find missing requirements
- `edge-cases` - Identify edge cases
- `architecture` - Architecture review
- `full` - All of the above

**Options:**
- `--type <type>` - Audit type (see above)
- `--agent <name>` - Target agent: `chatgpt`, `gemini`
- `--import <file>` - Import feedback from file
- `--dry-run` - Preview import without changes
- `--api` - Use API-based audit (requires API keys)
- `--redact` - Redact secrets from audit request

**Example workflow:**
```bash
# 1. Generate request
ldf audit --type spec-review --agent chatgpt > audit-request.md

# 2. Copy to ChatGPT, save response to feedback.md

# 3. Import feedback
ldf audit --import feedback.md

# 4. Review changes, iterate
```

---

## MCP Integration

### `ldf mcp-config`

Generate MCP server configuration.

**Usage:**
```bash
ldf mcp-config                          # Print config to stdout
ldf mcp-config > .agent/mcp.json        # Save to file
ldf mcp-config --servers spec,coverage  # Specific servers only
```

**Options:**
- `--servers <list>` - Comma-separated list: `spec_inspector`, `coverage_reporter`
- `--output <file>` - Write to file instead of stdout

**Generated config:**
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

---

### `ldf mcp-health`

Check MCP server health.

**Usage:**
```bash
ldf mcp-health                          # Check all servers
ldf mcp-health --server spec_inspector  # Check specific server
```

**Output:**
```
MCP Server Health Check
=======================

spec_inspector:     ✓ Healthy
coverage_reporter:  ✓ Healthy

All MCP servers operational.
```

---

## Hooks & Git Integration

### `ldf hooks`

Manage Git pre-commit hooks.

**Usage:**
```bash
ldf hooks install                       # Install hooks
ldf hooks uninstall                     # Remove hooks
ldf hooks status                        # Check hook status
```

**What hooks do:**
- Run `ldf lint --all` before commit
- Prevent commits with invalid specs
- Validate guardrail coverage

---

## Templates & Presets

### `ldf list-presets`

List available guardrail presets.

**Usage:**
```bash
ldf list-presets
```

**Output:**
```
Available presets:
  • saas       - Multi-tenant SaaS applications (+5 guardrails)
  • fintech    - Financial applications (+7 guardrails)
  • healthcare - HIPAA-compliant applications (+6 guardrails)
  • api-only   - Pure API services (+4 guardrails)
  • custom     - Core guardrails only (8 guardrails)
```

---

### `ldf list-packs`

List available question-packs.

**Usage:**
```bash
ldf list-packs
ldf list-packs --core                   # Core packs only
ldf list-packs --optional               # Optional packs only
```

**Output:**
```
Core question-packs:
  • security     - Auth, secrets, vulnerabilities
  • testing      - Coverage, test types, strategies
  • api-design   - REST, versioning, errors
  • data-model   - Schema, migrations, indexes

Optional question-packs:
  • billing         - Payments, subscriptions, invoicing
  • multi-tenancy   - RLS, tenant isolation
  • provisioning    - Async jobs, queues, external services
  • webhooks        - Event delivery, signatures, retry logic
```

---

### `ldf add-pack`

Add question-pack to existing project.

**Usage:**
```bash
ldf add-pack billing                    # Add single pack
ldf add-pack billing,webhooks           # Add multiple packs
```

---

### `ldf template`

Manage spec templates.

**Usage:**
```bash
ldf template list                       # List templates
ldf template export --output my-template.zip  # Export current setup
```

---

## Diagnostics & Maintenance

### `ldf doctor`

Diagnose project health and installation issues.

**Usage:**
```bash
ldf doctor
```

**Checks:**
- LDF installation and version
- Python version compatibility
- Required dependencies
- Project configuration validity
- Spec structure correctness
- MCP server availability (if installed)

**Output:**
```
LDF Installation Health Check
=============================

✓ LDF version: 1.0.0
✓ Python version: 3.11.5
✓ pip version: 23.0.1

Project Health:
✓ .ldf/ directory exists
✓ config.yaml valid
✓ guardrails.yaml valid
✓ 3 specs found

Optional Components:
✓ MCP servers installed
✗ Automation features not installed
✗ S3 support not installed

Recommendations:
  • Consider installing automation: pip install llm-ldf[automation]
```

---

### `ldf status`

Show project status overview.

**Usage:**
```bash
ldf status
ldf status --verbose                    # Detailed view
ldf status --format json                # JSON output
```

**Output:**
```
LDF Project Status
==================

Project: my-saas-app
Preset: saas (13 guardrails)
Specs: 3 total

Specs Overview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spec Name       Phase    Status     Guardrails  Tasks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
user-auth       complete valid      13/13       12/12 ✓
checkout-flow   design   valid      13/13       0/8
admin-dashboard req      valid      10/13       0/0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendations:
  • checkout-flow: Create tasks.md
  • admin-dashboard: 3 guardrails marked N/A, verify reasons
```

---

### `ldf update`

Update framework files (templates, macros, question-packs).

**Usage:**
```bash
ldf update                              # Update all framework files
ldf update --templates                  # Update templates only
ldf update --dry-run                    # Preview changes
```

**Options:**
- `--templates` - Update spec templates only
- `--macros` - Update enforcement macros only
- `--question-packs` - Update question-packs only
- `--dry-run` - Show what would change without updating

**Note:** Preserves customizations in `.ldf/custom/`

---

### `ldf --version`

Show LDF version.

**Usage:**
```bash
ldf --version
ldf -v
```

**Output:**
```
ldf version 1.0.0
```

---

### `ldf --help`

Show help for any command.

**Usage:**
```bash
ldf --help                              # General help
ldf init --help                         # Command-specific help
ldf lint --help
```

---

## Workspace Management

Commands for managing multi-project workspaces with shared resources.

### `ldf workspace init`

Initialize a new workspace for managing multiple LDF projects.

**Usage:**
```bash
ldf workspace init                      # Basic initialization
ldf workspace init --name my-platform   # With custom name
ldf workspace init --discover           # Auto-find existing LDF projects
ldf workspace init --force              # Overwrite existing workspace
```

**Options:**
- `--name <name>` - Workspace name (default: directory name)
- `--discover` - Auto-discover existing LDF projects in subdirectories
- `--force` - Overwrite existing workspace manifest
- `--create-shared` - Create `.ldf-shared/` directory (default: true)

**What it creates:**
```
ldf-workspace.yaml           # Workspace manifest
.ldf-shared/                 # Shared resources
├── guardrails/              # Shared guardrail definitions
├── templates/               # Shared spec templates
├── question-packs/          # Shared question-packs
└── macros/                  # Shared macro definitions
.ldf-workspace/              # Internal state cache
```

---

### `ldf workspace list`

List all projects in the workspace.

**Usage:**
```bash
ldf workspace list                      # Rich table output
ldf workspace list --format json        # JSON for scripting
ldf workspace list --format text        # Plain text
```

**Output:**
```
Workspace: my-platform
Root: /path/to/workspace

┌────────┬────────────────┬─────────┬─────────┐
│ Alias  │ Path           │ State   │ Version │
├────────┼────────────────┼─────────┼─────────┤
│ auth   │ services/auth  │ current │ 1.0.0   │
│ billing│ services/billing│ current │ 1.0.0   │
└────────┴────────────────┴─────────┴─────────┘
```

---

### `ldf workspace add`

Add a project to the workspace.

**Usage:**
```bash
ldf workspace add ./services/auth            # Add with auto-generated alias
ldf workspace add ./billing -a billing       # Add with custom alias
```

**Options:**
- `--alias, -a` - Custom alias for the project (default: directory name)

---

### `ldf workspace sync`

Synchronize workspace state and validate references.

**Usage:**
```bash
ldf workspace sync                           # Full sync
ldf workspace sync --no-validate-refs        # Skip reference validation
```

**Options:**
- `--rebuild-registry` - Rebuild project registry cache (default: true)
- `--validate-refs` - Validate cross-project references (default: true)

---

### `ldf workspace report`

Generate aggregated workspace report.

**Usage:**
```bash
ldf workspace report                         # Rich terminal output
ldf workspace report --format json           # JSON for automation
ldf workspace report --format html -o report.html  # HTML dashboard
```

---

### `ldf workspace graph`

Generate project dependency graph from cross-project references.

**Usage:**
```bash
ldf workspace graph                          # Mermaid diagram
ldf workspace graph --format dot             # Graphviz DOT format
ldf workspace graph --format json            # JSON for tooling
ldf workspace graph -o deps.md               # Write to file
```

---

### `ldf workspace validate-refs`

Validate all cross-project spec references.

**Usage:**
```bash
ldf workspace validate-refs                  # Rich output
ldf workspace validate-refs --format json    # JSON for scripting
```

---

### Environment Variable: `LDF_PROJECT`

Set the active project when running commands from a workspace.

```bash
export LDF_PROJECT=auth
ldf lint --all  # Runs lint in the 'auth' project
```

---

## Common Workflows

### Workflow 1: New Feature from Scratch

```bash
# 1. Create spec
ldf create-spec payment-processing

# 2. Edit requirements.md
code .ldf/specs/payment-processing/requirements.md

# 3. Validate
ldf lint payment-processing

# 4. Optional: Get AI review
ldf audit --type spec-review

# 5. Create design.md
code .ldf/specs/payment-processing/design.md

# 6. Create tasks.md
code .ldf/specs/payment-processing/tasks.md

# 7. Final validation
ldf lint payment-processing

# 8. Check overall status
ldf status
```

---

### Workflow 2: Pre-Commit Check

```bash
# Validate all specs before committing
ldf lint --all --format ci

# Check coverage
ldf coverage --fail-under 80

# Run full preflight
ldf preflight

# If all pass, commit
git add . && git commit -m "Add payment processing spec"
```

---

### Workflow 3: CI/CD Pipeline

```bash
#!/bin/bash
# In your CI/CD pipeline

# Install LDF
pip install llm-ldf

# Validate all specs
ldf lint --all --format ci || exit 1

# Check coverage
ldf coverage --fail-under 80 || exit 1

# Optional: Run automated security audit
ldf audit --api --type security || exit 1
```

---

### Workflow 4: Adding LDF to Existing Project

```bash
# 1. Analyze codebase
ldf convert analyze > analysis.md

# 2. Send to AI (Claude, ChatGPT, etc.)
# Paste analysis.md, ask to generate specs

# 3. Import generated specs
ldf convert import response.md --dry-run  # Preview
ldf convert import response.md           # Apply

# 4. Review and refine
ldf lint --all
ldf status
```

---

## Environment Variables

### `LDF_CONFIG_PATH`
Override config file location.
```bash
export LDF_CONFIG_PATH=/custom/path/config.yaml
```

### `LDF_LOG_LEVEL`
Set logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
```bash
export LDF_LOG_LEVEL=DEBUG
```

### `LDF_NO_COLOR`
Disable colored output.
```bash
export LDF_NO_COLOR=1
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Validation errors or command failed |
| `2` | Invalid command usage |
| `130` | Interrupted by user (Ctrl+C) |

---

## Related Documentation

- **[Installation Guides](../installation/)** - Platform-specific setup
- **[First Spec Tutorial](../tutorials/01-first-spec.md)** - Hands-on walkthrough
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues
- **[Workflow Diagrams](../visual-guides/workflows.md)** - Visual workflows

---

**Quick help:** Run `ldf <command> --help` for detailed information on any command.
