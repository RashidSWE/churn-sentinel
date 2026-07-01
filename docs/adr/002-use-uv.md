# ADR 002: Use uv for Dependency and Environment Management

**Status:** Accepted
**Date:** 2026-07-01

## Context

Phase 2 originally scaffolded the project with a standard `pip` + `venv` workflow (`pyproject.toml` with a `[project.optional-dependencies]` dev group, installed via `pip install -e ".[dev]"`). This works but is slow to resolve/install and doesn't produce a lockfile by default, so "it works on my machine" drift is possible over time.

## Decision

Use [uv](https://docs.astral.sh/uv/) as the environment and dependency manager for this project, replacing `pip` + `venv` directly. `uv.lock` is committed to the repo for reproducible installs.

Setup becomes:
```bash
uv sync --extra dev
uv run pytest
```

`pyproject.toml` stays the source of truth for dependencies — uv reads it natively, so no structural changes were needed there, only to the setup instructions in `README.md`.

## Alternatives Considered

- **pip + venv** (original setup): works, but slower installs and no lockfile by default.
- **Poetry**: mature and widely used, but slower than uv and adds another layer of config (`poetry.lock`, its own dependency resolution quirks) without a clear benefit here.
- **conda**: overkill for a project with no complex native/binary dependencies beyond what pip wheels already cover (xgboost, scikit-learn, etc. all ship wheels).

## Consequences

- `uv.lock` must be committed and kept in sync — contributors run `uv sync` instead of `pip install`.
- CI (Phase 7) will use uv to install dependencies, which should also speed up GitHub Actions runs via uv's caching.
- Docker (Phase 6) will install uv inside the image and use `uv sync --frozen` for reproducible, fast builds — noted here so it isn't forgotten when we get there.
