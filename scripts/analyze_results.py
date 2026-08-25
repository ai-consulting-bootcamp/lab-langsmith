"""
Step 9: Analyze evaluation results — aggregate metrics, categorical breakdown,
and error analysis. Reads data/eval_results_gpt-4o-mini.json (Step 7 output).

Usage:
    python3 scripts/analyze_results.py
"""

import json
import statistics
from collections import defaultdict

RESULTS_PATH = "data/eval_results_gpt-4o-mini.json"


def main():
    with open(RESULTS_PATH) as f:
        rows = json.load(f)

    scores = [r["correctness_score"] for r in rows]

    print("=== Aggregate Metrics ===")
    print(f"N: {len(scores)}")
    print(f"Mean:   {statistics.mean(scores):.3f}")
    print(f"Median: {statistics.median(scores):.3f}")
    print(f"Stdev:  {statistics.stdev(scores):.3f}")
    print(f"Min/Max: {min(scores)} / {max(scores)}")

    print("\n=== Categorical Analysis (by primary_tag) ===")
    by_tag = defaultdict(list)
    for r in rows:
        by_tag[r["primary_tag"]].append(r["correctness_score"])
    for tag, s in sorted(by_tag.items(), key=lambda kv: -statistics.mean(kv[1])):
        print(f"  {tag:<16} n={len(s)}  mean={statistics.mean(s):.2f}")

    print("\n=== Length gap (generated - reference chars) vs score ===")
    for r in sorted(rows, key=lambda r: r["correctness_score"]):
        gap = len(r["generated_title"]) - len(r["reference_title"])
        print(f"  score={r['correctness_score']:.1f}  length_gap={gap:+d}")

    gen_lens = [len(r["generated_title"]) for r in rows]
    ref_lens = [len(r["reference_title"]) for r in rows]
    print(f"\nMean generated title length: {statistics.mean(gen_lens):.1f} chars")
    print(f"Mean reference title length: {statistics.mean(ref_lens):.1f} chars")


if __name__ == "__main__":
    main()
