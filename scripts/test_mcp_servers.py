#!/usr/bin/env python3
"""
MCP Server Validation Script

Tests that MCP servers can be imported and their tools are properly defined.
Does NOT require a running database or coverage data - just validates structure.

Usage:
    python scripts/test_mcp_servers.py
    python scripts/test_mcp_servers.py --server spec_inspector
    python scripts/test_mcp_servers.py --verbose
"""

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def load_module(path: Path, module_name: str) -> Any:
    """Dynamically load a Python module from path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    # Don't execute the module, just load it
    return module


def check_file_exists(path: Path, name: str) -> tuple[bool, str]:
    """Check if file exists and is non-empty."""
    if not path.exists():
        return False, f"{name}: File not found at {path}"
    if path.stat().st_size == 0:
        return False, f"{name}: File is empty"
    return True, f"{name}: Found ({path.stat().st_size} bytes)"


def check_python_syntax(path: Path, name: str) -> tuple[bool, str]:
    """Check Python file for syntax errors."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            code = f.read()
        compile(code, path, "exec")
        return True, f"{name}: Syntax OK"
    except SyntaxError as e:
        return False, f"{name}: Syntax error at line {e.lineno}: {e.msg}"
    except UnicodeDecodeError as e:
        return False, f"{name}: Encoding error: {e}"


def check_imports(path: Path, name: str) -> tuple[bool, str]:
    """Check that required imports are present in the file."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        required = ["from mcp.server import Server", "from mcp import types"]
        missing = [imp for imp in required if imp not in content]

        if missing:
            return False, f"{name}: Missing imports: {missing}"
        return True, f"{name}: Required imports present"
    except Exception as e:
        return False, f"{name}: Error checking imports: {e}"


def check_tool_definitions(path: Path, name: str) -> tuple[bool, str]:
    """Check that tools are properly defined."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Check for list_tools decorator
        if "@app.list_tools()" not in content:
            return False, f"{name}: Missing @app.list_tools() decorator"

        # Check for call_tool decorator
        if "@app.call_tool()" not in content:
            return False, f"{name}: Missing @app.call_tool() decorator"

        # Count types.Tool definitions
        tool_count = content.count("types.Tool(")
        if tool_count == 0:
            return False, f"{name}: No tools defined"

        return True, f"{name}: Found {tool_count} tool definitions"
    except Exception as e:
        return False, f"{name}: Error checking tools: {e}"


def validate_spec_inspector(mcp_dir: Path, verbose: bool = False) -> list[tuple[bool, str]]:
    """Validate spec_inspector MCP server."""
    results = []
    server_dir = mcp_dir / "spec_inspector"

    # Check required files
    files = [
        ("server.py", server_dir / "server.py"),
        ("spec_parser.py", server_dir / "spec_parser.py"),
        ("guardrail_tracker.py", server_dir / "guardrail_tracker.py"),
        ("requirements.txt", server_dir / "requirements.txt"),
        ("README.md", server_dir / "README.md"),
    ]

    for name, path in files:
        results.append(check_file_exists(path, name))

    # Check Python syntax
    python_files = [f for f in files if f[0].endswith(".py")]
    for name, path in python_files:
        if path.exists():
            results.append(check_python_syntax(path, name))

    # Check server.py specifics
    server_path = server_dir / "server.py"
    if server_path.exists():
        results.append(check_imports(server_path, "server.py"))
        results.append(check_tool_definitions(server_path, "server.py"))

    return results


def validate_coverage_reporter(mcp_dir: Path, verbose: bool = False) -> list[tuple[bool, str]]:
    """Validate coverage_reporter MCP server."""
    results = []
    server_dir = mcp_dir / "coverage_reporter"

    # Check required files
    files = [
        ("server.py", server_dir / "server.py"),
        ("coverage_parser.py", server_dir / "coverage_parser.py"),
        ("guardrail_validator.py", server_dir / "guardrail_validator.py"),
        ("requirements.txt", server_dir / "requirements.txt"),
        ("README.md", server_dir / "README.md"),
    ]

    for name, path in files:
        results.append(check_file_exists(path, name))

    # Check Python syntax
    python_files = [f for f in files if f[0].endswith(".py")]
    for name, path in python_files:
        if path.exists():
            results.append(check_python_syntax(path, name))

    # Check server.py specifics
    server_path = server_dir / "server.py"
    if server_path.exists():
        results.append(check_imports(server_path, "server.py"))
        results.append(check_tool_definitions(server_path, "server.py"))

    return results


