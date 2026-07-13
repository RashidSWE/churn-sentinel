# Churn-sentinel - System Design
**status**: Accepted, **Last Updated**: 2026/07/07 **Supersedes**: Initial draft
----

## 1. Purpose
This document defines the architecture of churn-sentinel before implementation:
Component responsibilities, System boundaries, data flow, and the API contract. It's the reference for "how does this piece talk to that piece" questions during phase 3+

## 2. Archtectural style
Each layer depends on the layer below it( Layered architecture )

```
Presentation Layer   (API — request/response, validation)
        │
Application Layer    (Prediction Service — orchestrates inference)
        │
Machine Learning Layer (preprocessing pipeline + model)
        │
Data Layer           (raw dataset, cleaning, feature engineering)

```
Benefits: Separation of concerns, easier testing per layer, the model can be swapped without touching the API, the preprocessing pipeline is reused identically at training and inference time.

## 3. Component breakdown
| Component | Location | Responsibility |
|---|---|---|
| API | `src/churn_sentinel/api/` | Receive HTTP requests, validate input (Pydantic), call the Prediction Service, return JSON, expose `/docs`. **No ML logic here.** |
| Prediction Service | `src/churn_sentinel/models/predict.py` | Load the active model pipeline, run inference, shape the response. The API never touches the model directly — only this service does. |
| Data Processing | `src/churn_sentinel/data/` | Cleaning, feature engineering. Training and inference call the *same* fitted pipeline object — this is what prevents train/serve skew. |
| Model Training | `src/churn_sentinel/models/train.py` | Train, cross-validate, evaluate, serialize a model + pipeline to `models/`. |
| Model Registry | `models/` (repo root) | Versioned artifacts + `metadata.json` (see §5.5). |
| Config | `src/churn_sentinel/config/` | Centralized settings (model path, log level, etc.), loaded from environment variables. **New addition** vs. the original Phase 2 repo scaffold — reflected in PROJECT_PLAN.md. |
| Utils | `src/churn_sentinel/utils/` | Shared helpers with no home in the above (e.g. logging setup). **New addition**, same as above. |

## Data Flow
Training and serving are separate lifecycles with different triggers and different frequencies. Keeping them as two diagrams( not one) makes that explicit.

**4.1 Training flow** — runs manually or on a schedule, is allowed to be slow:
 
```
CSV (data/raw/)
   │
   ▼
Clean (churn_sentinel.data.cleaning)
   │
   ▼
Feature Engineering — preprocessor.fit_transform()
   │
   ▼
Train model (churn_sentinel.models.train)
   │
   ▼
Evaluate (PR-AUC, recall — per ADR-001)
   │
   ▼
Serialize {preprocessor + model} as one Pipeline → models/model_vN.pkl
   │
   ▼
Update models/metadata.json (see §5.5) — a deliberate, explicit step, not automatic
```
 
**4.2 Serving flow** — runs per-request, must be fast:
 
```
API startup: read models/metadata.json → load the active_version pipeline ONCE
   │
   ▼
Request arrives → Pydantic validation
   │
   ▼
preprocessor.transform()  ← transform only, NEVER re-fit
   │
   ▼
model.predict_proba()
   │
   ▼
Shape response → JSON
```
 
The "transform, not fit" distinction matters: at inference time we're reusing exactly what was learned during training. Re-fitting per request would be both slow and wrong (it would fit on a single row).
 
## 5. API Contract
 
### 5.1 `POST /predict`
 
**Request body:**
 
```json
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 12,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "Yes",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "Yes",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 70.35,
  "TotalCharges": 845.50
}
```
 
Field names and types mirror `get_feature_columns()` in `churn_sentinel.data.features` exactly — this is deliberate, so the Pydantic model and the training feature list can be checked against each other.
 
**Success response (200):**
 
```json
{
  "prediction": "Churn",
  "probability": 0.87
}
```
 
`probability` is the raw model output — no "confidence: High/Medium/Low" bucketing. Turning a probability into a business label requires defined thresholds, Shipping the raw number now avoids inventing an unstated threshold; bucketing can be added later as an explicit, documented decision.
 
**Validation error response (422):** FastAPI/Pydantic's default shape is used as-is, it stays consistent with the auto-generated OpenAPI docs.
 
**Internal error response (500):**
 
```json
{
  "error": "InternalError",
  "message": "Prediction failed."
}
```
 
Deliberately generic — internal exception details are logged (with a request ID), not returned to the client.
 
