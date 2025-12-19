# LDF - LLM Development Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **spec-driven development framework** for AI-assisted software engineering. LDF enforces a structured approach where requirements, design, and tasks are approved before any code is written.

> **Attribution**: LDF is a fork of the WDF (WTMI Development Framework/WTMI Internal Tool), created by Jay Dubinsky ([@JayFromEpic](https://github.com/JayFromEpic)). Made available to the community as part of the [llm.info](https://llm.info) resource library.

## Our Mission and Goal

**Our Mission** is to help developers build better software regardless of their experience level, and promote the continued sharing of knowledge for the betterment of all.

**Our Goal** is to make this mission a reality by providing a framework that any developer can leverage to build better code, in a structured and methodical way that won't give your product owner a heart attack :heart_hands:.

## Why LDF?

AI coding assistants are powerful but can produce inconsistent results. LDF solves this by:

- **Forcing structured thinking** - No code until requirements → design → tasks are approved
- **Enforcing guardrails** - 8 core constraints validated at every phase
- **Enabling multi-agent review** - Use ChatGPT/Gemini to audit your AI's specs
- **Reducing token usage** - MCP servers provide 90% token savings vs file reads

## Quick Start

### 1. Install

```bash
# Install the CLI
pip install ldf

# Or install from source
git clone https://github.com/LLMdotInfo/ldf.git
cd ldf
pip install -e .
```

### 2. Initialize Your Project

```bash
# Interactive setup (recommended for first-time users)
ldf init

# Or non-interactive with preset
ldf init --path ./my-project --preset saas -y
```

The interactive CLI guides you through:
- **Project path** - Where to create your project
- **Preset selection** - Choose domain-specific guardrails
- **Question packs** - Pre-selected based on preset, customize as needed
- **MCP servers** - AI integration tools

This creates:
```
my-project/
├── .ldf/
│   ├── config.yaml           # Project configuration
│   ├── guardrails.yaml       # Active guardrails (8 core + preset)
│   ├── question-packs/       # Domain question templates
│   ├── answerpacks/          # Design decision storage
│   └── specs/                # Your feature specifications
├── .claude/commands/         # Slash commands for AI
└── CLAUDE.md                 # AI assistant instructions
```

### 3. Create Your First Spec

In Claude Code (or any AI assistant with the CLAUDE.md instructions):

```
/project:create-spec user-authentication
```

LDF guides you through:
1. **Question-Packs** - Answer critical questions about security, testing, API design
2. **Requirements** - Generate user stories with acceptance criteria
3. **Design** - Define architecture, data models, APIs
4. **Tasks** - Break down into implementable steps with guardrail checklists

### 4. Validate & Implement

```bash
# Lint your specs
ldf lint

# Generate audit request for ChatGPT/Gemini review
ldf audit --type spec-review

# After approval, implement tasks
/project:implement-task user-auth 1.1
```

## Core Features

### Guardrails

8 core guardrails are enabled by default:

| # | Guardrail | Severity | Description |
|---|-----------|----------|-------------|
| 1 | Testing Coverage | Critical | ≥80% default, ≥90% critical paths |
| 2 | Security Basics | Critical | OWASP Top 10 prevention |
| 3 | Error Handling | High | Consistent responses, no swallowed exceptions |
| 4 | Logging & Observability | High | Structured logging, correlation IDs |
| 5 | API Design | High | Versioning, pagination, error format |
| 6 | Data Validation | Critical | Input validation at boundaries |
| 7 | Database Migrations | High | Reversible, separate from backfills |
| 8 | Documentation | Medium | API docs, README, inline comments |

**Presets** add domain-specific guardrails:

| Preset | Additional Guardrails |
|--------|----------------------|
| `saas` | Multi-tenancy, RLS, subscription billing, audit logs |
| `fintech` | Double-entry ledger, money precision, compliance, idempotency |
| `healthcare` | HIPAA compliance, PHI handling, consent management |
| `api-only` | Rate limiting, versioning, OpenAPI docs |

### Three-Phase Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Requirements                                       │
│  - Answer question-packs (security, testing, API design)    │
│  - Generate user stories with EARS criteria                 │
│  - Create guardrail coverage matrix                         │
│  → Approval required before proceeding                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Design                                             │
│  - Architecture diagrams                                    │
│  - Data models and schemas                                  │
│  - API endpoint definitions                                 │
│  - Guardrail implementation mapping                         │
│  → Approval required before proceeding                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Tasks                                              │
│  - Numbered implementation steps                            │
│  - Per-task guardrail checklists                            │
│  - Dependencies and test requirements                       │
│  → Ready for implementation                                 │
└─────────────────────────────────────────────────────────────┘
```

### MCP Servers

LDF includes MCP (Model Context Protocol) servers for real-time validation:

| Server | Purpose |
|--------|---------|
| **spec-inspector** | Query spec status, guardrail coverage, task progress |
| **coverage-reporter** | Test coverage metrics per service/guardrail |

**Token savings:** 90% reduction compared to file reads.

```bash
# Generate MCP configuration for your project
mkdir -p .claude && ldf mcp-config > .claude/mcp.json
```

### Multi-Agent Audit

Use ChatGPT and Gemini to review your AI's work:

```bash
# Generate audit request
ldf audit --type spec-review

# Copy the generated markdown to ChatGPT with the prompt
# from multi-agent/prompts/chatgpt/spec-review.md

# Import the feedback
ldf audit --import feedback.md
```

## CLI Reference

```bash
# Project initialization
ldf init                        # Initialize LDF in current project
  --preset saas|fintech|healthcare|api-only
  --question-packs security,testing,billing
  --force                       # Force reinitialize, overwrite existing
  --repair                      # Fix missing files without overwriting

# Project status
ldf status                      # Show project state and recommendations
ldf status --json               # JSON output for CI/scripts

# Add LDF to existing projects
ldf convert analyze             # Analyze codebase, generate AI prompt
ldf convert analyze -o file.md  # Save prompt to file
ldf convert import response.md  # Import AI-generated specs/answerpacks
ldf convert import response.md -n my-feature  # Custom spec name
ldf convert import response.md --dry-run      # Preview without creating

# Spec validation
ldf lint                        # Lint all specs
ldf lint <spec-name>            # Lint single spec
ldf lint --all --format ci      # CI-friendly output for GitHub Actions

# Multi-agent audit
ldf audit --type spec-review    # Generate spec review request
ldf audit --type code-audit     # Generate code audit request
ldf audit --import <file>       # Import audit feedback

# Coverage
ldf coverage                    # Show coverage summary
ldf coverage --service auth     # Coverage for specific service

# Framework updates
ldf update --check              # Check for framework updates
ldf update --dry-run            # Preview what would change
ldf update                      # Apply updates interactively
ldf update --only templates     # Update specific components
```

## CI/CD Integration

LDF includes GitHub Actions and GitLab CI templates for automated spec validation:

```bash
# GitHub Actions
mkdir -p .github/workflows
cp integrations/ci-cd/github-actions.yaml .github/workflows/ldf.yaml

# GitLab CI
cp integrations/ci-cd/gitlab-ci.yaml .gitlab-ci.yml
```

The CI pipeline validates:
- All specs pass `ldf lint --all`
- Answerpacks have no template markers
- Guardrail coverage matrices are complete
- (Optional) Automated audits with OpenAI

See [CI/CD Integration](integrations/ci-cd/README.md) for configuration options.

## Project Structure

```
ldf/
├── ldf/                        # CLI package (pip install ldf)
│   ├── _framework/             # Bundled framework assets
│   │   ├── templates/          # Spec templates (requirements, design, tasks)
│   │   ├── guardrails/         # Core + preset guardrails
│   │   ├── question-packs/     # Domain question templates
│   │   └── macros/             # Enforcement macros
│   └── _mcp_servers/           # MCP server implementations
│       ├── spec-inspector/     # Spec status MCP server
│       ├── coverage-reporter/  # Coverage metrics MCP server
│       └── db-inspector/       # Database schema MCP server (template)
├── multi-agent/
│   ├── prompts/                # ChatGPT & Gemini audit prompts
│   └── automation/             # Optional API integration
├── vscode-extension/           # VS Code extension (spec tree, guardrails)
├── integrations/               # IDE & CI/CD integrations
└── examples/
    ├── python-fastapi/         # Python/FastAPI example
    ├── typescript-node/        # TypeScript/Node example
    └── go-service/             # Go service example
```

## Examples

See the `examples/` directory for complete working examples:

- **[Python FastAPI](examples/python-fastapi/)** - User authentication with JWT, MFA
- **[Python Flask](examples/python-flask/)** - Blog API with SQLAlchemy, Blueprints
- **[Python Django](examples/python-django/)** - E-commerce API with DRF, multi-tenancy
- **[TypeScript Node](examples/typescript-node/)** - REST API with Prisma, Zod validation
- **[Go Service](examples/go-service/)** - Data pipeline with Chi router

### Recommended Additional Examples

See [examples/RECOMMENDATIONS.md](examples/RECOMMENDATIONS.md) for proposals on 5 additional framework examples (Rust, Java, Ruby, C#, PHP) to expand the collection to 10 total templates.

Each example includes:
- `.ldf/` configuration
- Complete spec (requirements → design → tasks)
- `AGENT.md` project instructions

## Documentation

- [Getting Started](docs/getting-started.md) - Installation and first spec
- [Task Format Guide](docs/task-format.md) - Task formatting and numbering
- [Concepts & Philosophy](docs/concepts.md) - Why spec-driven development
- [Multi-Agent Workflow](docs/multi-agent-workflow.md) - Using ChatGPT/Gemini for audits
- [Customization](docs/customization.md) - Adding guardrails and question-packs
- [VS Code Extension](docs/vscode-extension.md) - Visual spec management

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
