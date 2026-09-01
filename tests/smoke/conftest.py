"""Shared fixtures for end-to-end smoke tests."""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AUTH_SERVER_URL = "http://127.0.0.1:9000"
MCP_SERVER_URL = "http://127.0.0.1:8000"
MCP_ENDPOINT_URL = f"{MCP_SERVER_URL}/mcp"
DISCOVERY_URL = f"{AUTH_SERVER_URL}/.well-known/openid-configuration"
MCP_AUTH_METADATA_URL = f"{MCP_SERVER_URL}/.well-known/oauth-authorization-server"
STARTUP_TIMEOUT_SECONDS = 30


def _load_env_example() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (REPO_ROOT / ".env.example").read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        env[key] = value
    return env


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


@pytest.fixture(scope="session")
def running_servers() -> Iterator[dict[str, str]]:
    """Spawn NanoIDP and the MCP server for the full OAuth integration seam."""
    env = os.environ.copy()
    env.update(_load_env_example())

    auth_process = subprocess.Popen(
        ["uv", "run", "python", "-m", "nanoidp"],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    mcp_process = subprocess.Popen(
        ["uv", "run", "launch-mcp"],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        _wait_until_healthy(DISCOVERY_URL, STARTUP_TIMEOUT_SECONDS)
        _wait_until_healthy(MCP_AUTH_METADATA_URL, STARTUP_TIMEOUT_SECONDS)
        yield {
            "auth_server_url": AUTH_SERVER_URL,
            "mcp_server_url": MCP_SERVER_URL,
            "mcp_endpoint_url": MCP_ENDPOINT_URL,
        }
    finally:
        for process in (mcp_process, auth_process):
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.fixture(scope="session")
def auth_server_discovery(running_servers: dict[str, str]) -> dict[str, object]:
    with urlopen(DISCOVERY_URL) as response:
        return json.load(response)
