"""
Step 12: Run the evaluation with both the correctness evaluator (Step 6) and
the custom style-fit evaluator (Step 11) together, then compare the two
scoring dimensions per example.

Usage:
    python3 scripts/run_evaluation_with_custom.py
Writes: data/eval_results_multi_evaluator.json
"""

import json

from dotenv import load_dotenv
from langsmith import Client

from custom_evaluator import style_fit_evaluator
from evaluator import correctness_evaluator
from target_function import generate_title

load_dotenv()

DATASET_NAME = "blog-title-generation-medium-articles"
EXPERIMENT_PREFIX = "gpt-4o-mini-blog-title-multi-eval"
MAX_CONCURRENCY = 3
OUTPUT_PATH = "data/eval_results_multi_evaluator.json"


def main():
    client = Client()

    results = client.evaluate(
        generate_title,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator, style_fit_evaluator],
        experiment_prefix=EXPERIMENT_PREFIX,
        max_concurrency=MAX_CONCURRENCY,
    )

    print(results)

    rows = []
    for r in results:
        run = r["run"]
        example = r["example"]
        eval_results = r["evaluation_results"]["results"]

        def get(key, field):
            item = next((er for er in eval_results if er.key == key), None)
            return getattr(item, field) if item else None

        rows.append({
            "example_id": str(example.id),
            "primary_tag": example.metadata.get("primary_tag"),
            "reference_title": example.outputs["title"],
            "generated_title": run.outputs.get("title", "") if run.outputs else "",
            "correctness_score": get("correctness", "score"),
            "correctness_reasoning": get("correctness", "comment"),
            "style_fit_score": get("style_fit", "score"),
            "style_fit_reasoning": get("style_fit", "comment"),
        })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(rows, f, indent=2)

    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
