# How should the two uv apps be laid out and run locally?

Type: grilling

## Question

Decide repo structure (uv workspace vs independent projects; directory naming), how developers start both servers, default ports/URLs, and how the MCP server discovers the auth server's OIDC configuration for local dev.

**Already decided** (see [Initial charting decisions](05-charting-initial-decisions.md)): uv workspace monorepo.

**Constraints from** [OIDC proxy IdP research](01-research-fastmcp-oidc-proxy-idp-requirements.md): MCP server `base_url` must align with pre-registered upstream redirect URI (`{base_url}/auth/callback`, default `http://localhost:8000/auth/callback`); auth server's `config_url` points at its own `/.well-known/openid-configuration` on a separate port.

**Constraints from** [Python OIDC server research](02-research-python-demo-oidc-server-options.md): NanoIDP thin app (`apps/auth-server/` with YAML config); suggested ports auth `9000` / MCP `8000`; pre-registered OAuth client in nanoidp settings whose redirect URI matches MCP `base_url`.

Remaining: directory names, env var layout, startup orchestration for smoke tests.
