import pandas as pd


DATA_PATH = "data/trialgpt_criterion_annotations.parquet"


df = pd.read_parquet(DATA_PATH)


print("\nShape:")
print(df.shape)


print("\nColumns:")
print(df.columns.tolist())


print("\nFirst 3 rows:")
print(df.head(3).to_string())


print("\nEligibility labels:")
print(df["expert_eligibility"].value_counts(dropna=False))


print("\nCriterion types:")
print(df["criterion_type"].value_counts(dropna=False))


print("\nUnique patients:")
print(df["patient_id"].nunique())


print("\nUnique trials:")
print(df["trial_id"].nunique())