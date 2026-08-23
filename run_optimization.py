from pathlib import Path

import pandas as pd

from config import langsmith_client
from evaluators import (
    label_accuracy_evaluator,
    correctness_evaluator,
)
from optimization_targets import (
    target_gpt4o_mini,
    target_gpt4_1,
)


DATASET_NAME = "clinical-trial-eligibility-curated-v1"

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

MODEL_RUNS = [
    {
        "name": "gpt-4o-mini",
        "target": target_gpt4o_mini,
        "experiment_prefix": "optimization-gpt-4o-mini",
    },
    {
        "name": "gpt-4.1",
        "target": target_gpt4_1,
        "experiment_prefix": "optimization-gpt-4.1",
    },
]


def collect_results(
    experiment_results,
    model_name: str,
) -> pd.DataFrame:

    records = []

    for result in experiment_results:

        example = result["example"]
        run = result["run"]

        example_metadata = example.metadata or {}
        output = run.outputs or {}

        metrics = output.get(
            "_metrics",
            {},
        )

        evaluation_results = (
            result["evaluation_results"]["results"]
        )

        scores = {}

        for evaluation in evaluation_results:
            scores[evaluation.key] = evaluation.score

        records.append(
            {
                "model": model_name,
                "case_id": example_metadata.get("case_id"),
                "category": example_metadata.get("category"),
                "difficulty": example_metadata.get("difficulty"),

                "label_accuracy": scores.get(
                    "label_accuracy"
                ),

                "correctness": scores.get(
                    "correctness"
                ),

                "input_tokens": metrics.get(
                    "input_tokens"
                ),

                "output_tokens": metrics.get(
                    "output_tokens"
                ),

                "total_tokens": metrics.get(
                    "total_tokens"
                ),

                "latency_seconds": metrics.get(
                    "latency_seconds"
                ),

                "estimated_cost_usd": metrics.get(
                    "estimated_cost_usd"
                ),

                "run_id": str(run.id),
            }
        )

    return pd.DataFrame(records)


def main():

    all_results = []

    for config in MODEL_RUNS:

        model_name = config["name"]

        print("\n" + "=" * 70)
        print(f"Running model: {model_name}")
        print("=" * 70)

        experiment_results = langsmith_client.evaluate(
            config["target"],
            data=DATASET_NAME,
            evaluators=[
                label_accuracy_evaluator,
                correctness_evaluator,
            ],
            experiment_prefix=(
                config["experiment_prefix"]
            ),
            description=(
                f"Cost-performance comparison for "
                f"{model_name} on the clinical trial "
                f"eligibility dataset."
            ),
            max_concurrency=2,
            blocking=True,
            metadata={
                "optimization_run": True,
                "target_model": model_name,
                "dataset_version": "v1",
            },
        )

        model_results = collect_results(
            experiment_results,
            model_name,
        )

        if len(model_results) != 15:
            raise ValueError(
                f"{model_name}: expected 15 results, "
                f"received {len(model_results)}."
            )

        all_results.append(
            model_results
        )

        model_file = (
            RESULTS_DIR
            / f"optimization_{model_name}.csv"
        )

        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        model_results.to_csv(
            model_file,
            index=False,
        )

        print(
            f"Saved {model_name} results to: "
            f"{model_file}"
        )

    combined = pd.concat(
        all_results,
        ignore_index=True,
    )

    combined_file = (
        RESULTS_DIR
        / "optimization_results.csv"
    )

    combined.to_csv(
        combined_file,
        index=False,
    )

    print("\n" + "=" * 70)
    print("Both experiments completed.")
    print(
        f"Combined results saved to: "
        f"{combined_file}"
    )


if __name__ == "__main__":
    main()
    