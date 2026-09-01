# How should the two uv apps be laid out and run locally?

Type: grilling

Status: resolved

## Question

Decide repo structure (uv workspace vs independent projects; directory naming), how developers start both servers, default ports/URLs, and how the MCP server discovers the auth server's OIDC configuration for local dev.

**Already decided** (see [Initial charting decisions](05-charting-initial-decisions.md)): uv workspace monorepo.

**Constraints from** [OIDC proxy IdP research](01-research-fastmcp-oidc-proxy-idp-requirements.md): MCP server `base_url` must align with pre-registered upstream redirect URI (`{base_url}/auth/callback`, default `http://localhost:8000/auth/callback`); auth server's `config_url` points at its own `/.well-known/openid-configuration` on a separate port.

**Constraints from** [Python OIDC server research](02-research-python-demo-oidc-server-options.md): NanoIDP thin app (`apps/auth-server/` with YAML config); suggested ports auth `9000` / MCP `8000`; pre-registered OAuth client in nanoidp settings whose redirect URI matches MCP `base_url`.

## Answer

- **Workspace layout:** Root `pyproject.toml` as a uv workspace with members `apps/auth-server` and `apps/mcp-server`. Shared dev deps (e.g. pytest for smoke tests) live at the workspace root.
- **Hostnames:** `127.0.0.1` consistently — nanoidp issuer, OIDCProxy `base_url`, redirect URI, and smoke tests all use `127.0.0.1` (not mixed with `localhost`).
- **Ports:** Auth server `9000`, MCP server `8000`.
- **Environment variables:** Root `.env.example` (no committed secrets) with shared vars both apps read:

  ```
  DEMO_OIDC_CLIENT_ID=mcp-proxy-client
  DEMO_OIDC_CLIENT_SECRET=dev-secret
  AUTH_SERVER_URL=http://127.0.0.1:9000
  MCP_SERVER_URL=http://127.0.0.1:8000
  ```

  MCP app derives `OIDCProxy` `config_url` from `AUTH_SERVER_URL`; auth app nanoidp config seeds the matching client credentials and redirect URI (`{MCP_SERVER_URL}/auth/callback`).

- **NanoIDP config:** Commit `apps/auth-server/config/` (settings.yaml, users.yaml, dev keys) — demo-only, documented in README — so `uv run` works without a setup ritual.
- **Developer startup:** README documents the two per-app run commands. Root workspace exposes a `[project.scripts]` entry runnable as `uv run start` to launch both servers together. No `scripts/dev.sh`.
