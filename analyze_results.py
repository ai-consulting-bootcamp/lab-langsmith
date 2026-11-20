"""Analyse baseline evaluation results: overall metrics, by category/difficulty, failures."""
import json
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/baseline_results.csv")

# Add metadata (category, difficulty, source) from the original examples file
with open("data/examples.json") as f:
    examples = json.load(f)
meta = pd.DataFrame([{"question": e["inputs"]["question"], **e["metadata"]} for e in examples])
df = df.merge(meta, left_on="inputs.question", right_on="question", how="left")

score = "feedback.correctness"
df[score] = df[score].astype(float)  # True/False -> 1.0/0.0

# ---------- Overall ----------
print("=== OVERALL ===")
print(f"Examples: {len(df)}")
print(f"Pass rate: {df[score].mean():.0%} ({int(df[score].sum())}/{len(df)})")
print(f"Median latency: {df['execution_time'].median():.2f}s")

# ---------- By category / difficulty ----------
print("\n=== BY DIFFICULTY ===")
by_diff = df.groupby("difficulty")[score].agg(["mean", "count"]).reindex(["easy", "medium", "hard"])
print(by_diff)

print("\n=== BY CATEGORY ===")
by_cat = df.groupby("category")[score].agg(["mean", "count"]).sort_values("mean")
print(by_cat)

# ---------- Failures ----------
print("\n=== FAILED EXAMPLES ===")
for _, r in df[df[score] == 0].iterrows():
    print(f"\n[{r['category']} / {r['difficulty']}] {r['inputs.question']}")
    print("  Model:    ", str(r["outputs.answer"])[:300])
    print("  Reference:", str(r["reference.answer"])[:300])

# ---------- Chart ----------
ax = by_cat["mean"].plot(kind="barh", figsize=(7, 4), xlim=(0, 1))
ax.set_xlabel("Pass rate")
ax.set_title("Correctness by category (gpt-4o-mini, judge gpt-4o-mini)")
plt.tight_layout()
plt.savefig("results/pass_rate_by_category.png", dpi=150)

df.to_csv("results/baseline_results_with_metadata.csv", index=False)
print("\nSaved chart and enriched CSV to results/")