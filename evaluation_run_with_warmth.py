"""
Runs the full evaluation: coach_target against all 15 dataset examples,
scored by BOTH coaching_correctness_evaluator (structure/advice-giving)
and warmth_evaluator (tone/empathy). Results appear as one experiment
in the LangSmith UI, with both scores visible per example for comparison.

Run this once the dataset, target function, and both evaluators have
been verified individually.
"""

from dotenv import load_dotenv
from langsmith import Client

from target_function import coach_target
from evaluator import coaching_correctness_evaluator
from warmth_evaluator import warmth_evaluator

load_dotenv()

DATASET_NAME = "coaching-eval-dataset"

if __name__ == "__main__":
    client = Client()

    results = client.evaluate(
        coach_target,
        data=DATASET_NAME,
        evaluators=[coaching_correctness_evaluator, warmth_evaluator],
        experiment_prefix="coach-gpt4o-mini-with-warmth",
        max_concurrency=2,
    )

    print("Evaluation complete.")
    print(f"View results at: {client._host_url}/datasets")
