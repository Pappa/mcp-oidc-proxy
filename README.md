# mcp-oidc-proxy

Local prototype for exercising [FastMCP `OIDCProxy`](https://gofastmcp.com/servers/auth/oidc-proxy) against a demo OIDC provider.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Python 3.14+

## Setup

```bash
uv sync
```

Demo client credentials are committed in `config/` with defaults matching `.env.example`. Copy `.env.example` to `.env` when you run the MCP server.

## Running locally

Run each server in its own terminal from the repository root:

```bash
uv run python -m nanoidp
```

```bash
uv run launch-mcp
```

The auth server listens on `http://127.0.0.1:9000` and exposes standard OIDC discovery, JWKS, authorize, and token endpoints. [NanoIDP](https://github.com/cdelmonte-zg/nanoidp) reads committed configuration from `./config`. It is for local development and testing only — not a production identity provider.

Demo credentials:

- User: `admin` / `admin`
- OAuth client: values from `.env.example` (`mcp-proxy-client` / `dev-secret`)

## Tests

```bash
uv run pytest          # unit/integration tests (smoke excluded)
uv run pytest -m smoke # end-to-end smoke tests (issue 07+)
```
