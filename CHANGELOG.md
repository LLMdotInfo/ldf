# Changelog

All notable changes to LDF (LLM Development Framework) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-29

### Added
- **Python 3.13 and 3.14 Support** - Extended compatibility testing to Python 3.13 and 3.14
- **Node.js 22 Support** - Added Node.js 22 to ldf-vscode test matrix

### Changed
- **Updated Development Dependencies** - pytest ≥8.0.0, pytest-cov ≥5.0.0, black ≥24.0.0, ruff ≥0.5.0, mypy ≥1.10.0
- **Improved Exception Handling** - Narrowed exception types and added debug logging across 8 modules for better observability
- **TypeScript 5.5** - Updated ldf-vscode to TypeScript ^5.5.0

### Fixed
- **Silent Exception Suppression** - Added logging/user feedback for previously silent failures in:
  - `ldf/doctor.py` - Auto-fix failures now show warnings
  - `ldf/mcp_health.py` - Config parse errors display warnings
  - `ldf/convert.py` - Framework detection logs debug info
  - `ldf/workspace/commands.py` - Registry read errors logged
  - `ldf/cli.py` - Template discovery errors logged
  - `ldf/docs.py` - Pack YAML errors logged as warnings
  - `ldf/template.py` - Unreadable files during secret scan logged
  - `ldf/_mcp_servers/coverage_reporter/guardrail_validator.py` - Guardrail loader fallbacks logged

---

## [1.1.1] - 2025-12-29

### Fixed

#### Workspace Targeting
- **`--project` flag now works** - Commands (`lint`, `audit`, `coverage`, `status`, `create-spec`) now correctly use the specified project context instead of always using `cwd`
- **Priority order documented** - CLI flag (`--project`) > env var (`LDF_PROJECT`) > auto-detect from cwd

#### N/A Status Handling
- **N/A counting fixed** - Guardrail tracker now correctly counts "N/A - reason" status (uses `startswith` instead of exact match)
- **Justification required** - `ldf lint` now warns when N/A status lacks justification (use format: "N/A - <reason>")

#### Reference Deduplication
- **Duplicate references removed** - `parse_references()` now deduplicates by (project, spec, section) to prevent duplicate lint errors

#### Workspace Discovery
- **Basename collision detection** - Warns when multiple discovered projects have the same alias (e.g., `services/auth` and `libs/auth` both becoming "auth")

#### MCP Health
- **Dynamic guardrail counts** - `mcp-health` now uses `get_active_guardrails()` instead of hardcoded count of 8

### Changed
- `get_project_context()` now returns `ProjectContext` with `project_root` for cleaner code
- Commands gracefully fall back to `cwd` when not in an LDF project (for `status` showing "new" state)

---

## [1.1.0] - 2025-12-27

### Added

#### Multi-Project Workspace Support
- **`ldf-workspace.yaml`** - Workspace manifest for managing multiple LDF projects
- **`ldf workspace init`** - Initialize a multi-project workspace
- **`ldf workspace add`** - Add a project to the workspace
- **`ldf workspace list`** - List all projects in the workspace
- **`ldf workspace sync`** - Sync all projects in the workspace
- **Cross-Project References** - Reference specs across projects with `@project:spec#section` syntax
- **Shared Resources** - Inherit guardrails, templates, and question-packs from `.ldf-shared/`
- **Workspace-Wide Validation** - Lint and validate across all projects with `--validate-refs`

#### Test Coverage & Quality
- **92% Test Coverage** - Comprehensive test suite with 1,302 passing tests
- **Coverage Threshold** - Minimum 90% coverage enforced in CI
- **New Test Modules** - project_resolver, workspace_commands, workspace_models, references, spec_list, template_mgmt
- **Output Format Tests** - JSON, SARIF, and text output validation for lint and template commands

#### Security Hardening
- **Empty String Validation** - MCP spec_inspector validates spec names
- **Python Interpreter Path** - MCP config uses `sys.executable` for correct venv handling
- **Path Parts Matching** - Workspace exclusions use path parts instead of substring matching
- **Error Surfacing** - YAML parse errors in workspace manifest are properly reported

### Changed
- Version number now aligns with config schema version (1.1)

