Status: ready-for-agent

# auth-proxy prototype

Derived from [wayfinder map](map.md) and resolved decision tickets.

## Problem Statement

Developers building MCP servers that protect tools with OAuth need a local, reproducible way to validate that FastMCP's `OIDCProxy` correctly bridges a standard OIDC provider to MCP's authentication flow. Without a working reference setup, it is hard to tell whether auth failures come from the MCP server, the proxy configuration, or the upstream identity provider.

Today this repository has planning artifacts and quality-gate scaffolding but no runnable applications, no demo identity provider, and no automated proof that an MCP client can authenticate and call a protected tool end-to-end.

## Solution

Deliver a uv workspace monorepo containing two distinct Python applications:

1. **Auth server** — a thin NanoIDP-based demo OIDC provider with committed development configuration, pre-registered OAuth client credentials, and a demo user account. Its only purpose is to stand in for a real upstream IdP during local development and testing.

2. **MCP server** — a FastMCP HTTP server with a single protected `hello_world` tool, secured by `OIDCProxy` pointed at the auth server's OIDC discovery document.

Together with shared environment configuration, a workspace-level `uv run start` command, README guidance, and automated smoke tests, this gives developers a clone-and-run prototype that proves the OIDC proxy integration works.

## User Stories

1. As a developer cloning this repository, I want a uv workspace with two member applications, so that I can install all dependencies with a single `uv sync` at the root.

2. As a developer, I want an `.env.example` at the workspace root documenting shared configuration variables, so that I know which values the auth server and MCP server must agree on.

3. As a developer, I want the auth server to run NanoIDP with committed demo configuration, so that I can start the IdP without running an init or setup ritual.

4. As a developer, I want a demo user account in the auth server configuration, so that I can complete a login during OAuth flows in local testing.

5. As a developer, I want the auth server to expose standard OIDC discovery at a stable URL on port 9000, so that FastMCP `OIDCProxy` can fetch provider metadata.

6. As a developer, I want the auth server to issue RS256 JWT access tokens with a JWKS endpoint, so that the default FastMCP upstream token verifier can validate them.

7. As a developer, I want a pre-registered OAuth client in the auth server whose redirect URI matches the MCP server's callback URL, so that the upstream authorization-code flow succeeds without dynamic client registration on the IdP.

8. As a developer, I want all local URLs to use `127.0.0.1` consistently (not mixed with `localhost`), so that redirect URI and issuer validation do not fail due to hostname mismatch.

9. As a developer, I want the MCP server to run on HTTP port 8000, so that it aligns with the pre-registered redirect URI `http://127.0.0.1:8000/auth/callback`.

10. As a developer, I want the MCP server to use FastMCP `OIDCProxy` configured from environment variables, so that upstream `config_url`, client credentials, and `base_url` are not hard-coded.

11. As a developer, I want `OIDCProxy` to have authorization consent disabled for local development, so that headless automated tests can complete the OAuth flow without a browser consent screen.

12. As a developer, I want the MCP server to expose exactly one tool named `hello_world` that returns a fixed canned string, so that successful authentication is easy to verify.

13. As a developer, I want unauthenticated MCP tool calls to be rejected, so that I can confirm tools are actually protected.

14. As a developer, I want README instructions for starting each application individually, so that I can run and debug one server at a time.

15. As a developer, I want a workspace-level `uv run start` script entry that launches both servers together, so that I can bring up the full stack with one command during manual testing.

16. As a developer, I want smoke tests under a dedicated `tests/smoke/` package marked with `@pytest.mark.smoke`, so that slow end-to-end tests are separated from fast unit tests.

17. As a developer, I want `uv run pytest` to run unit tests only (excluding smoke), so that the default quality gate stays fast during iterative development.

18. As a developer, I want `uv run pytest -m smoke` to run end-to-end smoke tests, so that I can explicitly verify the full integration when needed.

19. As a developer, I want smoke tests to spawn the auth server and MCP server as real subprocesses, so that the test exercises the same process boundaries as manual usage.

20. As a developer, I want smoke tests to wait until both servers are healthy before asserting behavior, so that flaky startup timing does not cause false failures.

21. As a developer, I want smoke tests to use FastMCP's `Client` with `HeadlessOAuth` from the testing utilities, so that the full MCP OAuth flow is automated without a browser.

