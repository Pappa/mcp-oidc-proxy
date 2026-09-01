"""Entry point for the FastMCP HTTP server."""

from __future__ import annotations

from urllib.parse import urlparse

from mcp_oidc_proxy.config import load_settings
from mcp_oidc_proxy.server import create_mcp_server


def _host_and_port(mcp_server_url: str) -> tuple[str, int]:
    parsed = urlparse(mcp_server_url)
    if not parsed.hostname or parsed.port is None:
        msg = f"MCP_SERVER_URL must include an explicit port: {mcp_server_url!r}"
        raise ValueError(msg)
    return parsed.hostname, parsed.port


def main() -> None:
    """Run the MCP server over HTTP transport."""
    settings = load_settings()
    mcp = create_mcp_server(settings)
    host, port = _host_and_port(settings.mcp_server_url)
    mcp.run(transport="http", host=host, port=port)
