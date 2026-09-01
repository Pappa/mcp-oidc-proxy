"""Environment-driven configuration for the MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urljoin

from dotenv import load_dotenv

DEFAULT_CLIENT_ID = "mcp-proxy-client"
DEFAULT_CLIENT_SECRET = "dev-secret"
DEFAULT_AUTH_SERVER_URL = "http://127.0.0.1:9000"
DEFAULT_MCP_SERVER_URL = "http://127.0.0.1:8000"
DEFAULT_OIDC_AUDIENCE = "mcp-oidc-proxy"


@dataclass(frozen=True, slots=True)
class McpServerSettings:
    """Runtime settings shared with the demo OIDC provider."""

    client_id: str
    client_secret: str
    auth_server_url: str
    mcp_server_url: str
    oidc_audience: str

    @property
    def oidc_config_url(self) -> str:
        return urljoin(
            f"{self.auth_server_url.rstrip('/')}/",
            ".well-known/openid-configuration",
        )


def load_settings() -> McpServerSettings:
    """Load settings from the process environment and optional `.env` file."""
    load_dotenv()
    return McpServerSettings(
        client_id=os.getenv("DEMO_OIDC_CLIENT_ID", DEFAULT_CLIENT_ID),
        client_secret=os.getenv("DEMO_OIDC_CLIENT_SECRET", DEFAULT_CLIENT_SECRET),
        auth_server_url=os.getenv("AUTH_SERVER_URL", DEFAULT_AUTH_SERVER_URL),
        mcp_server_url=os.getenv("MCP_SERVER_URL", DEFAULT_MCP_SERVER_URL),
        oidc_audience=os.getenv("OIDC_AUDIENCE", DEFAULT_OIDC_AUDIENCE),
    )