### Removed
- Deprecated CLI flags: `--service`, `--validate`, `--diff`, `--json` on status command
- `list-framework` command group (use `status` instead)
- Legacy v1.0 schema support (upgrade projects with `ldf update`)

### Fixed
- **Workspace CLI Flags** - `--create-shared`, `--rebuild-registry`, `--validate-refs` now support `--no-*` variants
- **import_ai_response Validator** - Uses comprehensive `validate_spec_name` instead of weaker `sanitize_spec_name`

## [1.0.0] - 2025-12-26

### Added

#### Core CLI Commands
- **`ldf init`** - Initialize LDF in a project with presets, question-packs, and MCP servers
- **`ldf status`** - Show project state and framework version
- **`ldf lint`** - Validate specs with optional strict mode and CI-friendly output
- **`ldf create-spec`** - Create new specs interactively or with templates
- **`ldf audit`** - Generate and import multi-agent audit prompts
- **`ldf coverage`** - Report test coverage mapped to specs
- **`ldf convert`** - Convert existing codebases to LDF methodology
- **`ldf update`** - Update framework files with conflict resolution
- **`ldf hooks`** - Install/remove git pre-commit hooks for spec validation
- **`ldf doctor`** - Run project health checks
- **`ldf mcp-config`** - Generate MCP server configuration for Claude/Cursor/Gemini
- **`ldf export-docs`** - Export documentation for review

#### Guardrails System
- **8 Core Guardrails** - Testing, Security, Error Handling, Logging, API Design, Data Validation, Database Migrations, Documentation
- **4 Domain Presets** - saas, fintech, healthcare, api-only
- **Custom Guardrails** - Define project-specific guardrails in YAML
- **Guardrail Coverage Matrix** - Track coverage across requirements, design, and tasks

#### Question-Packs
- **security** - Authentication, authorization, data protection decisions
- **testing** - Test strategy, coverage requirements, mocking approaches
- **api-design** - Versioning, pagination, error format decisions
- **data-model** - Schema design, relationships, migration strategy

#### Template System
- **Jinja2 Macros** - clarify-first, coverage-gate, task-guardrails
- **Template Import/Export** - Share configurations across projects
- **Markdown Templates** - requirements.md, design.md, tasks.md formats

#### MCP Server Integration
- **spec_inspector** - Query spec status and guardrail coverage (90% token savings)
- **coverage_reporter** - Report test coverage metrics per spec
- **db_inspector** - Database schema inspection template

#### Multi-Agent Audit Workflow
- **ChatGPT Integration** - Generate prompts and import feedback via API
- **Gemini Integration** - Architecture review and gap analysis
- **Audit Types** - spec-review, security-check, gap-analysis, edge-cases
- **Audit History** - Track and compare audits over time

#### Security Hardening
- **Path Traversal Prevention** - Validates all spec names and paths
- **Symlink Escape Protection** - Prevents symlink-based directory escapes
- **Safe Template Import** - Validates zip archives before extraction
- **Input Validation** - Comprehensive validation at all entry points

#### Cross-Platform Support
- **Windows** - Full support including batch file handling
- **macOS** - Native support with Homebrew compatibility
- **Linux** - Tested on Ubuntu, Fedora, and derivatives

### Commands Reference

| Command | Description |
|---------|-------------|
| `ldf init` | Initialize LDF in a project |
| `ldf status` | Show project state |
| `ldf lint [SPEC]` | Validate spec(s) |
| `ldf create-spec NAME` | Create a new spec |
| `ldf audit --type TYPE --spec SPEC` | Run multi-agent audit |
| `ldf coverage` | Report test coverage |
| `ldf convert` | Convert existing codebase |
| `ldf update` | Update framework files |
| `ldf hooks install` | Install git hooks |
| `ldf doctor` | Check project health |
| `ldf mcp-config` | Generate MCP config |

### Dependencies
- Python 3.10+
- click >= 8.0.0
- pyyaml >= 6.0
- rich >= 13.0.0
- jinja2 >= 3.0.0
- questionary >= 2.0.0

### Optional Dependencies
- **mcp**: MCP server support (mcp >= 0.9.0, coverage >= 7.0.0)
- **automation**: API integration (openai >= 1.0.0, google-generativeai >= 0.3.0)
- **s3**: S3 template storage (boto3 >= 1.26.0)
