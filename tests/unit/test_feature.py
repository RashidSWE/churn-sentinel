import numpy as np
import pandas as pd
import pytest

from churn_sentinel.data.cleaning import clean, load_raw
from churn_sentinel.data.features import (
    build_preprocessor,
    get_feature_columns,
    TARGET_COLUMN,
)

RAW_PATH = "data/raw/Telco-Customer-Churn.csv"


@pytest.fixture(scope="module")
def cleaned_df() -> pd.DataFrame:
    return clean(load_raw(RAW_PATH))


def test_feature_columns_all_present_in_cleaned_data(cleaned_df):
    missing = set(get_feature_columns()) - set(cleaned_df.columns)
    assert not missing, f"Feature columns missing from cleaned data: {missing}"


def test_preprocessor_fits_and_transforms_without_error(cleaned_df):
    X = cleaned_df[get_feature_columns()]
    preprocessor = build_preprocessor()
    transformed = preprocessor.fit_transform(X)
    # Output should be fully numeric and have no NaNs
    assert not np.isnan(transformed.toarray() if hasattr(transformed, "toarray") else transformed).any()


def test_preprocessor_output_is_numeric(cleaned_df):
    X = cleaned_df[get_feature_columns()]
    preprocessor = build_preprocessor()
    transformed = preprocessor.fit_transform(X)
    arr = transformed.toarray() if hasattr(transformed, "toarray") else transformed
    assert np.issubdtype(arr.dtype, np.number)


def test_preprocessor_handles_unseen_category_at_transform_time(cleaned_df):
    """Simulates a category at inference time that wasn't seen during fit —
    should not raise, thanks to handle_unknown='ignore'."""
    X = cleaned_df[get_feature_columns()].copy()
    preprocessor = build_preprocessor()
    preprocessor.fit(X)

    X_new = X.iloc[[0]].copy()
    X_new["PaymentMethod"] = "Some New Payment Method"
    # Should not raise
    preprocessor.transform(X_new)


def test_target_column_not_in_feature_columns():
    assert TARGET_COLUMN not in get_feature_columns()