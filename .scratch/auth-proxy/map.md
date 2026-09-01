# auth-proxy

Type: wayfinder:map

## Destination

A runnable prototype in this repo: two distinct Python applications packaged with uv — a minimal demo OIDC provider and a FastMCP HTTP MCP server with dummy tools — wired together via FastMCP's `OIDCProxy` so an MCP client can authenticate through the demo provider and invoke protected tools.

## Notes

- Domain: MCP authentication prototype; FastMCP OIDC proxy integration
- Skills to consult: `research`, `prototype`, `grilling`, `domain-modeling`
- Both apps are Python; use uv for packaging
- The auth server is demo-only — its sole purpose is to validate the OIDC proxy flow
- Primary reference: [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy)

## Decisions so far

- [Initial charting decisions](issues/05-charting-initial-decisions.md): uv workspace monorepo; automated local smoke tests launching both servers; single `hello_world` MCP tool
- [What must the demo OIDC provider expose for FastMCP OIDCProxy?](issues/01-research-fastmcp-oidc-proxy-idp-requirements.md): minimal IdP needs discovery + authorize + token + JWKS (RS256); pre-registered client with redirect `{mcp_base_url}/auth/callback`; no DCR — FastMCP handles MCP-facing OAuth

## Not yet specified

- Which Python stack implements the demo OIDC provider (ticket 02)
- Exact workspace directory names and root `pyproject.toml` layout
- Auth server port vs MCP server port (MCP default redirect assumes `http://localhost:8000/auth/callback`)
- Environment variable / secrets layout shared between apps (client_id, client_secret, issuer URLs)
- Smoke-test harness details (pytest? subprocess? which MCP client library?)

## Out of scope

- Production deployment, hardening, or multi-instance scaling
- Integrating a real third-party IdP (Auth0, Google, Azure, etc.)
- Non-Python implementations
- Manual-only verification (automated smoke tests are in scope)
- MCP client implementation beyond what's needed to verify the flow
