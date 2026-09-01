# Python demo OIDC server options

Research ticket: [02-research-python-demo-oidc-server-options](../issues/02-research-python-demo-oidc-server-options.md)

**Question:** Which Python stack should implement the local-only demo OIDC provider that pairs with FastMCP `OIDCProxy` in this prototype?

**Date:** 2026-09-01

---

## Context

The auth-proxy prototype needs **two distinct Python apps** in one repo (uv-managed):

1. A **demo OIDC provider** — exists only to exercise the auth flow.
2. A **FastMCP HTTP MCP server** — protected by `OIDCProxy`, with dummy tools.

FastMCP docs: [OIDC Proxy](https://gofastmcp.com/servers/auth/oidc-proxy)

---

## What FastMCP `OIDCProxy` needs from the upstream provider

`OIDCProxy` bridges a standard OIDC provider to MCP's OAuth flow. FastMCP handles DCR for MCP clients, consent, token re-issuance, and storage; the **upstream demo IdP** must supply a normal OIDC authorization server surface.

### Required upstream capabilities

| Capability | Why | Source |
|---|---|---|
| OIDC discovery document at a stable URL | `OIDCProxy(config_url=...)` fetches provider metadata | [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy) |
| `authorization_endpoint` | Browser login / consent redirect | [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy) |
| `token_endpoint` | Code → token exchange by the proxy | [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy) |
| `jwks_uri` (for default JWT verification) | `JWTVerifier` validates upstream tokens via JWKS | [FastMCP JWTVerifier docs](https://github.com/prefecthq/fastmcp/blob/main/fastmcp_slim/fastmcp/server/auth/providers/jwt.py) |
| Pre-registered OAuth client (`client_id`, `client_secret`) | Providers without DCR (the proxy's target class) | [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy) |
| Redirect URI = `{mcp_base_url}{redirect_path}` (default `/auth/callback`) | Must match provider app registration | [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy) |
| Authorization code grant | Standard MCP browser flow | [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy) |
| `client_secret_basic` or `client_secret_post` at token endpoint | Proxy authenticates to upstream; default is `client_secret_basic` | [FastMCP OIDC Proxy docs](https://gofastmcp.com/servers/auth/oidc-proxy) |
| JWT signed with a verifiable key (typically **RS256**) | Default verifier uses asymmetric JWKS | [Authlib OIDC docs](https://docs.authlib.org/en/stable/oauth2/authorization-server/flask/openid-connect.html); [FastMCP JWTVerifier](https://github.com/prefecthq/fastmcp/blob/main/fastmcp_slim/fastmcp/server/auth/providers/jwt.py) |
| `openid` scope (if using `verify_id_token=True`) | Returns `id_token` for local JWT verification when access tokens are opaque | [FastMCP PR #3248](https://github.com/PrefectHQ/fastmcp/pull/3248) |

### Not required for this prototype

- Dynamic Client Registration on the **upstream** provider (FastMCP does DCR for MCP clients).
- Production hardening (HTTPS enforcement, key rotation, rate limits).
- Refresh-token longevity tuning (nice-to-have, not blocking).
- User management beyond a single demo account.

### Local-dev caveat: HTTP vs HTTPS

Authlib's metadata validators expect `https` URLs in strict mode ([Authlib RFC 8414 models](https://github.com/authlib/authlib/blob/main/oauth2/rfc8414/models.py)). For localhost, Authlib's official examples set `AUTHLIB_INSECURE_TRANSPORT=1` ([example-oauth2-server README](https://github.com/authlib/example-oauth2-server/blob/master/README.md)). Django OAuth Toolkit similarly serves `http://localhost` discovery in dev ([DOT OIDC docs](https://django-oauth-toolkit.readthedocs.io/en/latest/oidc.html)).

---

## Options surveyed

### 1. Authlib + Flask (official examples)

**What it is:** Authlib is a full OAuth 2.0 / OIDC / JOSE library with first-party **authorization server** integrations for Flask and Django — not just client support ([Authlib](https://authlib.org/), [Authlib authorization server docs](https://docs.authlib.org/en/stable/oauth2/authorization-server/)).

**Starting points:**

| Repo | Scope | Notes |
|---|---|---|
| [authlib/example-oauth2-server](https://github.com/authlib/example-oauth2-server) | OAuth 2.0 AS | ~700 stars; SQLite + SQLAlchemy; client registration UI; `uv sync` ready |
| [authlib/example-oidc-server](https://github.com/authlib/example-oidc-server) | OIDC 1.0 AS | Adds `OpenIDCode` grant; issues `id_token`; **does not ship discovery/JWKS routes** |

The OIDC example signs tokens with HS256 and a dummy symmetric key ([example `oauth2.py`](https://github.com/authlib/example-oidc-server/blob/master/website/oauth2.py)). For FastMCP's default `JWTVerifier`, the prototype should switch to **RS256** and add:

- `GET /.well-known/openid-configuration`
- `GET /oauth/jwks` (or similar) returning the public JWK set

Authlib documents the OIDC code-flow extension pattern ([Flask OIDC Provider](https://docs.authlib.org/en/stable/oauth2/authorization-server/flask/openid-connect.html)). Discovery metadata shape is documented separately ([OIDC Discovery](https://docs.authlib.org/en/v1.6.8/oauth/oidc/discovery.html)). Community examples wire the `.well-known` route manually ([Stack Overflow discussion](https://stackoverflow.com/questions/61022475/any-examples-of-setting-up-well-known-url-using-authlib)).

**Complexity:** Low–medium. Fork the OIDC example, add ~30 lines for discovery/JWKS, swap HS256 → RS256, seed one client for the MCP server.

**Maintenance:** Authlib is actively maintained (used by FastMCP itself via joserfc for JWT work per [Authlib site](https://authlib.org/)). Flask example repos are reference-quality but not versioned as libraries — pin Authlib in `pyproject.toml`.

**Fit:** **Excellent.** Python-native, uv-friendly, minimal dependencies, matches "demo-only AS" scope. Sync Flask is fine for a local IdP that only serves browser login + token endpoints.

---

### 2. Authlib + Django

**What it is:** Same Authlib AS primitives with Django integration and OIDC provider docs ([Django OIDC Provider](https://docs.authlib.org/en/stable/oauth2/authorization-server/django/openid-connect.html)).

**Complexity:** Medium–high. Requires Django project scaffolding, settings, migrations, and route wiring comparable to option 1 but with more framework ceremony.

**Maintenance:** Same Authlib core; more moving parts (Django version, ORM models).

**Fit:** Good if the team already standardizes on Django; otherwise heavier than needed for a throwaway demo IdP.

---

### 3. django-oauth-toolkit (DOT)

**What it is:** Mature Django app that exposes OAuth 2.0 + OIDC provider endpoints out of the box ([DOT getting started](https://django-oauth-toolkit.readthedocs.io/en/latest/getting_started.html), [DOT OIDC](https://django-oauth-toolkit.readthedocs.io/en/latest/oidc.html)).

**Highlights:**

- Enable OIDC with `OIDC_ENABLED: True` and an RSA private key.
- Discovery at `/o/.well-known/openid-configuration/` (verified in community walkthroughs, e.g. [Mike Robinson's article](https://heymike.dev/articles/using-django-as-openid-connect-provider)).
- Register the FastMCP app as a Django `Application` (authorization code grant, RS256).
- Built-in admin UI for clients and scopes.

**Complexity:** Medium upfront (full Django stack, migrations, `manage.py` workflow), **low ongoing** for OIDC correctness — discovery, JWKS, and token formats are handled.

**Maintenance:** Well-established project built on OAuthLib ([OAuthLib README](https://github.com/oauthlib/oauthlib)); Django LTS coupling is the main long-term cost.

**Fit:** Strong if "batteries included OIDC" outweighs framework weight. Poor fit for a repo that wants two **lightweight** sibling uv apps.

---

### 4. OAuthLib (raw)

**What it is:** Low-level, framework-agnostic OAuth 1/2 logic ([OAuthLib README](https://github.com/oauthlib/oauthlib)). Provider support exists but **you implement every HTTP endpoint, persistence layer, and OIDC JWT detail yourself**.

**Complexity:** High. OAuthLib is the engine inside DOT and other integrations — using it directly means re-building what Authlib or DOT already provide.

**Maintenance:** Stable core, but **you** own all AS code.

**Fit:** **Poor** for this prototype. Appropriate only if avoiding Authlib/Django dependencies is a hard requirement.

---

### 5. Authlib + Starlette / FastAPI (manual AS)

**What it is:** Authlib has excellent **client** integrations for Starlette/FastAPI ([Starlette client docs](https://docs.authlib.org/en/stable/oauth2/client/web/starlette.html)) but **no first-party authorization server integration** for ASGI frameworks ([Authlib AS index](https://docs.authlib.org/en/stable/oauth2/authorization-server/)).

**Complexity:** High. Would require porting Flask AS patterns to ASGI request/response objects or using Authlib's framework-agnostic server core directly.

**Fit:** **Poor** unless the demo IdP must share FastAPI/Starlette with the MCP server (it should not — two distinct apps).

---

### 6. Keycloak in Docker (not Python-native)

**What it is:** Full-featured Java OIDC/OAuth IdP; `start-dev` mode for local use ([Keycloak container docs](https://www.keycloak.org/server/containers); community guides such as [karuppiah.dev](https://karuppiah.dev/trying-to-authenticate-in-a-demo-application-using-openid-connect-oidc-using-keycloak)).

**Complexity:** Low to **run** (one `docker run`), high **operational** surface (admin console, realm/client export, JVM memory, port 8080).

**Maintenance:** External lifecycle — image updates, realm JSON in repo, not uv Python deps.

**Fit:** **Good reference / fallback** when you want a "real" IdP without writing code. **Poor default** for this repo's goal of a Python demo app alongside FastMCP. Could be orchestrated from a `scripts/` helper but is not "written in Python."

---

### 7. Other lightweight mock IdPs (not Python-native)

| Tool | Runtime | Pros | Cons | Source |
|---|---|---|---|---|
| [Dex](https://dexidp.io/) | Go binary | Lighter than Keycloak; mock connector for dev | Not Python; YAML config; still a separate process | [dexidp.io](https://dexidp.io/) |
| [mocc](https://github.com/jonasbg/mocc) | Go | Tiny; accepts any client creds; RS256 id_tokens | Not Python; intentionally non-spec-strict | [GitHub](https://github.com/jonasbg/mocc) |
| [dev-oidc](https://github.com/camcima/dev-oidc) | Node | Config-driven; discovery + JWKS; docker-compose friendly | Not Python; Node runtime | [GitHub](https://github.com/camcima/dev-oidc) |
| [stubidp](https://github.com/cerberauth/stubidp) | Node/npx | Fastest zero-code local OIDC | Not Python; npx/Node dependency | [GitHub](https://github.com/cerberauth/stubidp) |

**Fit:** Best when the goal is **only** to test FastMCP, not to demonstrate a Python IdP. Useful as a **CI smoke-test fallback** or to unblock MCP-side work before the Python AS exists.

---

## Comparison table

| Option | Python / uv native | Initial effort | Ongoing maintenance | OIDC discovery + JWKS | Pre-registered client | FastMCP fit | Demo UX (login UI) |
|---|---|---|---|---|---|---|---|
| **Authlib + Flask (recommended)** | Yes | Low–medium | Low (pin deps) | Add routes (~30 LOC); RS256 | Web UI or seed script | **Best** | Built-in in examples |
| Authlib + Django | Yes | Medium–high | Medium | Manual (same as Flask) | Custom | Good | Build yourself |
| django-oauth-toolkit | Yes | Medium | Medium (Django) | **Built-in** | Django admin | Good | Django admin |
| OAuthLib raw | Yes | **High** | **High (you own it)** | Build yourself | Build yourself | Possible | Build yourself |
| Authlib + Starlette/FastAPI AS | Yes | **High** | High | Build yourself | Build yourself | Possible | Build yourself |
| Keycloak Docker | No | Low (run) | Medium (ops) | **Built-in** | Admin console | Good | Keycloak UI |
| Mock IdPs (mocc, dev-oidc, stubidp) | No | **Lowest** | Low | **Built-in** | Trivial / generated | Good for MCP-only testing | Minimal mock UI |

---

## Recommendation

### Default choice: **Authlib + Flask**, adapted from [`authlib/example-oidc-server`](https://github.com/authlib/example-oidc-server)

**Rationale:**

1. **Matches repo intent.** The map explicitly calls for a Python demo OIDC app packaged with uv — not a Docker sidecar ([map](../map.md)).
2. **Smallest credible Python OIDC AS.** The official OIDC example already implements authorization code + `id_token` issuance with SQLAlchemy persistence and a browser login/registration flow. That is exactly the upstream surface `OIDCProxy` consumes.
3. **FastMCP alignment.** `OIDCProxy` discovers `jwks_uri` and validates JWTs — RS256 + a JWKS route is the straightforward path (preferred over the example's HS256 dummy config). If access tokens remain opaque, set `verify_id_token=True` on the MCP server ([FastMCP PR #3248](https://github.com/PrefectHQ/fastmcp/pull/3248)).
4. **Low maintenance.** Pin `authlib`, `flask`, `flask-sqlalchemy` in the demo app's `pyproject.toml`; no JVM, no Node, no Django admin surface.
5. **Proven local-dev pattern.** `AUTHLIB_INSECURE_TRANSPORT=1` + SQLite is documented in Authlib's own examples.

**Concrete implementation sketch:**

```
demo-oidc/                    # uv app (sibling to mcp-server app)
  pyproject.toml              # authlib, flask, flask-sqlalchemy
  app/
    oauth2.py                 # from example-oidc-server + RS256 key
    routes.py                 # + /.well-known/openid-configuration, /oauth/jwks
    models.py                 # SQLite User, OAuth2Client, codes, tokens
  keys/rsa.pem                # dev-only; gitignored
```

**Seed data for local dev:**

- One `OAuth2Client` with `grant_types: [authorization_code]`, scopes `openid profile`, `token_endpoint_auth_method: client_secret_basic`, redirect URI `http://localhost:{MCP_PORT}/auth/callback`.
- Export `CLIENT_ID` / `CLIENT_SECRET` to the MCP app's env.
- Issuer and discovery URLs should use a single configurable base (e.g. `http://127.0.0.1:9000`).

**Run:**

```bash
export AUTHLIB_INSECURE_TRANSPORT=1
uv run flask --app app run --port 9000
```

### Runner-up: **django-oauth-toolkit**

Choose DOT when the team values **built-in discovery/JWKS/admin** over minimal footprint. Trade-off: pulling Django into a repo whose other app is FastMCP (not Django) increases total complexity for little gain in a demo-only IdP.

### Explicit non-choices

- **OAuthLib alone** — too much bespoke AS code.
- **Starlette/FastAPI AS** — no Authlib server integration; unnecessary given Flask example.
- **Keycloak / mock IdPs as default** — fine for CI or temporary MCP development, but they fail the "Python demo provider" requirement and add non-uv runtime dependencies.

---

## Suggested wiring to FastMCP (for implementers)

```python
from fastmcp import FastMCP
from fastmcp.server.auth.oidc_proxy import OIDCProxy

auth = OIDCProxy(
    config_url="http://127.0.0.1:9000/.well-known/openid-configuration",
    client_id=os.environ["DEMO_OIDC_CLIENT_ID"],
    client_secret=os.environ["DEMO_OIDC_CLIENT_SECRET"],
    base_url="http://127.0.0.1:8000",
    # verify_id_token=True,  # if demo AS issues opaque access tokens
)
mcp = FastMCP(name="Demo MCP", auth=auth)
```

Sources: [FastMCP OIDC Proxy](https://gofastmcp.com/servers/auth/oidc-proxy), [verify_id_token PR](https://github.com/PrefectHQ/fastmcp/pull/3248).

---

## Sources

- [FastMCP OIDC Proxy documentation](https://gofastmcp.com/servers/auth/oidc-proxy)
- [FastMCP `OIDCProxy` source (`verify_id_token`)](https://github.com/PrefectHQ/fastmcp/blob/main/src/fastmcp/server/auth/oidc_proxy.py)
- [FastMCP PR #3248 — `verify_id_token` option](https://github.com/PrefectHQ/fastmcp/pull/3248)
- [FastMCP `JWTVerifier` source](https://github.com/prefecthq/fastmcp/blob/main/fastmcp_slim/fastmcp/server/auth/providers/jwt.py)
- [Authlib project site](https://authlib.org/)
- [Authlib authorization server overview](https://docs.authlib.org/en/stable/oauth2/authorization-server/)
- [Authlib Flask OIDC Provider](https://docs.authlib.org/en/stable/oauth2/authorization-server/flask/openid-connect.html)
- [Authlib OIDC Discovery metadata](https://docs.authlib.org/en/v1.6.8/oauth/oidc/discovery.html)
- [authlib/example-oauth2-server](https://github.com/authlib/example-oauth2-server)
- [authlib/example-oidc-server](https://github.com/authlib/example-oidc-server)
- [Django OAuth Toolkit — OIDC](https://django-oauth-toolkit.readthedocs.io/en/latest/oidc.html)
- [Django OAuth Toolkit — Getting started](https://django-oauth-toolkit.readthedocs.io/en/latest/getting_started.html)
- [OAuthLib README](https://github.com/oauthlib/oauthlib)
- [Keycloak containers](https://www.keycloak.org/server/containers)
- [Dex](https://dexidp.io/)
- [mocc — minimal OIDC mock](https://github.com/jonasbg/mocc)
- [dev-oidc](https://github.com/camcima/dev-oidc)
- [stubidp](https://github.com/cerberauth/stubidp)
- [Stack Overflow — Authlib `.well-known` setup](https://stackoverflow.com/questions/61022475/any-examples-of-setting-up-well-known-url-using-authlib)
