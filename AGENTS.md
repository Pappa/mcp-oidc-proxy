# Agent instructions

## Agent skills

### Issue tracker

Issues and specs live as markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context layout: `CONTEXT.md` at the repo root and ADRs under `docs/adr/`. See `docs/agents/domain.md`.

## Python tooling

### Installing packages

Install Python packages with uv only

- **Never** run `pip install`, `pip3 install`, or `python -m pip install`.
- **Always ask the user** before adding or upgrading any Python dependency.
- When the user approves an install, use **uv**:
  - `uv add <package>` for runtime deps
  - `uv add --dev <package>` or `uv add --group dev <package>` for dev deps
  - `uv sync` to install from the lockfile

### Testing and Quality Gates

Before completing any work, the following quality gates should all pass.

Pytest:

```bash
uv run pytest
```

ty:

```bash
uv run ty check
```

Ruff:

```bash
uv run ruff check --fix && uv run ruff check
uv run ruff format && uv run ruff format --check
```