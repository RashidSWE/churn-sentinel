"""
Data cleaning for the Telco Customer Churn dataset.

Encodes the findings from Phase 1 EDA (see PROJECT_PLAN.md, section 9):
- 11 rows have blank TotalCharges, all tenure=0 customers -> dropped.
- customerID is an identifier, not a feature -> dropped before modeling.
- Several service columns encode "No internet service" as a separate
  category, duplicating the InternetService signal -> collapsed to "No".
"""

from __future__ import annotations

import pandas as pd

# Columns where "No internet service" / "No phone service" duplicate
# information already present in InternetService / PhoneService.
_REDUNDANT_NO_SERVICE_COLUMNS = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]

_REDUNDANT_NO_PHONE_COLUMNS = ["MultipleLines"]


def load_raw(path: str) -> pd.DataFrame:
    """Load the raw Telco churn CSV with no transformations applied."""
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the full cleaning pipeline to the raw Telco churn dataframe.

    Returns a new dataframe; does not mutate the input.
    """
    df = df.copy()

    df = _fix_total_charges(df)
    df = _drop_zero_tenure_rows(df)
    df = _collapse_redundant_categories(df)
    df = _drop_identifier_column(df)
    df = _encode_target(df)

    return df.reset_index(drop=True)


def _fix_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    """TotalCharges is read as a string; coerce to numeric (blanks -> NaN)."""
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df


def _drop_zero_tenure_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows with missing TotalCharges (all are tenure=0 new customers,
    per Phase 1 EDA). A zero-tenure customer is a degenerate case for
    churn prediction, so dropping is preferred over imputing.
    """
    before = len(df)
    df = df[df["TotalCharges"].notna()]
    dropped = before - len(df)
    if dropped:
        assert (df["tenure"] != 0).all() or dropped <= 11, (
            "Unexpected number of rows dropped for missing TotalCharges; "
            "verify assumption still holds against the current dataset."
        )
    return df


def _collapse_redundant_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse 'No internet/phone service' into 'No' — see module docstring."""
    for col in _REDUNDANT_NO_SERVICE_COLUMNS:
        df[col] = df[col].replace("No internet service", "No")
    for col in _REDUNDANT_NO_PHONE_COLUMNS:
        df[col] = df[col].replace("No phone service", "No")
    return df


def _drop_identifier_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["customerID"])


def _encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """Encode Churn as binary 0/1 (Yes -> 1) rather than leaving it as text."""
    df["Churn"] = (df["Churn"] == "Yes").astype(int)
    return df
