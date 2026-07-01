import pandas as pd
import pytest

from churn_sentinel.data.cleaning import clean


@pytest.fixture
def raw_sample() -> pd.DataFrame:
    """A small synthetic sample mirroring the real dataset's quirks."""
    return pd.DataFrame(
        {
            "customerID": ["0001-AAA", "0002-BBB", "0003-CCC"],
            "gender": ["Female", "Male", "Female"],
            "SeniorCitizen": [0, 0, 1],
            "Partner": ["Yes", "No", "No"],
            "Dependents": ["No", "No", "Yes"],
            "tenure": [1, 0, 34],
            "PhoneService": ["No", "Yes", "Yes"],
            "MultipleLines": ["No phone service", "No", "Yes"],
            "InternetService": ["DSL", "No", "Fiber optic"],
            "OnlineSecurity": ["No", "No internet service", "Yes"],
            "OnlineBackup": ["Yes", "No internet service", "No"],
            "DeviceProtection": ["No", "No internet service", "Yes"],
            "TechSupport": ["No", "No internet service", "No"],
            "StreamingTV": ["No", "No internet service", "Yes"],
            "StreamingMovies": ["No", "No internet service", "Yes"],
            "Contract": ["Month-to-month", "Month-to-month", "One year"],
            "PaperlessBilling": ["Yes", "Yes", "No"],
            "PaymentMethod": [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
            ],
            "MonthlyCharges": [29.85, 45.0, 56.95],
            # Row 2 (index 1) simulates the real dataset's blank-TotalCharges
            # quirk for a zero-tenure customer.
            "TotalCharges": ["29.85", " ", "1889.5"],
            "Churn": ["No", "No", "Yes"],
        }
    )


def test_clean_drops_blank_total_charges_rows(raw_sample):
    result = clean(raw_sample)
    assert result["TotalCharges"].isna().sum() == 0
    assert len(result) == 2  # the tenure=0 row with blank TotalCharges is dropped


def test_clean_drops_customer_id(raw_sample):
    result = clean(raw_sample)
    assert "customerID" not in result.columns


def test_clean_encodes_churn_as_binary(raw_sample):
    result = clean(raw_sample)
    assert set(result["Churn"].unique()) <= {0, 1}
    assert result["Churn"].dtype.kind in "iu"  # integer dtype


def test_clean_collapses_no_internet_service_category(raw_sample):
    result = clean(raw_sample)
    for col in ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]:
        assert "No internet service" not in result[col].unique()


def test_clean_collapses_no_phone_service_category(raw_sample):
    result = clean(raw_sample)
    assert "No phone service" not in result["MultipleLines"].unique()


def test_clean_does_not_mutate_input(raw_sample):
    original_columns = list(raw_sample.columns)
    clean(raw_sample)
    assert list(raw_sample.columns) == original_columns
    assert "customerID" in raw_sample.columns
