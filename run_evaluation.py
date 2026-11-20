"""Run the full LangSmith evaluation on the AML dataset and export results."""
import os
from aml_eval import client, target, correctness_evaluator, DATASET_NAME

os.makedirs("results", exist_ok=True)

results = client.evaluate(
    target,
    data=DATASET_NAME,
    evaluators=[correctness_evaluator],
    experiment_prefix="gpt-4o-mini-t0-baseline",  # model + config
    max_concurrency=2,                           # stay under rate limits
)

df = results.to_pandas()
df.to_csv("results/baseline_results.csv", index=False)

print(f"\n{len(df)} rows evaluated (expected 18)")
print(df.columns.tolist())  # so we know the exact score column name