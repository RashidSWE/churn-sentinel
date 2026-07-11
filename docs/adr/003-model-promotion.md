# ADR 003: Manual Model Promotion via metadata.json

**Status:** Accepted
**Date:** 2026-07-07

## Context

The API needs to know which trained model artifact is "active" at any given time. Training will happen repeatedly as we iterate (baseline → XGBoost → tuning), producing multiple versioned artifacts in `models/`. Something has to decide which one the API actually loads.

## Decision

A `models/metadata.json` file holds an `active_version` field. The API reads this file once at startup and loads the corresponding artifact.

Promotion (updating `active_version`) is a **deliberate, manual step** — not automatic at the end of every training run. A training run that underperforms shouldn't be able to silently replace a working model in production.

The API reads `metadata.json` once at startup, not on a polling loop — picking up a newly promoted model requires a restart/redeploy for v1.

## Alternatives Considered

- **Auto-promote on every training run**: rejected — no safeguard against a regression silently going live.
- **MLflow Model Registry**: the "real" way to do this, with proper staging/production tags and lineage. Deferred to a later phase (see PROJECT_PLAN.md backlog) — not needed yet at this project's scale, and hand-rolling the simple version first is a better learning step before adopting the heavier tool.
- **Hardcoded filename in code**: rejected — would require a code change + redeploy just to swap models, coupling an operational action to a code change.

## Consequences

- Promoting a new model is a manual edit to `metadata.json` (or a small script later) — acceptable overhead at this project's scale.
- If we ever want zero-downtime model swaps without a restart, this design needs revisiting (polling or a proper registry) — noted in docs/architecture.md §11 as a known limitation, not solved now.
- `metadata.json` becomes a small but real piece of state that needs to ship with `models/` — worth remembering when containerizing (Phase 6).