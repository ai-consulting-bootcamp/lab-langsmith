"""
Step 15: Analyze cost-performance trade-offs between the models compared in
Step 14 (scripts/run_ab_comparison.py). Reads data/ab_comparison_results.json.

Usage:
    python3 scripts/analyze_cost_performance.py
"""

import json
import statistics
from collections import defaultdict

RESULTS_PATH = "data/ab_comparison_results.json"


def main():
    with open(RESULTS_PATH) as f:
        rows = json.load(f)

    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)

    print(f"{'Model':<14} {'N':>3} {'Mean Score':>11} {'Total Cost':>12} {'Cost/Example':>14} {'Mean Latency':>14}")
    summary = {}
    for model, model_rows in by_model.items():
        scores = [r["correctness_score"] for r in model_rows]
        costs = [r["total_cost"] for r in model_rows]
        latencies = [r["latency_seconds"] for r in model_rows]
        mean_score = statistics.mean(scores)
        total_cost = sum(costs)
        cost_per_example = total_cost / len(costs)
        mean_latency = statistics.mean(latencies)

        summary[model] = {
            "n": len(model_rows),
            "mean_score": mean_score,
            "total_cost": total_cost,
            "cost_per_example": cost_per_example,
            "mean_latency": mean_latency,
        }
        print(f"{model:<14} {len(model_rows):>3} {mean_score:>11.3f} ${total_cost:>10.5f} ${cost_per_example:>12.6f} {mean_latency:>12.3f}s")

    print("\n=== Cost-Performance Ratios ===")
    models = list(summary.keys())
    if len(models) == 2:
        a, b = models
        score_gain = summary[b]["mean_score"] - summary[a]["mean_score"]
        cost_multiple = summary[b]["cost_per_example"] / summary[a]["cost_per_example"]
        print(f"{b} vs {a}: +{score_gain:.3f} mean score for {cost_multiple:.1f}x the cost per example")
        print(f"Cost per +0.01 score gained by switching to {b}: "
              f"${(summary[b]['cost_per_example'] - summary[a]['cost_per_example']) / (score_gain * 100):.6f}"
              if score_gain > 0 else "No score gain from the more expensive model.")

    # Extrapolated cost at scale
    print("\n=== Extrapolated Cost at Scale ===")
    for model, s in summary.items():
        print(f"{model}: ${s['cost_per_example'] * 1000:.2f} per 1,000 titles generated")


if __name__ == "__main__":
    main()
