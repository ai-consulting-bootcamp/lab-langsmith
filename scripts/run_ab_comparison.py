"""
Step 14: A/B comparison of gpt-4o-mini vs gpt-4o on the blog-title-generation
task - same dataset, same correctness evaluator, so the only variable is the
target model. Collects per-example score, token usage, cost, and latency
(all pulled directly from LangSmith's run records) for the Step 15 analysis.

Usage:
    python3 scripts/run_ab_comparison.py
Writes: data/ab_comparison_results.json
"""

import json
import time

from dotenv import load_dotenv
from langsmith import Client

from evaluator import correctness_evaluator
from target_function import generate_title, generate_title_gpt4o

load_dotenv()

DATASET_NAME = "blog-title-generation-medium-articles"
MAX_CONCURRENCY = 3
OUTPUT_PATH = "data/ab_comparison_results.json"

CONFIGURATIONS = [
    {"model": "gpt-4o-mini", "target_fn": generate_title, "experiment_prefix": "ab-gpt-4o-mini"},
    {"model": "gpt-4o", "target_fn": generate_title_gpt4o, "experiment_prefix": "ab-gpt-4o"},
]


def main():
    client = Client()
    rows = []

    for config in CONFIGURATIONS:
        print(f"\n=== Running {config['model']} ===")
        results = client.evaluate(
            config["target_fn"],
            data=DATASET_NAME,
            evaluators=[correctness_evaluator],
            experiment_prefix=config["experiment_prefix"],
            max_concurrency=MAX_CONCURRENCY,
        )

        pending = []
        for r in results:
            run = r["run"]
            example = r["example"]
            eval_results = r["evaluation_results"]["results"]
            correctness = next((er.score for er in eval_results if er.key == "correctness"), None)

            pending.append({
                "model": config["model"],
                "run_id": run.id,
                "example_id": str(example.id),
                "primary_tag": example.metadata.get("primary_tag"),
                "reference_title": example.outputs["title"],
                "generated_title": run.outputs.get("title", "") if run.outputs else "",
                "correctness_score": correctness,
            })

        # The client-side RunTree from evaluate() doesn't carry server-computed
        # cost/token/latency - re-fetch each run from the API once ingested,
        # with a small delay per call to stay under the API's rate limit.
        print("Waiting for run ingestion before fetching cost/token/latency...")
        time.sleep(5)
        for row in pending:
            run_id = row.pop("run_id")
            for attempt in range(5):
                try:
                    full_run = client.read_run(run_id)
                    break
                except Exception:
                    time.sleep(3)
            else:
                full_run = None
            row["total_tokens"] = full_run.total_tokens if full_run else None
            row["total_cost"] = float(full_run.total_cost) if full_run and full_run.total_cost is not None else None
            row["latency_seconds"] = full_run.latency if full_run else None
            row["error"] = full_run.error if full_run else None
            rows.append(row)
            time.sleep(0.5)

        # Save incrementally so a failure on one config doesn't lose the other's data.
        with open(OUTPUT_PATH, "w") as f:
            json.dump(rows, f, indent=2)
        print(f"Saved {len(rows)} rows so far to {OUTPUT_PATH}")

    print(f"\nWrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
