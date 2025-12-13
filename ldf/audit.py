"""LDF multi-agent audit functionality."""

import re
from pathlib import Path

from rich.markdown import Markdown
from rich.prompt import Confirm

from ldf.utils.console import console

# Patterns to redact when include_secrets=False
REDACTION_PATTERNS = [
    # PEM private keys (multiline) - must be first to catch entire blocks
    (r'-----BEGIN[A-Z ]*PRIVATE KEY-----[\s\S]*?-----END[A-Z ]*PRIVATE KEY-----', '[PEM_KEY_REDACTED]'),
    # PEM certificates and other sensitive blocks
    (r'-----BEGIN[A-Z ]*(?:PRIVATE|SECRET|ENCRYPTED)[A-Z ]*-----[\s\S]*?-----END[A-Z ]*(?:PRIVATE|SECRET|ENCRYPTED)[A-Z ]*-----', '[PEM_BLOCK_REDACTED]'),

    # JWTs (header.payload.signature - base64url encoded)
    (r'\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\b', '[JWT_REDACTED]'),

    # GitHub tokens (ghp_, gho_, ghs_, ghr_)
    (r'\b(ghp|gho|ghs|ghr)_[A-Za-z0-9]{36,}\b', '[GITHUB_TOKEN_REDACTED]'),

    # Slack tokens
    (r'\bxox[baprs]-[A-Za-z0-9-]+\b', '[SLACK_TOKEN_REDACTED]'),

    # GitLab tokens
    (r'\bglpat-[A-Za-z0-9\-_]{20,}\b', '[GITLAB_TOKEN_REDACTED]'),

    # npm tokens
    (r'\bnpm_[A-Za-z0-9]{36,}\b', '[NPM_TOKEN_REDACTED]'),

    # API keys, secrets, passwords, tokens with values (key=value or key: value patterns)
    (r'(?i)(api[_-]?key|secret|password|token|credential|auth)["\']?\s*[:=]\s*["\']?[^\s"\']{8,}', r'\1=[REDACTED]'),

    # Prefixed API keys (sk-, pk-, api_, etc.)
    (r'(?i)\b(sk|pk|api|key|secret|token)[_-][a-zA-Z0-9\-_]{16,}\b', '[API_KEY_REDACTED]'),

    # Bearer tokens
    (r'(?i)bearer\s+[a-zA-Z0-9\-._~+/]{20,}=*', 'Bearer [REDACTED]'),

    # AWS-style keys
    (r'(?i)(aws[_-]?(?:access[_-]?key|secret)[_-]?(?:id)?)\s*[:=]\s*["\']?[A-Z0-9]{16,}', r'\1=[REDACTED]'),
    (r'\bAKIA[A-Z0-9]{16}\b', '[AWS_ACCESS_KEY_REDACTED]'),

    # Base64-encoded secrets (long base64 that looks like credentials - 64+ chars)
    (r'(?<=["\':=\s])[A-Za-z0-9+/]{64,}={0,2}(?=["\'\s,\n]|$)', '[BASE64_REDACTED]'),

    # Generic long alphanumeric strings that look like secrets (40+ chars)
    (r'(?<=["\':=\s])[a-zA-Z0-9]{40,}(?=["\'\s,\n]|$)', '[POSSIBLE_SECRET_REDACTED]'),

    # Environment variable references with secret-like names
    (r'\$\{?(?:SECRET|TOKEN|PASSWORD|API_KEY|CREDENTIALS)[_A-Z]*\}?', '[ENV_VAR_REDACTED]'),

    # Generic private/secret JSON keys with long values
    (r'(?i)"[^"]*(?:private|secret|password|token|key|credential)[^"]*"\s*:\s*"[^"]{20,}"', '"[SENSITIVE_KEY]": "[REDACTED]"'),
]


def _redact_content(content: str) -> str:
    """Redact potentially sensitive content from spec export.

    Args:
        content: Raw content to redact

    Returns:
        Content with sensitive patterns redacted
    """
    redacted = content
    for pattern, replacement in REDACTION_PATTERNS:
        redacted = re.sub(pattern, replacement, redacted)
    return redacted


