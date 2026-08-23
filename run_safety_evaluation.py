from pathlib import Path

import pandas as pd

from config import langsmith_client
from optimization_targets import target_gpt4_1
from evaluators import (
    label_accuracy_evaluator,
    correctness_evaluator,
    decision_safety_evaluator,
)


# ---------------------------------------------------------
# Configuration


DATASET_NAME = "clinical-trial-eligibility-curated-v1"

EXPERIMENT_PREFIX = "gpt-4.1-decision-safety"

BASE_DIR = Path(__file__).resolve().parent

RESULTS_FILE = (
    BASE_DIR
    / "results"
    / "decision_safety_results.csv"
)


# ---------------------------------------------------------
# Main


def main():

    print("Starting decision-safety evaluation.")
    print("Target model: gpt-4.1")
    print(f"Dataset: {DATASET_NAME}")

    experiment_results = langsmith_client.evaluate(
        target_gpt4_1,
        data=DATASET_NAME,
        evaluators=[
            label_accuracy_evaluator,
            correctness_evaluator,
            decision_safety_evaluator,
        ],
        experiment_prefix=EXPERIMENT_PREFIX,
        description=(
            "Evaluation of gpt-4.1 clinical-trial eligibility "
            "outputs across label accuracy, correctness, and "
            "decision safety."
        ),
        max_concurrency=2,
        blocking=True,
        metadata={
            "target_model": "gpt-4.1",
            "custom_evaluator": "decision_safety",
            "dataset_version": "v1",
        },
    )

    records = []

    for result in experiment_results:

        example = result["example"]
        run = result["run"]

        metadata = example.metadata or {}

        evaluation_results = (
            result["evaluation_results"]["results"]
        )

        scores = {}
        comments = {}

        for evaluation in evaluation_results:

            scores[evaluation.key] = evaluation.score

            comments[
                f"{evaluation.key}_comment"
            ] = evaluation.comment

        records.append(
            {
                "case_id": metadata.get("case_id"),
                "category": metadata.get("category"),
                "difficulty": metadata.get("difficulty"),

                "label_accuracy": scores.get(
                    "label_accuracy"
                ),

                "correctness": scores.get(
                    "correctness"
                ),

                "decision_safety": scores.get(
                    "decision_safety"
                ),

                "correctness_comment": comments.get(
                    "correctness_comment"
                ),

                "decision_safety_comment": comments.get(
                    "decision_safety_comment"
                ),

                "run_id": str(run.id),
            }
        )

    if len(records) != 15:
        raise ValueError(
            f"Expected 15 results, received {len(records)}."
        )

    df = pd.DataFrame(records)

    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = df.sort_values("case_id")

    df.to_csv(
        RESULTS_FILE,
        index=False,
    )

    # -----------------------------------------------------
    # Simple comparison
    

    correctness_rate = df[
        "correctness"
    ].mean()


    if df["decision_safety"].isna().any():
        failed_cases = df.loc[
            df["decision_safety"].isna(),
            "case_id",
        ].tolist()

        raise ValueError(
            "Decision-safety evaluator failed for: "
            + ", ".join(failed_cases)
        )

    safety_rate = df[
        "decision_safety"
    ].mean()

    disagreements = df[
        df["correctness"]
        != df["decision_safety"]
    ]

    print("\nEvaluation completed.")

    print(
        f"Correctness pass rate: "
        f"{correctness_rate:.1%}"
    )

    print(
        f"Decision-safety pass rate: "
        f"{safety_rate:.1%}"
    )

    print(
        f"Correctness/safety disagreements: "
        f"{len(disagreements)}"
    )

    if not disagreements.empty:

        print("\nCases where the evaluators disagree:")

        print(
            disagreements[
                [
                    "case_id",
                    "label_accuracy",
                    "correctness",
                    "decision_safety",
                ]
            ].to_string(index=False)
        )

    print(
        f"\nResults saved to: {RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()