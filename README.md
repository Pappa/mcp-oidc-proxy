# mcp-oidc-proxy

Local prototype for exercising [FastMCP `OIDCProxy`](https://gofastmcp.com/servers/auth/oidc-proxy) against a demo OIDC provider.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Python 3.14+

## Setup

```bash
uv sync
```

No `.env` file is required for the auth server — demo client credentials are committed in NanoIDP config with defaults matching `.env.example`. Copy `.env.example` to `.env` when you add the MCP server (issue 07).

## Auth server (demo OIDC provider)

The auth server is a thin launcher around [NanoIDP](https://github.com/cdelmonte-zg/nanoidp) with committed demo configuration. It is for local development and testing only — not a production identity provider.

```bash
uv run --package auth-server auth-server
```

The server listens on `http://127.0.0.1:9000` and exposes standard OIDC discovery, JWKS, authorize, and token endpoints.

Demo credentials:

- User: `admin` / `admin`
- OAuth client: values from `.env.example` (`mcp-proxy-client` / `dev-secret`)

## Tests

```bash
uv run pytest          # unit/integration tests (smoke excluded)
uv run pytest -m smoke # end-to-end smoke tests (issue 07+)
```
