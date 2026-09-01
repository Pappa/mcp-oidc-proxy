"""End-to-end smoke tests for the OIDC proxy integration."""

from __future__ import annotations

import pytest
from fastmcp import Client

from mcp_oidc_proxy.constants import HELLO_WORLD_MESSAGE
from smoke.nanoidp_oauth import NanoIDPHeadlessOAuth

pytestmark = pytest.mark.smoke


@pytest.mark.asyncio
async def test_authenticated_hello_world_returns_canned_string(
    running_servers: dict[str, str],
) -> None:
    mcp_url = running_servers["mcp_endpoint_url"]
    auth = NanoIDPHeadlessOAuth(mcp_url)

    async with Client(mcp_url, auth=auth) as client:
        result = await client.call_tool("hello_world")

    assert result.data == HELLO_WORLD_MESSAGE


@pytest.mark.asyncio
async def test_unauthenticated_hello_world_is_rejected(
    running_servers: dict[str, str],
) -> None:
    mcp_url = running_servers["mcp_endpoint_url"]

    with pytest.raises(Exception) as exc_info:
        async with Client(mcp_url) as client:
            await client.call_tool("hello_world")

    message = str(exc_info.value).lower()
    assert any(token in message for token in ("401", "unauthorized", "auth", "error"))
