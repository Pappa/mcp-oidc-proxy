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
- [Which Python stack should implement the demo OIDC provider?](issues/02-research-python-demo-oidc-server-options.md): NanoIDP thin uv app (YAML config + launcher); auth on port 9000, MCP on 8000; Authlib + Flask is runner-up
- [How should the two uv apps be laid out and run locally?](issues/03-grilling-repo-layout-and-dev-workflow.md): uv workspace (`apps/auth-server`, `apps/mcp-server`); `127.0.0.1:9000`/`8000`; root `.env.example`; committed nanoidp config; README + `uv run start`
- [How do we verify the OIDC proxy works end-to-end?](issues/04-grilling-verification-and-success-criteria.md): `tests/smoke/` with `@pytest.mark.smoke`; unit tests via `uv run pytest`, smoke via `uv run pytest -m smoke`; HeadlessOAuth E2E against subprocess servers
- [Bootstrap uv workspace and runnable demo OIDC auth server](issues/06-bootstrap-uv-workspace-and-auth-server.md): committed `./config/` for NanoIDP; `uv run python -m nanoidp` on `127.0.0.1:9000`; `.env.example`; pytest smoke marker exclusion

## Not yet specified

<!-- Map complete — ready for implementation handoff -->

## Out of scope

- Production deployment, hardening, or multi-instance scaling
- Integrating a real third-party IdP (Auth0, Google, Azure, etc.)
- Non-Python implementations
- Manual-only verification (automated smoke tests are in scope)
- MCP client implementation beyond what's needed to verify the flow
