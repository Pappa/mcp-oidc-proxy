# Initial charting decisions

Type: grilling

Status: resolved

## Question

Lock in early decisions from the charting grilling round: repo layout, verification approach, and MCP tool surface.

## Answer

- **Repo layout**: uv workspace monorepo with two member apps (e.g. `apps/auth-server/` and `apps/mcp-server/`).
- **Verification**: automated smoke tests that launch both servers locally and exercise the auth flow end-to-end.
- **MCP tools**: a single `hello_world` tool returning canned output — sufficient to prove auth gating.

## Comments

Resolved from user answers during initial map charting (Q1–Q3).
