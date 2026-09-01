"""Integration tests for the demo OIDC auth server."""

from __future__ import annotations

import json
import subprocess
import time
from collections.abc import Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest

AUTH_SERVER_URL = "http://127.0.0.1:9000"
DISCOVERY_URL = f"{AUTH_SERVER_URL}/.well-known/openid-configuration"
JWKS_URL = f"{AUTH_SERVER_URL}/.well-known/jwks.json"
AUTHORIZE_URL = f"{AUTH_SERVER_URL}/authorize"
TOKEN_URL = f"{AUTH_SERVER_URL}/token"
EXPECTED_CLIENT_ID = "mcp-proxy-client"
EXPECTED_REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"
STARTUP_TIMEOUT_SECONDS = 30

pytestmark = pytest.mark.integration


def _wait_until_healthy(url: str, timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
        time.sleep(0.2)
    raise TimeoutError(f"Server did not become healthy at {url}: {last_error}")


@pytest.fixture(scope="module")
def auth_server() -> Iterator[str]:
    process = subprocess.Popen(
        ["uv", "run", "python", "-m", "nanoidp"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        _wait_until_healthy(DISCOVERY_URL, STARTUP_TIMEOUT_SECONDS)
        yield AUTH_SERVER_URL
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_oidc_discovery_document(auth_server: str) -> None:
    with urlopen(DISCOVERY_URL) as response:
        document = json.load(response)

    assert document["issuer"] == "http://127.0.0.1:9000"
    assert document["authorization_endpoint"] == AUTHORIZE_URL
    assert document["token_endpoint"] == TOKEN_URL
    assert document["jwks_uri"] == JWKS_URL


def test_jwks_returns_rs256_key(auth_server: str) -> None:
    with urlopen(JWKS_URL) as response:
        document = json.load(response)

    keys = document["keys"]
    assert keys
    assert keys[0]["kty"] == "RSA"
    assert keys[0]["alg"] == "RS256"


def test_authorize_endpoint_is_reachable(auth_server: str) -> None:
    authorize_request = (
        f"{AUTHORIZE_URL}?response_type=code"
        f"&client_id={EXPECTED_CLIENT_ID}"
        f"&redirect_uri={EXPECTED_REDIRECT_URI}"
        "&scope=openid"
        "&state=test-state"
    )
    request = Request(authorize_request, method="GET")
    try:
        urlopen(request)
    except HTTPError as exc:
        # Login page or OAuth error redirect is enough to prove the route exists.
        assert exc.code in {200, 302, 400}


def test_token_endpoint_is_reachable(auth_server: str) -> None:
    request = Request(
        TOKEN_URL,
        data=b"grant_type=client_credentials",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        urlopen(request)
    except HTTPError as exc:
        assert exc.code in {400, 401}
