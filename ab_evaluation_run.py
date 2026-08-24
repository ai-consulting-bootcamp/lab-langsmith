"""
Cost/performance A/B comparison: runs the coaching target function with
two different models (gpt-4o-mini vs gpt-4o) against the same 15-example
dataset, scored by the same two evaluators (correctness + warmth).

Produces two separate experiments in the LangSmith UI, viewable
side-by-side, with token usage and cost already tracked per example by
LangSmith — no extra cost-tracking code needed.
"""

from dotenv import load_dotenv
from langsmith import Client

from target_function_comparaison import coach_target_mini, coach_target_gpt4o
from evaluator import coaching_correctness_evaluator
from warmth_evaluator import warmth_evaluator

load_dotenv()

DATASET_NAME = "coaching-eval-dataset"
EVALUATORS = [coaching_correctness_evaluator, warmth_evaluator]

if __name__ == "__main__":
    client = Client()

    print("Running gpt-4o-mini...")
    mini_results = client.evaluate(
        coach_target_mini,
        data=DATASET_NAME,
        evaluators=EVALUATORS,
        experiment_prefix="coach-gpt4o-mini-ab",
        max_concurrency=2,
    )
    print("gpt-4o-mini run complete.\n")

    print("Running gpt-4o...")
    gpt4o_results = client.evaluate(
        coach_target_gpt4o,
        data=DATASET_NAME,
        evaluators=EVALUATORS,
        experiment_prefix="coach-gpt4o-ab",
        max_concurrency=2,
    )
    print("gpt-4o run complete.\n")

    print("Both experiments complete — compare them side-by-side in the LangSmith UI:")
    print(f"{client._host_url}/datasets")