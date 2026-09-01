# How do we verify the OIDC proxy works end-to-end?

Type: grilling

## Question

Define concrete success criteria and the verification workflow: which MCP client to use, the manual steps (or automated test) to complete OAuth and call a protected dummy tool, and what artifacts (README section, script, test) the prototype should include.

**Already decided** (see [Initial charting decisions](05-charting-initial-decisions.md)): automated smoke tests launching both servers locally; single `hello_world` tool as the protected endpoint to hit.

**Constraints from** [OIDC proxy IdP research](01-research-fastmcp-oidc-proxy-idp-requirements.md): smoke test must exercise full MCP OAuth flow through `OIDCProxy` (synthetic DCR → authorize → token → protected `hello_world` call); MCP server on HTTP transport; upstream redirect URI must match `{mcp_base_url}/auth/callback`.

**Constraints from** [Python OIDC server research](02-research-python-demo-oidc-server-options.md): smoke tests must launch both servers (NanoIDP auth app + FastMCP MCP server) as subprocesses.

Remaining: test harness choice, MCP client library, concrete pass/fail criteria.
