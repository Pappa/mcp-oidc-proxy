# What must the demo OIDC provider expose for FastMCP OIDCProxy?

Type: research

Status: resolved

## Question

What OIDC/OAuth2 endpoints, metadata, token characteristics, and client-registration assumptions does FastMCP's `OIDCProxy` require from an upstream provider? Document what a minimal demo auth server must implement (and what FastMCP handles itself) for local end-to-end testing.

## Answer

Full findings: [fastmcp-oidc-proxy-idp-requirements.md](../research/fastmcp-oidc-proxy-idp-requirements.md)

**Gist:** `OIDCProxy` targets upstream providers without DCR. The demo IdP must expose OIDC discovery (seven mandatory fields with default `strict=True`), authorization-code flow with PKCE S256, token endpoint (`authorization_code` + `refresh_token` recommended), and JWKS-backed RS256 JWT access tokens, with a pre-registered client whose redirect URI is `{mcp_base_url}/auth/callback` (default `http://localhost:8000/auth/callback`). FastMCP synthesizes MCP-facing OAuth (DCR, authorize/token, metadata, consent) and issues HS256 reference JWTs to MCP clients while re-validating upstream tokens on each request. The demo IdP does not need DCR, MCP discovery routes, or consent UI.
