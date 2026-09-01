# How do we verify the OIDC proxy works end-to-end?

Type: grilling

Status: resolved

## Question

Define concrete success criteria and the verification workflow: which MCP client to use, the manual steps (or automated test) to complete OAuth and call a protected dummy tool, and what artifacts (README section, script, test) the prototype should include.

**Already decided** (see [Initial charting decisions](05-charting-initial-decisions.md)): automated smoke tests launching both servers locally; single `hello_world` tool as the protected endpoint to hit.

**Constraints from** [OIDC proxy IdP research](01-research-fastmcp-oidc-proxy-idp-requirements.md): smoke test must exercise full MCP OAuth flow through `OIDCProxy` (synthetic DCR → authorize → token → protected `hello_world` call); MCP server on HTTP transport; upstream redirect URI must match `{mcp_base_url}/auth/callback`.

**Constraints from** [Python OIDC server research](02-research-python-demo-oidc-server-options.md): smoke tests must launch both servers (NanoIDP auth app + FastMCP MCP server) as subprocesses.

**Constraints from** [repo layout decision](03-grilling-repo-layout-and-dev-workflow.md): use root `.env.example` vars; servers at `127.0.0.1:9000` and `127.0.0.1:8000`; smoke tests may reuse the same env layout as `uv run start`.

## Answer

- **Harness:** `pytest` + `pytest-asyncio` at workspace root; run unit tests via `uv run pytest`, smoke tests via `uv run pytest -m smoke`.
- **Test location:** `tests/smoke/` for E2E smoke tests; unit tests elsewhere under `tests/` (excluded from default smoke marker).
- **Marker:** `@pytest.mark.smoke` on smoke tests; default `uv run pytest` excludes smoke (configure in `pyproject.toml` with `addopts = "-m 'not smoke'"` or equivalent).
- **Server lifecycle:** Session-scoped fixture spawns nanoidp + MCP server as subprocesses using `.env.example` vars; polls until OIDC discovery and MCP endpoint respond; tears down after session.
- **MCP client / OAuth:** FastMCP `Client` with `HeadlessOAuth` from `fastmcp.utilities.tests` (no browser). MCP app sets `require_authorization_consent=False` on `OIDCProxy`. If nanoidp login form blocks headless flow, extend `redirect_handler` to POST demo credentials from committed config.
- **Pass/fail criteria:**
  1. Both servers healthy within timeout (e.g. 30s)
  2. Authenticated `call_tool("hello_world")` returns expected canned string
  3. Unauthenticated `call_tool("hello_world")` fails (401 or auth error)
- **CI:** Smoke tests run explicitly with `-m smoke` in quality gates (separate step from default unit test run).
