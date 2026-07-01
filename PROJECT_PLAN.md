# churn-sentinel — End-to-End ML Pipeline for Customer Churn Prediction

**Status:** Planning complete → Ready for Phase 1
**Last updated:** 2026-07-01
**Repo name:** `churn-sentinel`
**Type:** Living document — update this as the project evolves. Don't let it go stale.

---

## 1. Project Charter

**Problem statement:** Subscription businesses lose revenue when customers churn (cancel/stop using the service) without warning. We will build a system that predicts which customers are likely to churn, so a business could act on it (retention offers, outreach, etc.).

**Goals:**
- Learn the full SDLC for an ML system, not just model training
- Produce a portfolio-worthy, professionally structured repo
- Build something we keep iterating on, not a one-off

**Non-goals (v1):**
- Not building a real-time streaming system
- Not building a user-facing web app (API only, for now)
- Not doing deep learning — tabular data doesn't need it, and it would obscure the actual learning goal (deployment, not model architecture)

**Success criteria for v1:**
- Model achieves reasonable performance (we'll define the metric in Phase 1)
- API is deployed and publicly reachable
- Repo has tests, CI, and documentation a stranger could follow
- You can explain every part of the stack in an interview

---

## 2. SDLC Phases & Roadmap

We'll work in phases. Each phase has a clear Definition of Done (DoD) before moving to the next — but this is iterative, not waterfall-rigid. We'll revisit earlier phases as we learn things.

| Phase | Focus | Status |
|---|---|---|
| 0. Planning | This document | ✅ Done |
| 1. Requirements & Data | Define metrics, source dataset, EDA | ✅ Done |
| 2. Design & Architecture | System design, repo structure, ADRs | ✅ Done |
| 3. Model Development | Baseline → iterate, experiment tracking | ⬜ Next |
| 4. API Layer | FastAPI service wrapping the model | ⬜ |
| 5. Testing | Unit, integration, model validation tests | ⬜ |
| 6. Containerization | Dockerfile, local docker-compose | ⬜ |
| 7. CI/CD | GitHub Actions: lint, test, build, deploy | ⬜ |
| 8. Deployment | Render or Fly.io, live endpoint | ⬜ |
| 9. Monitoring & Observability | Logging, basic metrics, drift checks | ⬜ |
| 10. Continuous Development | Backlog of v2+ features (below) | 🔁 Ongoing forever |

---

## 3. Phase 1 Preview — Requirements & Data (what's next)

When we start, we'll nail down:
- **Dataset**: likely the Telco Customer Churn dataset (Kaggle/IBM) — clean, well-known, realistic size (~7K rows). Alternative: a synthetic dataset if you want to practice data generation too.
- **Target metric**: churn is usually imbalanced, so accuracy is the wrong primary metric. We'll likely use **recall** or **F1/PR-AUC** depending on the business framing (catching churners matters more than overall accuracy).
- **EDA**: understand features, class imbalance, missingness, correlations.
- **Acceptance criteria**: a number we're trying to beat (e.g. "beat a naive baseline that predicts majority class").

---

## 4. Proposed Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | Your choice, ML ecosystem standard |
| Env/dependency mgmt | uv | Fast, reproducible (`uv.lock`), replaces pip + venv |
| Data/EDA | pandas, matplotlib/seaborn | Standard, well-documented |
| Modeling | scikit-learn → XGBoost/LightGBM | Strong tabular performance, fast CPU training |
| Experiment tracking | MLflow (local) | Industry-standard, teaches a real MLOps tool |
| API | FastAPI | Modern, async, auto-generates OpenAPI docs |
| Validation | Pydantic | Pairs with FastAPI, type-safe request/response |
| Testing | pytest | Standard Python testing |
| Containerization | Docker | The "last mile" skill this project is built around |
| CI/CD | GitHub Actions | Free, integrates directly with your repo |
| Deployment | Render (free tier) | Simpler than Fly.io for a first deploy; we can migrate later |
| Monitoring | structlog + simple metrics endpoint | Lightweight, no need for a full observability stack yet |

We will treat every tech choice as reversible — if something annoys you in practice, we swap it and note why in an ADR (see below).

---

## 5. Repo Structure (proposed)

```
churn-sentinel/
├── README.md
├── PROJECT_PLAN.md          ← this doc, kept up to date
├── docs/
│   └── adr/                 ← Architecture Decision Records
├── data/
│   ├── raw/                 ← gitignored, raw data
│   └── processed/           ← gitignored, cleaned data
├── notebooks/                ← EDA, exploratory only — nothing here ships
├── src/
│   ├── churn_sentinel/
│   │   ├── data/             ← loading, cleaning, feature engineering
│   │   ├── models/           ← training, evaluation
│   │   └── api/               ← FastAPI app
├── tests/
│   ├── unit/
│   └── integration/
├── models/                   ← serialized trained model artifacts (or DVC-tracked)
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/        ← CI/CD pipelines
├── requirements.txt / pyproject.toml
└── .gitignore
```

**Why this matters:** notebooks are for exploration only — production code lives in `src/`, tested and importable. This is the #1 thing that separates "tutorial ML" from "real ML engineering."

---

## 6. Engineering Practices We'll Follow

- **Architecture Decision Records (ADRs)**: every non-trivial decision (e.g. "why XGBoost over a neural net," "why Render over Fly.io") gets a short markdown file in `docs/adr/`. This is a real industry practice and great portfolio signal.
- **Trunk-based git flow**: `main` always deployable, feature branches, PRs even though it's solo (good habit, gives you a PR history to show).
- **Conventional commits**: `feat:`, `fix:`, `docs:`, `test:` prefixes — keeps history readable and can auto-generate changelogs later.
- **Test pyramid**: lots of fast unit tests (data transforms, feature engineering), fewer integration tests (API endpoints), minimal end-to-end tests.
- **Model versioning**: every trained model gets a version + metrics logged (MLflow handles this), so we can always answer "why did predictions change?"
- **12-factor app principles** where relevant: config via environment variables, no secrets in code, stateless service.

---

## 7. Continuous Development Backlog (v2+)

This is the "we never really finish" list — pull from this whenever you want to extend the project:

- [ ] Add a simple frontend (Streamlit or a small React app) to demo predictions
- [ ] Add data drift detection (e.g. with `evidently`) and a scheduled check job
- [ ] Add model retraining pipeline triggered by new data
- [ ] Add authentication to the API (API keys or OAuth)
- [ ] Add A/B testing between two model versions
- [ ] Swap deployment target to compare Render vs Fly.io vs a VPS
- [ ] Add a feature store (even a toy one) if you want to go deeper into MLOps
- [ ] Write a blog post / README case study explaining the system design (great for portfolio)
- [ ] Add load testing (locust) to see how the free-tier deployment holds up
- [ ] Explore explainability (SHAP values) and expose them via the API

---

## 8. Open Decisions

- [x] **Exact dataset source**: IBM Telco Customer Churn dataset (7,043 rows, 21 cols), pulled from a public GitHub mirror. Stored at `data/raw/Telco-Customer-Churn.csv` (gitignored — raw data isn't committed).
- [x] **Primary evaluation metric**: PR-AUC as primary, recall on churn class as a secondary business-facing metric, F1 as a summary stat. Accuracy explicitly rejected due to class imbalance (see Phase 1 findings below).
- [ ] Render vs Fly.io for final deploy (can prototype on both)
- [ ] Whether to use MLflow locally or skip it for v1 and add later

---

## 9. Phase 1 Findings (EDA)

**Class balance**: 73.5% No-churn / 26.5% Churn. Confirms accuracy is the wrong primary metric — a model that always predicts "No churn" would score ~73.5% while being useless.

**Data quality**:
- 11 rows (0.15%) have blank `TotalCharges` — all are `tenure = 0` customers (brand new, so an empty lifetime-charges value is legitimate, not corrupted data). Decision: **drop these rows** in the cleaning step; a zero-tenure customer is a degenerate case for churn prediction anyway.
- No duplicate `customerID`s, no other missing values. Dataset is otherwise clean.
- No numeric outliers of concern (`tenure`: 0–72 months, `MonthlyCharges`: $18–$119).

**Feature notes**:
- 16 categorical columns (mostly binary or 3-valued), 3 numeric (`tenure`, `MonthlyCharges`, `TotalCharges`), 1 ID column (`customerID`, drop before training).
- Several service-related columns (`OnlineSecurity`, `TechSupport`, `StreamingTV`, etc.) encode `"No internet service"` as a separate category — this duplicates the signal already in `InternetService`. Plan to collapse this during feature engineering to avoid redundant one-hot columns.

**Acceptance baseline (to beat)**: a naive majority-class classifier scores 0% recall on churners. Any real model needs to meaningfully beat that — we'll set a concrete PR-AUC/recall target once we have a first baseline model trained (Phase 3).

---

## 10. Phase 2 Deliverables (Design & Architecture)

Repo scaffolded on disk following the structure in section 5:
- Full directory tree created (`src/churn_sentinel/`, `tests/`, `docs/adr/`, etc.)
- `pyproject.toml` — dependencies (pandas, scikit-learn, xgboost, fastapi, mlflow, etc.) and dev tools (pytest, ruff)
- `.gitignore` — excludes raw/processed data, model artifacts, mlruns, standard Python/editor cruft
- `README.md` — project overview, structure, local setup instructions
- **ADR-001** (`docs/adr/001-evaluation-metric.md`): formalizes the PR-AUC/recall-over-accuracy decision from Phase 1, including the precision/recall cost tradeoff reasoning and alternatives considered
- ADR template (`docs/adr/template.md`) for future decisions

**Data cleaning module** (`src/churn_sentinel/data/cleaning.py`) — first real production code, encoding the Phase 1 EDA findings:
- Coerces `TotalCharges` to numeric, drops the 11 blank-value (tenure=0) rows
- Drops `customerID` (identifier, not a feature)
- Collapses redundant `"No internet/phone service"` categories down to `"No"`
- Encodes `Churn` target as binary 0/1

Validated with **6 passing unit tests** (`tests/unit/test_cleaning.py`) covering each transformation, plus a manual end-to-end run against the full real dataset (7,043 → 7,032 rows, 21 → 20 columns, zero NaNs remaining, confirms the pipeline behaves as designed).

---

## Next Step

Move into **Phase 3: Model Development** — split data, engineer remaining features (encoding categoricals, scaling if needed), train a baseline model, and set up MLflow experiment tracking.