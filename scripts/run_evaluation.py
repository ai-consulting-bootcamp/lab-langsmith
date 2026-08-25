"""
Step 7: Execute the evaluation experiment via LangSmith's client.evaluate(),
using the target function (Step 5) and correctness evaluator (Step 6) against
the blog-title-generation dataset (Step 4).

Usage:
    python3 scripts/run_evaluation.py
Writes: data/eval_results_gpt-4o-mini.json (per-example results, for Step 9 analysis)
"""

import json

from dotenv import load_dotenv
from langsmith import Client

from evaluator import correctness_evaluator
from target_function import generate_title

load_dotenv()

DATASET_NAME = "blog-title-generation-medium-articles"
EXPERIMENT_PREFIX = "gpt-4o-mini-blog-title"
MAX_CONCURRENCY = 3
OUTPUT_PATH = "data/eval_results_gpt-4o-mini.json"


def main():
    client = Client()

    results = client.evaluate(
        generate_title,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator],
        experiment_prefix=EXPERIMENT_PREFIX,
        max_concurrency=MAX_CONCURRENCY,
    )

    print(results)

    rows = []
    for r in results:
        run = r["run"]
        example = r["example"]
        eval_results = r["evaluation_results"]["results"]
        correctness = next((er.score for er in eval_results if er.key == "correctness"), None)
        comment = next((er.comment for er in eval_results if er.key == "correctness"), None)

        rows.append({
            "example_id": str(example.id),
            "primary_tag": example.metadata.get("primary_tag"),
            "reference_title": example.outputs["title"],
            "generated_title": run.outputs.get("title", "") if run.outputs else "",
            "correctness_score": correctness,
            "correctness_reasoning": comment,
            "run_id": str(run.id),
            "error": run.error,
        })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(rows, f, indent=2)

    n_scored = sum(1 for r in rows if r["correctness_score"] is not None)
    n_errors = sum(1 for r in rows if r["error"])
    print(f"\nCollected {len(rows)} results ({n_scored} scored, {n_errors} errors)")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
