# mcp-oidc-proxy

Local prototype for exercising [FastMCP `OIDCProxy`](https://gofastmcp.com/servers/auth/oidc-proxy) against a demo OIDC provider.

The repository packages two cooperating apps:

- **Auth server** — a [NanoIDP](https://github.com/cdelmonte-zg/nanoidp) demo OIDC provider on `http://127.0.0.1:9000`
- **MCP server** — a FastMCP HTTP server on `http://127.0.0.1:8000` with a single protected `hello_world` tool

Together they prove that an MCP client can authenticate through `OIDCProxy`, call a protected tool, and be rejected when unauthenticated.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Python 3.14+

## Setup

```bash
uv sync
cp .env.example .env
```

Demo client credentials are committed in `config/` with defaults matching `.env.example`. Both servers read the same environment variable names so credentials stay aligned.

## Running locally

Run each server in its own terminal from the repository root:

```bash
uv run python -m nanoidp
```

```bash
uv run launch-mcp
```

The auth server listens on `http://127.0.0.1:9000` and exposes standard OIDC discovery, JWKS, authorize, and token endpoints. NanoIDP reads committed configuration from `./config`.

**Demo-only warning:** the auth server exists solely to validate the OIDC proxy flow during local development and testing. It is not a production identity provider.

Demo credentials:

- User: `admin` / `admin`
- OAuth client: values from `.env.example` (`mcp-proxy-client` / `dev-secret`)

## Tests

```bash
uv run pytest          # unit/integration tests (smoke excluded)
uv run pytest -m smoke # end-to-end smoke tests (spawns both servers)
```

Smoke tests launch real subprocesses for NanoIDP and the MCP server, complete the OAuth flow with FastMCP `HeadlessOAuth`, and verify both authenticated and unauthenticated tool calls.