### 5.2 `GET /health`
 
Distinguishes **liveness** (is the process running?) from **readiness** (can it actually serve a correct prediction right now?) — same concept Kubernetes uses.
 
```json
{
  "status": "healthy",
  "model_version": "v2"
}
```
 
or, per the decision to start anyway but report unhealthy if the model failed to load:
 
```json
{
  "status": "unhealthy",
  "reason": "model_load_failed"
}
```
 
**HTTP status code:** `200` when healthy, **`503`** when unhealthy — deploy platforms and load balancers typically key off the status code, not the body.
 
### 5.3 `GET /model-info`
 
```json
{
  "model_version": "v2",
  "trained_at": "2026-07-01T10:00:00Z",
  "metrics": {"pr_auc": 0.63, "recall": 0.81}
}
```
 
Read from `metadata.json` — lets a client check what's actually deployed without redeploying anything.
 
## 6. Model Versioning & Registry
 
`models/` holds versioned artifacts plus one small pointer file:
 
```
models/
  model_v1.pkl
  model_v2.pkl
  metadata.json
```
 
```json
{
  "active_version": "v2",
  "versions": {
    "v2": {"trained_at": "2026-07-01T10:00:00Z", "metrics": {"pr_auc": 0.63, "recall": 0.81}},
    "v1": {"trained_at": "2026-06-28T09:00:00Z", "metrics": {"pr_auc": 0.60, "recall": 0.75}}
  }
}
```
 
**Decisions made:**
- `active_version` is written by a **deliberate promotion step**, not automatically at the end of every training run. A training run that produces a worse model shouldn't silently replace a working one in production — promotion is a conscious choice.
- The API reads `metadata.json` **once, at startup**. Picking up a newly-promoted model requires a redeploy/restart for v1. Polling for changes without a restart is a possible future enhancement, not needed now.
## 7. Deployment Architecture
 
Deployment target is **intentionally left open** (Render vs. Fly.io — see PROJECT_PLAN.md open decisions). The architecture doesn't depend on which one we pick — that's the point of containerizing:
 
```
Internet
   │
   ▼
[ Render  |  Fly.io — target TBD ]
   │
FastAPI Application (Docker container)
   │
Trained Model Pipeline (loaded from models/ at startup)
```
 
**Future (not v1):** load balancer → multiple FastAPI containers → shared/external model storage, once there's a reason to scale beyond one instance.
 
## 8. Error Handling Strategy
 
| Code | Meaning | Example |
|---|---|---|
| 200 | Success | prediction returned |
| 422 | Validation error | malformed/missing request field (FastAPI default shape) |
| 500 | Internal error | unexpected exception during inference |
| 503 | Service unhealthy | `/health` — model failed to load |
 
## 9. Logging Strategy
 
`structlog` for structured logs. Log: incoming request ID, prediction + probability, model version used, latency, errors, startup events.
 
**Do not log:** the full raw request payload verbatim. Even though this dataset has no direct PII beyond `customerID` (already dropped before reaching the model), logging every field of every request is unnecessary.
 
## 10. Security Considerations
 
**Now:** input validation via Pydantic, no secrets in source control, config via environment variables (see §3, Config component).
**Later (not v1):** API keys/auth, HTTPS enforcement, rate limiting, audit logging.
 
## 11. Non-Functional Notes for Later Phases
 
- **Zero-downtime deploy:** not solved in v1 — a redeploy will have brief downtime. Acceptable for a learning project; revisit if this ever needs to be "always on."
- **Model drift detection:** flagged for Phase 9 (Monitoring), not designed yet.
- **Scaling beyond one instance:** the layered separation (API / preprocessing / model / training) is what makes this possible later without a rewrite — no action needed now.
## 12. Repo Structure Update
 
Reflects the `config/` and `utils/` additions from this design pass:
 
```
src/churn_sentinel/
├── api/          ← REST endpoints
├── data/         ← cleaning, feature engineering
├── models/       ← training, prediction service, evaluation
├── config/       ← settings, loaded from environment variables (NEW)
└── utils/        ← shared helpers, e.g. logging setup (NEW)
```
 
## 13. Future Architecture Evolution
 
MLflow Model Registry (replacing the hand-rolled `metadata.json`), SHAP explainability, drift detection (Evidently), scheduled retraining, PostgreSQL for prediction history, auth, Docker Compose multi-service, Kubernetes, Prometheus/Grafana.