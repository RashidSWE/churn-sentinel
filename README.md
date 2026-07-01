# churn-sentinel

An end-to-end ML pipeline for predicting customer churn — from raw data to a deployed, containerized API. Built as a continuously-developed learning project following real SDLC practices (design docs, ADRs, tests, CI/CD), not a one-off tutorial.

## What it does

Predicts which customers are likely to churn (cancel their subscription/service) based on account and usage attributes, using the [IBM Telco Customer Churn dataset](https://www.kaggle.com/blastchar/telco-customer-churn). Exposes predictions via a FastAPI service, containerized with Docker and deployed to a live endpoint.

## Project status

🚧 Actively in development. See [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) for the full roadmap and current phase.

## Architecture Decision Records

Significant design decisions are documented in [`docs/adr/`](./docs/adr/). Start with [ADR-001](./docs/adr/001-evaluation-metric.md) for why we optimize for PR-AUC/recall instead of accuracy.

## Repo structure

```
churn-sentinel/
├── PROJECT_PLAN.md          ← living roadmap, SDLC phases, tech stack
├── docs/adr/                 ← Architecture Decision Records
├── data/                     ← raw & processed data (gitignored, not committed)
├── notebooks/                ← exploratory analysis only — nothing here ships
├── src/churn_sentinel/       ← production code (data, models, api)
├── tests/                    ← unit + integration tests
├── models/                   ← trained model artifacts (gitignored)
├── Dockerfile, docker-compose.yml
└── .github/workflows/        ← CI/CD
```

## Local setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency and environment management (faster than pip, and gives us a reproducible `uv.lock`).

```bash
uv sync --extra dev
```

This creates a `.venv` and installs all dependencies (including dev tools) pinned to `uv.lock`. To run any command inside the environment:

```bash
uv run pytest
uv run uvicorn churn_sentinel.api.main:app --reload   # once the API exists
```

Or activate the venv directly:

```bash
source .venv/bin/activate
```

## Running tests

```bash
uv run pytest
```

(More usage instructions — training, running the API locally, Docker — will be added as those pieces are built.)