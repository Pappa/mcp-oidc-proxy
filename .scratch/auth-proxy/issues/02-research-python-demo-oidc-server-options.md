# Which Python stack should implement the demo OIDC provider?

Type: research

Status: resolved

## Question

Survey practical options for a minimal, local-only OIDC/OAuth2 authorization server written in Python (libraries, frameworks, or lightweight IdPs runnable from Python/uv). Compare complexity, maintenance burden, and fit with FastMCP OIDCProxy requirements. Recommend a default choice for this prototype.

## Answer

Full findings: [python-demo-oidc-server-options.md](../research/python-demo-oidc-server-options.md)

**Gist:** Default choice is **NanoIDP** as a thin uv workspace app (dependency + YAML config + launcher) — built-in discovery, JWKS, RS256, login UI; auth on port `9000`, MCP on `8000`. Runner-up is **Authlib + Flask** from `example-oidc-server` when full AS code ownership is preferred. Third: django-oauth-toolkit. Non-choices: OAuthLib alone, Keycloak/Docker sidecars.