22. As a developer, I want smoke tests to complete synthetic MCP client registration, authorization, token exchange, and a protected `hello_world` tool call, so that the entire `OIDCProxy` path is covered.

23. As a developer, I want smoke tests to assert that an unauthenticated `hello_world` call fails with an auth error, so that negative cases are covered alongside the happy path.

24. As a maintainer, I want smoke tests runnable as a separate step in quality gates, so that CI can run fast unit tests on every change and smoke tests when appropriate.

25. As a developer evaluating FastMCP OIDC integration, I want the auth server to remain clearly demo-only and documented as such, so that I do not mistake it for a production identity provider.

26. As a developer, I want the MCP server to use HTTP transport (not stdio), so that OAuth callbacks and browser-based flows work as FastMCP's OIDC proxy expects.

27. As a developer, I want shared client ID and secret values to flow from environment configuration into both the NanoIDP client definition and the MCP server's `OIDCProxy` setup, so that credential drift between apps is impossible.

28. As a developer extending this prototype later, I want the workspace structure to keep auth and MCP concerns in separate member packages, so that either application can evolve independently.

## Implementation Decisions

### Workspace structure

- Convert the repository into a **uv workspace** with the root project holding shared development dependencies (pytest, pytest-asyncio, ruff, ty, etc.) and two workspace members: **auth-server** and **mcp-server** under an `apps/` directory.
- Register a **workspace script** `start` at the root so `uv run start` launches both servers (typically as subprocesses or concurrent processes managed by a small Python entrypoint).

### Auth server (NanoIDP thin app)

- Implement as a workspace member depending on the **nanoidp** package (user approval required before adding the dependency per repository agent instructions).
- Ship **committed demo configuration** including settings, users, and development cryptographic keys so `uv run` works out of the box. Document clearly that keys and passwords are for local demo only.
- Configure NanoIDP to listen on **`127.0.0.1:9000`** with issuer `http://127.0.0.1:9000`.
- Seed **one demo user** (e.g. admin credentials) for login during OAuth.
- Seed **one pre-registered OAuth client** matching the shared environment variables, with `client_secret_basic` authentication and redirect URI `http://127.0.0.1:8000/auth/callback`.
- Launcher invokes NanoIDP pointing at the committed config directory; no separate shell script wrapper.

### MCP server (FastMCP + OIDCProxy)

- Implement as a workspace member depending on **fastmcp** (user approval required before adding).
- Run with **HTTP transport** on `127.0.0.1:8000`.
- Configure **`OIDCProxy`** using environment variables:
  - `config_url` derived from `AUTH_SERVER_URL` + `/.well-known/openid-configuration`
  - `client_id` / `client_secret` from `DEMO_OIDC_CLIENT_ID` / `DEMO_OIDC_CLIENT_SECRET`
  - `base_url` from `MCP_SERVER_URL`
- Set **`require_authorization_consent=False`** on `OIDCProxy` for local development and headless testing.
- Expose a single protected tool **`hello_world`** returning a fixed canned string (exact string is an implementation detail but must be stable and asserted in smoke tests).

### Shared configuration

- Provide **`.env.example`** at the workspace root with:
  - `DEMO_OIDC_CLIENT_ID`
  - `DEMO_OIDC_CLIENT_SECRET`
  - `AUTH_SERVER_URL=http://127.0.0.1:9000`
  - `MCP_SERVER_URL=http://127.0.0.1:8000`
- Both applications read the same variable names; the auth server's NanoIDP config and the MCP server's `OIDCProxy` must stay in sync.

### OIDC / OAuth architecture (from research)

- The **upstream IdP** (NanoIDP) must provide OIDC discovery, authorization endpoint, token endpoint, and JWKS with RS256 JWTs. It does **not** need MCP-facing dynamic client registration, MCP discovery routes, or consent UI — FastMCP `OIDCProxy` synthesizes those for MCP clients.
- FastMCP issues its own HS256 reference JWTs to MCP clients while re-validating upstream tokens via JWKS on each protected request.
- Redirect URI on the upstream client must **exactly match** `{MCP_SERVER_URL}/auth/callback` (default path `/auth/callback`).

### Documentation

