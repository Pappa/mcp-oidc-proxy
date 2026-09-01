# 06: Bootstrap uv workspace and runnable demo OIDC auth server

**What to build:** A developer can clone the repository, run `uv sync` at the workspace root, and start the auth-server member to get a working demo OIDC provider on `127.0.0.1:9000` — no init ritual required. NanoIDP runs with committed demo configuration: a demo user, a pre-registered OAuth client (credentials and redirect URI aligned with the future MCP server at `http://127.0.0.1:8000/auth/callback`), RS256 JWTs, and standard OIDC discovery/JWKS/authorize/token endpoints. Root `.env.example` documents the shared environment variables. Pytest is configured with a registered `smoke` marker and default runs exclude smoke; coverage configuration is aligned with the new workspace layout so `uv run pytest` succeeds (even if no tests exist yet).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `uv sync` at workspace root installs auth-server and shared dev dependencies
- [ ] Auth server starts on `127.0.0.1:9000` and serves a valid OIDC discovery document
- [ ] JWKS endpoint returns RS256 keys; authorize and token endpoints are reachable
- [ ] Pre-registered OAuth client matches `.env.example` values and MCP redirect URI `http://127.0.0.1:8000/auth/callback`
- [ ] Demo user exists for login during OAuth flows
- [ ] `.env.example` at workspace root documents `DEMO_OIDC_CLIENT_ID`, `DEMO_OIDC_CLIENT_SECRET`, `AUTH_SERVER_URL`, `MCP_SERVER_URL`
- [ ] Default `uv run pytest` excludes smoke-marked tests; `smoke` marker is registered in pytest config
