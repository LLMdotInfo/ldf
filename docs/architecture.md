# LDF Architecture Guide

This guide explains how LDF is structured for contributors and maintainers.

## Module Map

```
ldf/
├── cli.py              # Click CLI entry point (thin layer)
├── init.py             # Project initialization & repair
├── update.py           # Framework file updates, conflict resolution
├── lint.py             # Spec validation
├── audit.py            # Multi-agent audit generation/import
├── audit_api.py        # API integration for automated audits
├── detection.py        # Project state detection (NEW, CURRENT, OUTDATED, etc.)
├── convert.py          # Backwards fill for existing codebases
├── coverage.py         # Test coverage reporting
├── hooks.py            # Git hook management
├── mcp_config.py       # MCP server configuration generation
├── spec.py             # Spec file operations
├── prompts.py          # Interactive prompt utilities
└── utils/
    ├── config.py       # Configuration loading/saving
    ├── console.py      # Rich console output
    ├── descriptions.py # Human-readable descriptions
    ├── guardrail_loader.py  # Guardrail YAML parsing
    ├── hooks.py        # Pre-commit hook utilities
    ├── logging.py      # Structured logging setup
    └── spec_parser.py  # Spec markdown parsing
```

## Module Responsibilities

### CLI Layer (`cli.py`)

The CLI is a thin layer using Click that:
- Parses command-line arguments
- Calls into domain modules
- Formats output using Rich

**Pattern**: CLI functions should handle user interaction (prompts, output) but delegate business logic to domain modules.

### Domain Modules

| Module | Responsibility |
|--------|---------------|
| `init.py` | Creates `.ldf/` structure, copies framework files, handles `--force` and `--repair` modes |
| `update.py` | Compares framework files using checksums, handles conflicts, preserves user content |
| `lint.py` | Validates spec files against rules, checks guardrail coverage matrices |
| `audit.py` | Generates audit prompts for external LLMs, imports feedback into audit history |
| `audit_api.py` | Integrates with OpenAI/Google APIs for automated audits |
| `detection.py` | Determines project state from `.ldf/` structure and config version |
| `convert.py` | Analyzes codebases for backwards fill, parses AI-generated specs |
| `coverage.py` | Parses coverage reports, maps to specs/guardrails |
| `hooks.py` | Manages git pre-commit hooks for spec validation |
| `mcp_config.py` | Generates MCP server configuration for Claude |

## Data Flow

### Framework → Project

When `ldf init` runs, framework files are copied to the project:

```
framework/                         .ldf/ (project)
├── templates/           ──copy──▶ templates/
│   ├── requirements.md            ├── requirements.md
│   ├── design.md                  ├── design.md
│   └── tasks.md                   └── tasks.md
├── guardrails/
│   ├── core.yaml        ──merge─▶ guardrails.yaml
│   └── presets/*.yaml
├── question-packs/      ──copy──▶ question-packs/
│   ├── core/*.yaml                ├── security.yaml
│   └── domain/*.yaml              ├── testing.yaml
├── macros/              ──copy──▶ macros/
│   ├── clarify-first.md           ├── clarify-first.md
│   └── ...                        └── ...
└── commands/            ──copy──▶ .claude/commands/
    └── *.md                       └── *.md
```

### Update Flow

When `ldf update` runs:

1. Load checksums from `.ldf/config.yaml`
2. For each framework file:
   - **Templates/Macros**: Always replace (strategy: `replace`)
   - **Question-packs**: Check if user modified → prompt if yes (strategy: `replace_if_unmodified`)
3. **Never touch**: `specs/`, `answerpacks/`, `guardrails.yaml` (user content)
4. Update `framework_version` and checksums in config

### Detection Flow

`detect_project_state()` returns one of:

| State | Condition |
|-------|-----------|
| `NEW` | No `.ldf/` directory |
| `CURRENT` | `framework_version` matches installed version |
| `OUTDATED` | `framework_version` < installed version |
| `LEGACY` | Has `.ldf/` but no `framework_version` |
| `PARTIAL` | Missing required files (templates, macros) |
| `CORRUPTED` | Invalid YAML or structure |

## MCP Server Integration

MCP servers in `mcp-servers/` are standalone Python scripts:

```
mcp-servers/
├── spec-inspector/     # Query specs, tasks, guardrail coverage
├── coverage-reporter/  # Test coverage metrics
└── db-inspector/       # Database schema inspection (template)
```

**How they integrate:**

1. `ldf mcp-config` generates Claude's `.claude/mcp.json`
2. Config points to server scripts with project path as argument
3. Servers read from `.ldf/` at runtime
4. Claude calls servers via MCP protocol

**Example generated config:**
```json
{
  "mcpServers": {
    "spec-inspector": {
      "command": "python",
      "args": ["/path/to/mcp-servers/spec-inspector/server.py", "--project", "/path/to/project"]
    }
  }
}
```

## Configuration Schema

### `.ldf/config.yaml`

```yaml
# Framework version for update tracking
framework_version: "0.1.0"

# Selected preset during init
preset: saas

# Question packs copied during init
question_packs:
  - security
  - testing
  - api-design
  - data-model

# MCP servers enabled
mcp_servers:
  - spec-inspector
  - coverage-reporter

# Checksums for update tracking (auto-generated)
checksums:
  question-packs/security.yaml: "abc123..."
  question-packs/testing.yaml: "def456..."

# API configuration for automated audits (optional)
audit_api:
  chatgpt:
    api_key: ${OPENAI_API_KEY}
    model: gpt-4
  gemini:
    api_key: ${GOOGLE_API_KEY}
    model: gemini-pro
```

## Testing Patterns

### Fixtures

Common fixtures in `tests/conftest.py`:

- `tmp_path` - pytest built-in for temp directories
- `initialized_project` - project with `ldf init` run
- `cli_runner` - Click's test runner

### Testing CLI Commands

```python
def test_command(cli_runner, tmp_path):
    result = cli_runner.invoke(main, ["status"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "State:" in result.output
```

### Testing Domain Logic

```python
def test_detection(tmp_path):
    # Setup
    (tmp_path / ".ldf").mkdir()
    (tmp_path / ".ldf" / "config.yaml").write_text("framework_version: '0.1.0'")

    # Test
    result = detect_project_state(tmp_path)

    # Assert
    assert result.state == ProjectState.CURRENT
```

## Adding New Features

### New CLI Command

1. Add command function in `cli.py` with `@main.command()` decorator
2. Create domain module if needed (e.g., `ldf/new_feature.py`)
3. Add tests in `tests/test_new_feature.py`
4. Update `README.md` CLI Reference section

### New Framework File

1. Add file to `framework/` directory
2. Update `init.py` to copy it during initialization
3. Update `update.py` to handle it during updates
4. Add to `REQUIRED_*` constants in `detection.py` if mandatory

### New MCP Server

1. Create server directory in `mcp-servers/`
2. Implement `server.py` with MCP SDK
3. Add server name to `mcp_config.py` server list
4. Document in `mcp-servers/README.md`

## Error Handling

- Domain modules raise exceptions with descriptive messages
- CLI catches and formats errors with Rich
- `utils/logging.py` provides structured logging
- Exit codes: 0 = success, 1 = error, 2 = user abort

## Code Style

- Type hints on all public functions
- Docstrings in Google style
- `black` for formatting
- `ruff` for linting
- Tests with `pytest`
