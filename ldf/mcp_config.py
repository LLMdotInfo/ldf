"""MCP configuration generator for LDF projects."""

import json
from pathlib import Path


def get_ldf_installation_path() -> Path:
    """Get the LDF package installation path.

    Returns:
        Path to the LDF package root directory (containing mcp-servers/).
    """
    # The mcp_config.py file is at ldf/mcp_config.py
    # LDF root is one level up from that
    return Path(__file__).parent.parent.resolve()


def generate_mcp_config(
    project_root: Path | None = None,
    servers: list[str] | None = None,
    output_format: str = "claude",
) -> str:
    """Generate MCP server configuration JSON.

    Args:
        project_root: Project directory (defaults to cwd)
        servers: List of server names to include (defaults to all available)
        output_format: Output format - "claude" wraps in mcpServers, "json" is raw

    Returns:
        JSON string with MCP configuration
    """
    if project_root is None:
        project_root = Path.cwd()
    project_root = project_root.resolve()

    ldf_path = get_ldf_installation_path()
    mcp_servers_dir = ldf_path / "mcp-servers"

    # Available servers
    available_servers = {
        "spec-inspector": {
            "command": "python",
            "args": [str(mcp_servers_dir / "spec-inspector" / "server.py")],
            "env": {
                "LDF_ROOT": str(project_root),
                "SPECS_DIR": str(project_root / ".ldf" / "specs"),
            },
        },
        "coverage-reporter": {
            "command": "python",
            "args": [str(mcp_servers_dir / "coverage-reporter" / "server.py")],
            "env": {
                "PROJECT_ROOT": str(project_root),
            },
        },
    }

    # Filter to requested servers
    if servers:
        config = {name: available_servers[name] for name in servers if name in available_servers}
    else:
        config = available_servers

    # Format output
    if output_format == "claude":
        output = {"mcpServers": config}
    else:
        output = config

    return json.dumps(output, indent=2)


def print_mcp_config(
    project_root: Path | None = None,
    servers: list[str] | None = None,
    output_format: str = "claude",
) -> None:
    """Print MCP configuration to stdout.

    Args:
        project_root: Project directory (defaults to cwd)
        servers: List of server names to include
        output_format: Output format - "claude" or "json"
    """
    config = generate_mcp_config(project_root, servers, output_format)
    print(config)
