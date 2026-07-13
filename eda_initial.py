import pandas as pd

df = pd.read_csv("/Users/rashka/dev/Personal_Projects/churn-sentinel/data/raw/Telco-Customer-Churn.csv")

print("=== Shape ===")
print(df.shape)

print("\n=== Dtypes ===")
print(df.dtypes)

print("\n=== Churn class balance ===")
print(df["Churn"].value_counts())
print(df["Churn"].value_counts(normalize=True).round(3))

print("\n=== Missing values ===")
print(df.isnull().sum()[df.isnull().sum() > 0])

print("\n=== TotalCharges dtype issue check ===")
# Known quirk: TotalCharges has blank strings for tenure=0 customers
bad_rows = df[pd.to_numeric(df["TotalCharges"], errors="coerce").isnull()]
print(f"Rows where TotalCharges isn't numeric: {len(bad_rows)}")
print(bad_rows[["customerID", "tenure", "TotalCharges", "Churn"]])

print("\n=== Duplicate customerIDs ===")
print(df["customerID"].duplicated().sum())

print("\n=== Numeric summary ===")
print(df[["tenure", "MonthlyCharges"]].describe())

print("\n=== Categorical cardinality ===")
cat_cols = df.select_dtypes(include="object").columns.tolist()
for c in cat_cols:
    if c not in ("customerID",):
        print(f"{c}: {df[c].nunique()} unique -> {df[c].unique()[:6]}")
