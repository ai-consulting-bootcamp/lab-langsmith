"""
Runs the full evaluation: coach_target against all 15 dataset examples,
scored by coaching_correctness_evaluator. Results appear as an experiment
in the LangSmith UI under the coaching-eval-lab project.

Run this once the dataset (dataset_upload.py), target function, and
evaluator have all been verified individually.
"""

from dotenv import load_dotenv
from langsmith import Client

from target_function import coach_target
from evaluator import coaching_correctness_evaluator

load_dotenv()

DATASET_NAME = "coaching-eval-dataset"

if __name__ == "__main__":
    client = Client()

    results = client.evaluate(
        coach_target,
        data=DATASET_NAME,
        evaluators=[coaching_correctness_evaluator],
        experiment_prefix="coach-gpt4o-mini",
        max_concurrency=2,
    )

    print("Evaluation complete.")
    print(f"View results at: {client._host_url}/datasets")
