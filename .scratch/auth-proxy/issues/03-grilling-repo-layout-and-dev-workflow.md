# How should the two uv apps be laid out and run locally?

Type: grilling

Blocked by: 02

## Question

Decide repo structure (uv workspace vs independent projects; directory naming), how developers start both servers, default ports/URLs, and how the MCP server discovers the auth server's OIDC configuration for local dev.

**Already decided** (see [Initial charting decisions](05-charting-initial-decisions.md)): uv workspace monorepo.

**Constraints from** [OIDC proxy IdP research](01-research-fastmcp-oidc-proxy-idp-requirements.md): MCP server `base_url` must align with pre-registered upstream redirect URI (`{base_url}/auth/callback`, default `http://localhost:8000/auth/callback`); auth server's `config_url` points at its own `/.well-known/openid-configuration` on a separate port.

Remaining: directory names, port assignment, env var layout, startup orchestration for smoke tests.