- Update the root **README** with: purpose of the prototype, prerequisite (uv), how to copy `.env.example`, how to run each server individually, how to run `uv run start`, and how to run unit vs smoke tests.

### Quality gates integration

- Configure pytest so default `addopts` **excludes** the `smoke` marker.
- Register the `smoke` marker in pytest configuration.
- Update agent-facing quality gate documentation to include `uv run pytest -m smoke` as a separate smoke step alongside the existing `uv run pytest` unit test step.

### Dependency policy

- All new runtime and dev dependencies must be added via **uv** only, with user approval before adding packages.

## Testing Decisions

### What makes a good test

- Test **external behavior** at system boundaries: HTTP responses, MCP protocol interactions, OAuth outcomes, and tool results.
- Do **not** test NanoIDP or FastMCP internal implementation details.
- Do **not** use in-process ASGI test clients for smoke tests — they bypass real subprocess and network boundaries that this prototype is meant to validate.

### Primary test seam (single highest boundary)

All meaningful verification flows through **one end-to-end seam**:

> Real subprocess auth server + real subprocess MCP server → FastMCP HTTP client with headless OAuth → MCP tool invocation.

This seam exercises: NanoIDP OIDC surface, `OIDCProxy` upstream bridging, MCP synthetic DCR, dual-layer PKCE, token issuance, JWT validation, and tool auth gating — without mocking any of those layers.

### Smoke tests (`tests/smoke/`)

- Mark all smoke tests with **`@pytest.mark.smoke`**.
- Use a **session-scoped fixture** that:
  1. Loads environment from `.env.example` values (or equivalent test env)
  2. Spawns NanoIDP and the MCP server as subprocesses
  3. Polls until OIDC discovery and the MCP HTTP endpoint respond (timeout ~30s)
  4. Tears down subprocesses after the session
- Use **FastMCP `Client`** with **`HeadlessOAuth`** from FastMCP testing utilities for the OAuth flow.
- If NanoIDP's login form blocks the default headless redirect handler, **extend `HeadlessOAuth.redirect_handler`** to POST demo credentials from committed config before following redirects.
- **Pass criteria:**
  1. Both servers become healthy within the startup timeout
  2. Authenticated `call_tool("hello_world")` returns the expected canned string
  3. Unauthenticated `call_tool("hello_world")` fails with 401 or an equivalent auth error

### Unit tests

- Default `uv run pytest` runs unit tests only (smoke excluded).
- Unit tests, if added, should cover small workspace utilities (e.g. environment loading, start-script process management) at a lower seam — not duplicate smoke coverage.
- No prior unit test examples exist in the repository; follow pytest conventions established in root `pyproject.toml`.

### CI / quality gates

- **Unit tests:** `uv run pytest` (existing quality gate).
- **Smoke tests:** `uv run pytest -m smoke` as a separate explicit step.
- Smoke tests may be slower; they should not block the fast unit-test loop unless the pipeline chooses to run both.

## Out of Scope

- Production deployment, hardening, HTTPS enforcement, key rotation, or multi-instance scaling
- Integrating real third-party IdPs (Auth0, Google, Azure, etc.)
- Non-Python implementations
- Manual-only verification (automated smoke tests are required)
- Building a custom OIDC authorization server (Authlib + Flask remains a documented runner-up, not in scope for this implementation)
- MCP client implementation beyond what smoke tests need
- SAML, device flow, or other NanoIDP features not required by `OIDCProxy`
- Additional MCP tools beyond `hello_world`
- Docker-based orchestration or shell script wrappers for dev startup

## Further Notes

- **Wayfinder artifacts:** Detailed research on upstream IdP requirements and Python OIDC server options lives under `.scratch/auth-proxy/research/` and informed this spec.
- **Python version:** Root `pyproject.toml` currently requires Python >=3.14; workspace members should align unless there is a compelling reason to differ.
- **Coverage:** Existing coverage configuration targets a `src` tree that does not yet exist; implementation should align coverage sources with the new workspace layout or adjust coverage config accordingly.
- **Headless OAuth risk:** The smoke test approach depends on FastMCP's `HeadlessOAuth` successfully navigating NanoIDP's login flow. If integration proves brittle, the fallback is a custom `redirect_handler` that submits demo credentials — not switching to browser automation unless headless approaches fail entirely.