def validate_db_inspector_template(mcp_dir: Path, verbose: bool = False) -> list[tuple[bool, str]]:
    """Validate db_inspector template (optional server)."""
    results = []
    server_dir = mcp_dir / "db_inspector"
    template_dir = server_dir / "template"

    # Check main README
    results.append(check_file_exists(server_dir / "README.md", "README.md"))

    # Check template files
    files = [
        ("template/server.py", template_dir / "server.py"),
        ("template/schema_query.py", template_dir / "schema_query.py"),
        ("template/requirements.txt", template_dir / "requirements.txt"),
    ]

    for name, path in files:
        results.append(check_file_exists(path, name))

    # Check Python syntax
    python_files = [f for f in files if f[0].endswith(".py")]
    for name, path in python_files:
        if path.exists():
            results.append(check_python_syntax(path, name))

    # Check server.py specifics
    server_path = template_dir / "server.py"
    if server_path.exists():
        results.append(check_imports(server_path, "template/server.py"))
        results.append(check_tool_definitions(server_path, "template/server.py"))

    return results


def validate_mcp_setup(mcp_dir: Path, verbose: bool = False) -> list[tuple[bool, str]]:
    """Validate MCP_SETUP.md documentation."""
    results = []
    setup_path = mcp_dir / "MCP_SETUP.md"

    results.append(check_file_exists(setup_path, "MCP_SETUP.md"))

    if setup_path.exists():
        with open(setup_path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Check for required sections
        sections = [
            "## Prerequisites",
            "## Quick Setup",
            "spec_inspector",
            "coverage_reporter",
            ".agent/mcp.json",
        ]

        for section in sections:
            if section in content:
                results.append((True, f"MCP_SETUP.md: Contains '{section}'"))
            else:
                results.append((False, f"MCP_SETUP.md: Missing '{section}'"))

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate MCP server structure")
    parser.add_argument(
        "--server",
        choices=["spec_inspector", "coverage_reporter", "db_inspector", "all"],
        default="all",
        help="Which server to validate",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all results, not just failures",
    )
    parser.add_argument(
        "--mcp-dir",
        type=Path,
        default=None,
        help="Path to mcp-servers directory",
    )
    args = parser.parse_args()

    # Find MCP servers directory
    if args.mcp_dir:
        mcp_dir = args.mcp_dir
    else:
        # Try to find it relative to script location
        script_dir = Path(__file__).parent
        mcp_dir = script_dir.parent / "mcp-servers"
        if not mcp_dir.exists():
            # Try current directory
            mcp_dir = Path("mcp-servers")

    if not mcp_dir.exists():
        print(f"{Colors.RED}Error: MCP servers directory not found at {mcp_dir}{Colors.RESET}")
        sys.exit(1)

    print(f"{Colors.BOLD}LDF MCP Server Validation{Colors.RESET}")
    print(f"Directory: {mcp_dir}\n")

    all_results = []
    servers_to_check = []

    if args.server == "all":
        servers_to_check = ["spec_inspector", "coverage_reporter", "db_inspector", "setup"]
    else:
        servers_to_check = [args.server]

    # Run validations
    for server in servers_to_check:
        print(f"{Colors.BLUE}Checking {server}...{Colors.RESET}")

        if server == "spec_inspector":
            results = validate_spec_inspector(mcp_dir, args.verbose)
        elif server == "coverage_reporter":
            results = validate_coverage_reporter(mcp_dir, args.verbose)
        elif server == "db_inspector":
            results = validate_db_inspector_template(mcp_dir, args.verbose)
        elif server == "setup":
            results = validate_mcp_setup(mcp_dir, args.verbose)
        else:
            continue

        all_results.extend(results)

        # Display results
        for success, message in results:
            if args.verbose or not success:
                color = Colors.GREEN if success else Colors.RED
                symbol = "✓" if success else "✗"
                print(f"  {color}{symbol}{Colors.RESET} {message}")

        print()

    # Summary
    passed = sum(1 for success, _ in all_results if success)
    failed = sum(1 for success, _ in all_results if not success)
    total = len(all_results)

    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Passed: {Colors.GREEN}{passed}/{total}{Colors.RESET}")
    if failed > 0:
        print(f"  Failed: {Colors.RED}{failed}/{total}{Colors.RESET}")
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}All validations passed!{Colors.RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
