"""FastMCP server protected by OIDCProxy."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from key_value.aio.stores.memory import MemoryStore

from mcp_oidc_proxy.config import McpServerSettings, load_settings
from mcp_oidc_proxy.constants import HELLO_WORLD_MESSAGE


def create_oidc_proxy(settings: McpServerSettings) -> OIDCProxy:
    """Build OIDCProxy from shared environment settings."""
    return OIDCProxy(
        config_url=settings.oidc_config_url,
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        base_url=settings.mcp_server_url,
        audience=settings.oidc_audience,
        required_scopes=["openid"],
        require_authorization_consent=False,
        client_storage=MemoryStore(),
        # NanoIDP omits subject_types_supported in discovery metadata.
        strict=False,
    )


def create_mcp_server(settings: McpServerSettings | None = None) -> FastMCP:
    """Create the protected MCP server with a single hello_world tool."""
    resolved_settings = settings or load_settings()
    mcp = FastMCP("mcp-oidc-proxy", auth=create_oidc_proxy(resolved_settings))

    @mcp.tool
    def hello_world() -> str:
        """Return a stable greeting for smoke and manual verification."""
        return HELLO_WORLD_MESSAGE

    return mcp
