"""Unit tests for MCP server configuration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from mcp_oidc_proxy.config import (
    DEFAULT_AUTH_SERVER_URL,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    DEFAULT_MCP_SERVER_URL,
    McpServerSettings,
    load_settings,
)
from mcp_oidc_proxy.constants import HELLO_WORLD_MESSAGE
from mcp_oidc_proxy.server import create_mcp_server


def test_load_settings_uses_documented_defaults(monkeypatch) -> None:
    monkeypatch.delenv("DEMO_OIDC_CLIENT_ID", raising=False)
    monkeypatch.delenv("DEMO_OIDC_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("AUTH_SERVER_URL", raising=False)
    monkeypatch.delenv("MCP_SERVER_URL", raising=False)
    monkeypatch.delenv("OIDC_AUDIENCE", raising=False)

    settings = load_settings()

    assert settings.client_id == DEFAULT_CLIENT_ID
    assert settings.client_secret == DEFAULT_CLIENT_SECRET
    assert settings.auth_server_url == DEFAULT_AUTH_SERVER_URL
    assert settings.mcp_server_url == DEFAULT_MCP_SERVER_URL
    assert (
        settings.oidc_config_url
        == "http://127.0.0.1:9000/.well-known/openid-configuration"
    )


@patch("mcp_oidc_proxy.server.OIDCProxy", return_value=MagicMock())
def test_create_mcp_server_builds_named_server(
    _mock_oidc_proxy: MagicMock,
) -> None:
    settings = McpServerSettings(
        client_id=DEFAULT_CLIENT_ID,
        client_secret=DEFAULT_CLIENT_SECRET,
        auth_server_url=DEFAULT_AUTH_SERVER_URL,
        mcp_server_url=DEFAULT_MCP_SERVER_URL,
        oidc_audience="mcp-oidc-proxy",
    )

    mcp = create_mcp_server(settings)

    assert mcp.name == "mcp-oidc-proxy"
    assert HELLO_WORLD_MESSAGE == "Hello from mcp-oidc-proxy!"
