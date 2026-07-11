"""
Feature engineering for churn-sentinel

Builds a scikit-learn ColumnTransformer that is fit and serialized **together**
with the model (as a single sklearn pipeline in models/train.py).
This is deliberate: It means the exact same preprocessing logic that was fit on training
data is what runs at inference time in the API, eliminating train/serve skew as class of bug

Column groups are derived from the cleaned dataframe produced by churn_sentinel.data.cleaning.clean() - 
see the model for what's already been handled

"""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Binary Yes/No (or equivalent tow-value) categorical columns
# These are label-encodedl to 0/1 rather than one-hot encoded, since
# one-hot on a binary column just produces a redundant second column.
BINARY_COLUMNS = [
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "PaperlessBilling",
]

# Gender is binary but not Yes/No -- handled the same way, listed
# separately for clarity when reading the schema
GENDER_COLUMN = "gender"

# Nominal categorical columns with 3+ unrelated categories -> one-hot encode
NOMINAL_COLUMNS = ["InternetService", "Contract", "PaymentMethod"]

# Already-Numeric columns, used as-is (scaled for linear models)
NUMERIC_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges"]

# Senior Citizen is already 0/1 in the raw-data -- passthrough, no encoding needed
PASSTHROUGH_NUMERIC_COLUMNS = ["SeniorCitizen"]

TARGET_COLUMN = "Churn"

def get_feature_columns() -> list[str]:
    """ All columns expected as model input, in a stable order."""
    return (
        BINARY_COLUMNS
        + [GENDER_COLUMN]
        + NOMINAL_COLUMNS
        + NUMERIC_COLUMNS
        + PASSTHROUGH_NUMERIC_COLUMNS
    )

def build_preprocessor() -> ColumnTransformer:
    """
    Build the (unfit) preprocessing ColumnTransformer
    """
    binary_pipeline = Pipeline(
        steps=[("onehot", OneHotEncoder(drop="if_binary", handle_unknown="ignore"))]
    )
    nominal_pipeline = Pipeline(
        steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
    )
    numeric_pipeline = Pipeline(steps=[("scale", StandardScaler())])

    return ColumnTransformer(
        transformers=[
            ("binary", binary_pipeline, BINARY_COLUMNS + [GENDER_COLUMN]),
            ("nominal", nominal_pipeline, NOMINAL_COLUMNS),
            ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
            ("passthrough", "passthrough", PASSTHROUGH_NUMERIC_COLUMNS)
        ],
        remainder="drop",
    )