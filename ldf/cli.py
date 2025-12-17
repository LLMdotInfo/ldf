"""LDF CLI - Command line interface for the LLM Development Framework."""

from pathlib import Path

import click

from ldf import __version__
from ldf.utils.console import console
from ldf.utils.logging import configure_logging


@click.group()
@click.version_option(version=__version__, prog_name="ldf")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def main(ctx, verbose):
    """LDF - LLM Development Framework.

    Spec-driven development for AI-assisted software engineering.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        configure_logging(verbose=True)


@main.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    help="Project directory path (created if doesn't exist)",
)
@click.option(
    "--preset",
    type=click.Choice(["saas", "fintech", "healthcare", "api-only", "custom"]),
    default=None,
    help="Guardrail preset to use",
)
@click.option(
    "--question-packs",
    "-q",
    multiple=True,
    help="Question packs to include (e.g., security, testing)",
)
@click.option(
    "--mcp-servers",
    "-m",
    multiple=True,
    help="MCP servers to enable",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Non-interactive mode, accept defaults",
)
@click.option(
    "--hooks/--no-hooks",
    default=None,
    help="Install pre-commit hooks for spec validation",
)
def init(
    path: str | None,
    preset: str | None,
    question_packs: tuple,
    mcp_servers: tuple,
    yes: bool,
    hooks: bool | None,
):
    """Initialize LDF in a project directory.

    Creates .ldf/ directory with configuration, guardrails, and templates.
    Also generates CLAUDE.md for AI assistant integration.

    If --path is not provided, prompts for project location interactively.
    Use -y/--yes for non-interactive mode with defaults.

    Examples:
        ldf init                            # Interactive setup
        ldf init --path ./my-project        # Create project at path
        ldf init --preset saas              # Use SaaS preset
        ldf init -y                         # Non-interactive with defaults
        ldf init --hooks                    # Also install pre-commit hooks
    """
    from pathlib import Path as PathLib

    from ldf.init import initialize_project

    project_path = PathLib(path) if path else None

    initialize_project(
        project_path=project_path,
        preset=preset,
        question_packs=list(question_packs) if question_packs else None,
        mcp_servers=list(mcp_servers) if mcp_servers else None,
        non_interactive=yes,
        install_hooks=hooks if hooks is not None else False,
    )


@main.command()
@click.argument("spec_name", required=False)
@click.option("--all", "-a", "lint_all", is_flag=True, help="Lint all specs")
@click.option("--fix", "-f", is_flag=True, help="Auto-fix issues where possible")
@click.option(
    "--format",
    "-F",
    "output_format",
    type=click.Choice(["rich", "ci"]),
    default="rich",
    help="Output format: rich (default) for terminal, ci for GitHub Actions",
)
def lint(spec_name: str | None, lint_all: bool, fix: bool, output_format: str):
    """Validate spec files against guardrail requirements.

    Examples:
        ldf lint --all              # Lint all specs
        ldf lint user-auth          # Lint single spec
        ldf lint user-auth --fix    # Lint and auto-fix issues
        ldf lint --all --format ci  # CI-friendly output for GitHub Actions
    """
    from ldf.lint import lint_specs

    exit_code = lint_specs(spec_name, lint_all, fix, output_format=output_format)
    raise SystemExit(exit_code)


@main.command("create-spec")
@click.argument("name")
def create_spec(name: str):
    """Create a new feature specification from templates.

    Creates the spec directory structure with template files:

    \b
    - .ldf/specs/{name}/requirements.md
    - .ldf/specs/{name}/design.md
    - .ldf/specs/{name}/tasks.md
    - .ldf/answerpacks/{name}/

    Examples:
        ldf create-spec user-auth
        ldf create-spec payment-processing
    """
    from ldf.spec import create_spec as do_create_spec

    success = do_create_spec(name)
    if not success:
        raise SystemExit(1)


@main.command()
@click.option(
    "--type",
    "-t",
    "audit_type",
    type=click.Choice([
        "spec-review", "code-audit", "security", "pre-launch",
        "gap-analysis", "edge-cases", "architecture"
    ]),
    help="Type of audit request to generate",
)
@click.option(
    "--spec",
    "-s",
    "spec_name",
    help="Audit a specific spec only",
)
@click.option(
    "--import",
    "-i",
    "import_file",
    type=click.Path(exists=True),
    help="Import audit feedback from file",
)
@click.option("--api", is_flag=True, help="Use API automation (requires config)")
@click.option(
    "--include-secrets",
    is_flag=True,
    help="Include potentially sensitive content (API keys, tokens) in export",
)
@click.option(
    "-y", "--yes",
    is_flag=True,
    help="Skip confirmation prompts",
)
def audit(
    audit_type: str | None,
    spec_name: str | None,
    import_file: str | None,
    api: bool,
    include_secrets: bool,
    yes: bool,
):
    """Generate audit requests or import feedback from other AI agents.

    By default, potentially sensitive content is redacted from exports.
    Use --include-secrets to include all content.

    Audit types:

    \b
    - spec-review:   Completeness, clarity, edge cases
    - code-audit:    Code quality, security, test coverage
    - security:      Authentication, OWASP Top 10, data exposure
    - pre-launch:    Production readiness, monitoring, rollback
    - gap-analysis:  Missing requirements, coverage gaps
    - edge-cases:    Boundary conditions, error handling
    - architecture:  Component coupling, scalability, API design

    Redacted patterns include:

    \b
    - API keys (api_key=..., sk-*, pk-*, api_*)
    - Bearer tokens and JWTs
    - Passwords and secrets in key=value format
    - AWS access keys and secret keys
    - Long alphanumeric strings (40+ chars)
    - Secret environment variables ($SECRET_*, $TOKEN, etc.)

    Note: Redaction uses heuristic patterns. Unusual secrets may not be
    caught, and some normal text may be redacted. Review output if needed.

    Examples:
        ldf audit --type spec-review           # Review all specs
        ldf audit --type security --spec auth  # Security audit on auth spec
        ldf audit --type gap-analysis          # Find coverage gaps
        ldf audit --import feedback.md         # Import audit feedback
    """
    from ldf.audit import run_audit

    run_audit(audit_type, import_file, api, include_secrets, yes, spec_name)


@main.command("mcp-config")
@click.option(
    "--root",
    "-r",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Project root directory (defaults to current directory)",
)
@click.option(
    "--server",
    "-s",
    multiple=True,
    help="Include specific MCP server(s) (can be used multiple times)",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["claude", "json"]),
    default="claude",
    help="Output format: claude (mcpServers wrapper) or json (raw)",
)
def mcp_config(root: Path | None, server: tuple, output_format: str):
    """Generate MCP server configuration for AI assistants.

    Outputs JSON configuration pointing to LDF's MCP servers with paths
    configured for the specified project directory.

    The 'claude' format (default) outputs JSON suitable for .claude/mcp.json:

    \\b
    {
      "mcpServers": {
        "spec-inspector": { ... },
        "coverage-reporter": { ... }
      }
    }

    The 'json' format outputs just the server configurations without wrapper.

    Examples:
        ldf mcp-config                    # Config for current directory
        ldf mcp-config -r ./my-project    # Config for specific project
        ldf mcp-config -s spec-inspector  # Only spec-inspector server
        ldf mcp-config --format json      # Raw JSON output

    To create .claude/mcp.json:
        mkdir -p .claude && ldf mcp-config > .claude/mcp.json
    """
    from ldf.mcp_config import print_mcp_config

    servers = list(server) if server else None
    print_mcp_config(root, servers, output_format)


@main.command()
@click.option("--service", "-s", help="Service name for service-specific coverage")
@click.option("--guardrail", "-g", type=int, help="Guardrail ID for guardrail-specific coverage")
def coverage(service: str | None, guardrail: int | None):
    """Check test coverage against guardrail requirements.

    Examples:
        ldf coverage                 # Overall coverage
        ldf coverage --service auth  # Service-specific
        ldf coverage --guardrail 1   # Guardrail-specific (Testing Coverage)
    """
    from ldf.coverage import report_coverage

    report = report_coverage(service=service, guardrail_id=guardrail)
    if report.get("status") in ("FAIL", "ERROR"):
        raise SystemExit(1)


@main.group()
def hooks():
    """Manage Git hooks for LDF validation.

    Pre-commit hooks validate specs (and optionally code) before commits.
    """
    pass


@hooks.command("install")
@click.option(
    "--detect/--no-detect",
    default=True,
    help="Auto-detect and suggest language linters",
)
@click.option(
    "-y", "--yes",
    is_flag=True,
    help="Non-interactive mode, use detected defaults",
)
def hooks_install(detect: bool, yes: bool):
    """Install LDF pre-commit hook.

    By default, auto-detects project languages (Python, TypeScript, Go)
    and prompts to enable linting for each.

    Examples:
        ldf hooks install              # Interactive, auto-detects linters
        ldf hooks install --no-detect  # Skip detection, spec lint only
        ldf hooks install -y           # Non-interactive, enable detected linters
    """
    from ldf.hooks import install_hooks

    success = install_hooks(detect_linters=detect, non_interactive=yes)
    if not success:
        raise SystemExit(1)


@hooks.command("uninstall")
def hooks_uninstall():
    """Remove LDF pre-commit hook.

    Removes the hook from .git/hooks/pre-commit.
    Configuration in .ldf/config.yaml is preserved.
    """
    from ldf.hooks import uninstall_hooks

    success = uninstall_hooks()
    if not success:
        raise SystemExit(1)


@hooks.command("status")
def hooks_status():
    """Show hook installation status and configuration.

    Displays whether the hook is installed and what checks are enabled.
    """
    from ldf.hooks import print_hooks_status

    print_hooks_status()


if __name__ == "__main__":
    main()