def run_audit(
    audit_type: str | None,
    import_file: str | None,
    use_api: bool,
    include_secrets: bool = False,
    skip_confirm: bool = False,
    spec_name: str | None = None,
) -> None:
    """Run audit request generation or import feedback.

    Args:
        audit_type: Type of audit (spec-review, code-audit, security, pre-launch,
            gap-analysis, edge-cases, architecture)
        import_file: Path to feedback file to import
        use_api: Whether to use API automation
        include_secrets: Whether to include potentially sensitive content
        skip_confirm: Whether to skip confirmation prompts
        spec_name: Optional specific spec to audit (audits all if not provided)
    """
    if import_file:
        _import_feedback(Path(import_file))
    elif audit_type:
        _generate_audit_request(audit_type, use_api, include_secrets, skip_confirm, spec_name)
    else:
        console.print("[red]Error: Specify --type or --import[/red]")
        console.print("\nExamples:")
        console.print("  ldf audit --type spec-review")
        console.print("  ldf audit --type gap-analysis --spec user-auth")
        console.print("  ldf audit --import feedback.md")


def _generate_audit_request(
    audit_type: str,
    use_api: bool,
    include_secrets: bool = False,
    skip_confirm: bool = False,
    spec_name: str | None = None,
) -> None:
    """Generate an audit request for external AI agents.

    Args:
        audit_type: Type of audit request
        use_api: Whether to use API automation
        include_secrets: Whether to include sensitive content
        skip_confirm: Whether to skip confirmation prompts
        spec_name: Optional specific spec to audit
    """
    console.print(f"\n[bold blue]Generating {audit_type} audit request...[/bold blue]\n")

    # Find specs to include
    specs_dir = Path.cwd() / ".ldf" / "specs"
    if not specs_dir.exists():
        console.print("[red]Error: .ldf/specs/ not found. Run 'ldf init' first.[/red]")
        return

    # Filter to specific spec if requested
    if spec_name:
        spec_path = specs_dir / spec_name
        if not spec_path.exists() or not spec_path.is_dir():
            console.print(f"[red]Error: Spec '{spec_name}' not found.[/red]")
            console.print(f"[dim]Available specs: {', '.join(d.name for d in specs_dir.iterdir() if d.is_dir())}[/dim]")
            return
        specs = [spec_path]
    else:
        specs = [d for d in specs_dir.iterdir() if d.is_dir()]

    if not specs:
        console.print("[yellow]No specs found to audit.[/yellow]")
        return

    # Generate audit request markdown
    output_path = Path.cwd() / f"audit-request-{audit_type}.md"
    content = _build_audit_request(audit_type, specs, include_secrets)

    # Warning and confirmation before export
    if not skip_confirm:
        console.print()
        console.print("[bold yellow]WARNING:[/bold yellow] This export will include spec content.")
        if include_secrets:
            console.print(
                "[bold red]SECRETS INCLUDED:[/bold red] "
                "Potentially sensitive content (API keys, tokens) will NOT be redacted."
            )
        else:
            console.print(
                "[dim]Sensitive patterns (API keys, tokens, passwords) will be redacted.[/dim]"
            )
        console.print()
        console.print(f"Output file: [cyan]{output_path}[/cyan]")
        console.print(f"Specs included: [cyan]{len(specs)}[/cyan]")
        console.print()

        if not Confirm.ask("Proceed with export?", default=True):
            console.print("[red]Aborted.[/red]")
            return

    output_path.write_text(content)

    console.print(f"[green]Generated: {output_path}[/green]")
    if not include_secrets:
        console.print("[dim]Note: Sensitive content was redacted. Use --include-secrets to include.[/dim]")
    console.print("\nNext steps:")
    console.print("  1. Copy the content of this file")
    console.print("  2. Paste into ChatGPT or Gemini with the appropriate prompt")
    console.print(f"  3. Save the response and run: ldf audit --import feedback.md")

    if use_api:
        console.print("\n[yellow]API automation not yet implemented.[/yellow]")
        console.print("Configure API keys in .ldf/config.yaml to enable.")


