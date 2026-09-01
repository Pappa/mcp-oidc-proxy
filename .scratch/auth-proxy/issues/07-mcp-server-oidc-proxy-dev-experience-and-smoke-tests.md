# 07: MCP server with OIDCProxy, unified dev experience, and smoke tests

**What to build:** With the auth server from ticket 06 running, a developer can bring up the full prototype: an MCP server on `127.0.0.1:8000` (HTTP transport) protected by `OIDCProxy` (env-driven config, consent disabled) exposing a single `hello_world` tool that returns a stable canned string; unauthenticated tool calls are rejected. `uv run start` at the workspace root launches both servers together. README documents purpose, prerequisites, `.env.example`, per-app run commands, `uv run start`, unit vs smoke test commands, and that the auth server is demo-only. Automated smoke tests in `tests/smoke/` (marked `@pytest.mark.smoke`) spawn both servers as subprocesses, wait for health, use FastMCP `Client` with `HeadlessOAuth` to complete the full OAuth flow, assert authenticated `hello_world` succeeds and unauthenticated calls fail, and run via `uv run pytest -m smoke`. Quality gate documentation includes the smoke step alongside default `uv run pytest`.

**Blocked by:** [06: Bootstrap uv workspace and runnable demo OIDC auth server](06-bootstrap-uv-workspace-and-auth-server.md)

**Status:** ready-for-agent

- [ ] MCP server member runs on `127.0.0.1:8000` with HTTP transport and `OIDCProxy` configured from environment variables
- [ ] `hello_world` tool returns a fixed canned string when called with valid authentication
- [ ] Unauthenticated `hello_world` calls are rejected
- [ ] `uv run start` launches auth server and MCP server together
- [ ] README covers full local dev workflow (individual apps, `uv run start`, unit vs smoke tests, demo-only auth server warning)
- [ ] Smoke tests spawn both servers as subprocesses and poll until healthy (~30s timeout)
- [ ] Smoke tests exercise full MCP OAuth flow via `HeadlessOAuth` and assert happy path + unauthenticated rejection
- [ ] `uv run pytest -m smoke` runs smoke tests; quality gate docs updated for the separate smoke step
