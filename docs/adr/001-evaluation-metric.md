# ADR 001: Use PR-AUC and Recall Instead of Accuracy as the Primary Evaluation Metric

**Status:** Accepted
**Date:** 2026-07-01

## Context

The Telco Customer Churn dataset has a class imbalance: 73.5% of customers did not churn, 26.5% did (see PROJECT_PLAN.md, Phase 1 Findings). A model that predicts "No churn" for every customer would score ~73.5% accuracy while providing zero business value — it would never catch a single at-risk customer.

We need a metric that reflects the actual business goal: identifying customers who are likely to churn so the business can intervene (retention offers, outreach, etc.) before they leave.

## Decision

We will use **PR-AUC (Precision-Recall Area Under Curve)** as the primary evaluation metric, with **recall on the churn class** tracked as a business-facing secondary metric, and **F1-score** as a summary statistic for quick comparisons.

Accuracy will still be logged for context but will not be used to select or tune models.

Rationale for the recall lean: a missed churner (false negative) generally costs the business more than a false alarm (false positive) — a false alarm just means a retention offer goes to someone who wasn't going to leave anyway, which is a minor cost. A missed churner is lost revenue with no chance to intervene. We will revisit this precision/recall tradeoff with a concrete cost-based threshold once we have a baseline model and can reason about the actual retention-offer cost vs. customer lifetime value.

## Alternatives Considered

- **Accuracy**: rejected — misleading on imbalanced data, as shown by the majority-class baseline scoring 73.5% while being useless.
- **ROC-AUC**: reasonable and will still be logged, but PR-AUC is more informative than ROC-AUC on imbalanced datasets because it focuses on the minority (churn) class rather than being dominated by the large number of true negatives.
- **Precision as primary**: rejected — over-optimizing for precision risks a model that only flags churners it's very confident about, missing many real churners. Given our cost asymmetry (see Decision), this is the wrong default lean.

## Consequences

- Model selection and hyperparameter tuning (Phase 3) will optimize for PR-AUC / recall, not accuracy — this needs to be explicit in the training code (`scoring` parameter in cross-validation, etc.) so we don't accidentally default to accuracy via library defaults.
- We'll need to pick a **classification threshold** deliberately (not just use the default 0.5) once we understand the precision/recall tradeoff at different thresholds — this will be a Phase 3 decision, documented in a follow-up ADR if the choice is non-trivial.
- Stakeholder-facing reporting (if we ever build a dashboard) should present recall and precision together, not accuracy alone, to avoid a misleading picture of model quality.