def _build_audit_request(
    audit_type: str,
    specs: list[Path],
    include_secrets: bool = False,
) -> str:
    """Build the audit request content.

    Args:
        audit_type: Type of audit request
        specs: List of spec directory paths
        include_secrets: Whether to include sensitive content unredacted

    Returns:
        Formatted audit request markdown
    """
    content = f"""# Audit Request: {audit_type.replace('-', ' ').title()}

## Instructions

Please review the following specifications and provide feedback on:

"""
    if audit_type == "spec-review":
        content += """- Completeness of requirements
- Clarity of acceptance criteria
- Missing edge cases
- Potential security concerns
- Guardrail coverage gaps
"""
    elif audit_type == "code-audit":
        content += """- Code quality and patterns
- Security vulnerabilities
- Performance concerns
- Test coverage gaps
- Documentation completeness
"""
    elif audit_type == "security":
        content += """- Authentication/authorization gaps
- Input validation issues
- OWASP Top 10 vulnerabilities
- Data exposure risks
- Secure coding practices
"""
    elif audit_type == "pre-launch":
        content += """- Production readiness
- Error handling completeness
- Monitoring/observability
- Rollback procedures
- Security hardening
"""
    elif audit_type == "gap-analysis":
        content += """- Missing requirements or user stories
- Untested edge cases
- Guardrail coverage gaps
- Undefined error scenarios
- Missing acceptance criteria
- Incomplete test coverage mapping
"""
    elif audit_type == "edge-cases":
        content += """- Boundary conditions (min/max values, empty inputs)
- Error handling paths
- Concurrent access scenarios
- Data validation edge cases
- Network failure handling
- Resource exhaustion scenarios
"""
    elif audit_type == "architecture":
        content += """- Component coupling analysis
- Scalability concerns
- Data flow correctness
- API design consistency
- Dependency management
- State management patterns
"""

    content += "\n## Specifications\n\n"

    for spec_path in specs:
        spec_name = spec_path.name
        content += f"### {spec_name}\n\n"

        for filename in ["requirements.md", "design.md", "tasks.md"]:
            filepath = spec_path / filename
            if filepath.exists():
                spec_content = filepath.read_text()

                # Apply redaction unless include_secrets is True
                if not include_secrets:
                    spec_content = _redact_content(spec_content)

                # Truncate if too long
                if len(spec_content) > 5000:
                    spec_content = spec_content[:5000] + "\n\n... (truncated)"
                content += f"#### {filename}\n\n```markdown\n{spec_content}\n```\n\n"

    content += """## Response Format

Please provide your feedback in the following format:

```markdown
## Findings

### Critical Issues
- Issue 1: [description]
- Issue 2: [description]

### Warnings
- Warning 1: [description]

### Suggestions
- Suggestion 1: [description]

## Summary

[Overall assessment and recommendations]
```
"""
    return content


def _import_feedback(feedback_path: Path) -> None:
    """Import audit feedback from external AI agents."""
    if not feedback_path.exists():
        console.print(f"[red]Error: File not found: {feedback_path}[/red]")
        return

    content = feedback_path.read_text()
    console.print(f"\n[bold blue]Importing feedback from: {feedback_path}[/bold blue]\n")

    # Display the feedback
    console.print(Markdown(content))

    # Save to .ldf/audit-history/
    audit_dir = Path.cwd() / ".ldf" / "audit-history"
    audit_dir.mkdir(exist_ok=True)

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    saved_path = audit_dir / f"feedback-{timestamp}.md"
    saved_path.write_text(content)

    console.print(f"\n[green]Feedback saved to: {saved_path}[/green]")
    console.print("\nNext steps:")
    console.print("  1. Review the findings above")
    console.print("  2. Update specs to address critical issues")
    console.print("  3. Run 'ldf lint' to validate changes")
