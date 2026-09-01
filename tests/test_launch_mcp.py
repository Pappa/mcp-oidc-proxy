"""Unit tests for the MCP server launcher."""

from __future__ import annotations

import pytest

from mcp_oidc_proxy.launch_mcp import _host_and_port


def test_host_and_port_parses_mcp_server_url() -> None:
    assert _host_and_port("http://127.0.0.1:8000") == ("127.0.0.1", 8000)


def test_host_and_port_requires_explicit_port() -> None:
    with pytest.raises(ValueError, match="explicit port"):
        _host_and_port("http://127.0.0.1")
