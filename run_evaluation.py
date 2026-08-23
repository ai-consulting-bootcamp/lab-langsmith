from pathlib import Path

import pandas as pd

from config import langsmith_client
from target import screen_patient, TARGET_MODEL
from evaluators import (
    label_accuracy_evaluator,
    correctness_evaluator,
    JUDGE_MODEL,
)


# ---------------------------------------------------------
# Experiment configuration


DATASET_NAME = "clinical-trial-eligibility-curated-v1"

EXPERIMENT_PREFIX = "clinical-trial-gpt-4o-mini-v1"

MAX_CONCURRENCY = 2

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_FILE = RESULTS_DIR / "evaluation_results.csv"


# ---------------------------------------------------------
# Run experiment


def main():

    print("Starting LangSmith evaluation.")
    print(f"Dataset: {DATASET_NAME}")
    print(f"Target model: {TARGET_MODEL}")
    print(f"Judge model: {JUDGE_MODEL}")
    print(f"Concurrency: {MAX_CONCURRENCY}")

    experiment_results = langsmith_client.evaluate(
        screen_patient,
        data=DATASET_NAME,
        evaluators=[
            label_accuracy_evaluator,
            correctness_evaluator,
        ],
        experiment_prefix=EXPERIMENT_PREFIX,
        description=(
            "Baseline evaluation of gpt-4o-mini for clinical "
            "trial eligibility screening using 15 curated "
            "TrialGPT examples."
        ),
        max_concurrency=MAX_CONCURRENCY,
        blocking=True,
        metadata={
            "models": [
                f"openai:{TARGET_MODEL}",
                JUDGE_MODEL,
            ],
            "target_model": TARGET_MODEL,
            "judge_model": JUDGE_MODEL,
            "dataset_version": "v1",
        },
    )

    print("\nExperiment completed.")

    # -----------------------------------------------------
    # Collect local results
   

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
                "number_of_criteria": metadata.get(
                    "number_of_criteria"
                ),
                "label_accuracy": scores.get(
                    "label_accuracy"
                ),
                "correctness": scores.get(
                    "correctness"
                ),
                "label_accuracy_comment": comments.get(
                    "label_accuracy_comment"
                ),
                "correctness_comment": comments.get(
                    "correctness_comment"
                ),
                "run_id": str(run.id),
            }
        )

    # -----------------------------------------------------
    # Verify all examples were processed
    

    if len(records) != 15:
        raise ValueError(
            f"Expected 15 evaluation results, "
            f"but received {len(records)}."
        )

    # -----------------------------------------------------
    # Save local results
   

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df = pd.DataFrame(records)

    results_df = results_df.sort_values(
        "case_id"
    )

    results_df.to_csv(
        RESULTS_FILE,
        index=False,
    )

    print(
        f"\nProcessed examples: {len(results_df)}"
    )

    print(
        f"Results saved to: {RESULTS_FILE}"
    )

    # -----------------------------------------------------
    # Small terminal summary
   

    print("\nScores:")

    print(
        results_df[
            [
                "case_id",
                "label_accuracy",
                "correctness",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()




'''
Starting LangSmith evaluation.
Dataset: clinical-trial-eligibility-curated-v1
Target model: gpt-4o-mini
Judge model: openai:gpt-4.1-mini
Concurrency: 2
View the evaluation results for experiment: 'clinical-trial-gpt-4o-mini-v1-1203d85e' at:
https://eu.smith.langchain.com/o/42775d6e-5dc7-4c51-ab8f-2ebf50f55e89/datasets/4444cbaf-f232-4c07-a4de-d0a4c1c4bad5/compare?selectedSessions=b6b1d295-92c3-4e15-8c85-52eec06a7189


15it [00:34,  2.29s/it]

Experiment completed.

Processed examples: 15
Results saved to: /Users/nevena/Ironhack_Labs/week7/lab-langsmith/results/evaluation_results.csv

Scores:
                    case_id  label_accuracy  correctness
    case_01_clear_inclusion             1.0         True
    case_02_clear_inclusion             1.0         True
    case_03_clear_exclusion             0.0        False
    case_04_clear_exclusion             0.0        False
case_05_missing_information             0.0        False
case_06_missing_information             1.0         True
 case_07_ambiguous_evidence             0.0        False
 case_08_ambiguous_evidence             1.0         True
  case_09_multiple_criteria             0.5        False
  case_10_multiple_criteria             0.6        False
 case_11_temporal_reasoning             0.0        False
     case_12_boundary_value             0.0        False
case_13_medical_terminology             1.0         True
     case_14_mixed_evidence             1.0         True
     case_15_not_applicable             0.0        False
'''