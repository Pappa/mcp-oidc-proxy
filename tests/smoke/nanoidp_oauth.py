"""Headless OAuth helper for NanoIDP login during smoke tests."""

from __future__ import annotations

import httpx2
from fastmcp.utilities.tests import HeadlessOAuth

DEMO_USERNAME = "admin"
DEMO_PASSWORD = "admin"
_REDIRECT_STATUSES = {301, 302, 303, 307, 308}


def _is_proxy_callback(location: str) -> bool:
    return "127.0.0.1:8000/auth/callback" in location


def _is_client_callback(location: str) -> bool:
    return "/callback" in location and not _is_proxy_callback(location)


class NanoIDPHeadlessOAuth(HeadlessOAuth):
    """Submit NanoIDP's login form when the authorize step returns HTML."""

    async def redirect_handler(self, authorization_url: str) -> None:
        async with httpx2.AsyncClient() as client:
            response = await client.get(authorization_url, follow_redirects=False)

            while True:
                if response.status_code in _REDIRECT_STATUSES:
                    location = response.headers.get("location")
                    if location is None:
                        break
                    if _is_client_callback(location):
                        break
                    if _is_proxy_callback(location):
                        response = await client.get(location, follow_redirects=False)
                        break
                    response = await client.get(location, follow_redirects=False)
                    continue

                if response.status_code == 200 and 'name="username"' in response.text:
                    response = await client.post(
                        str(response.url),
                        data={"username": DEMO_USERNAME, "password": DEMO_PASSWORD},
                        follow_redirects=False,
                    )
                    continue

                break

            self._stored_response = response
