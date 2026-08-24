import os
from dotenv import load_dotenv
from langsmith import Client

from target import target, target_gpt4o
from evaluator import correctness_evaluator, completeness_evaluator

load_dotenv()

client = Client()

DATASET_NAME = "school-orders-extraction"
evaluators = [correctness_evaluator, completeness_evaluator]

results_mini = client.evaluate(
    target,
    data=DATASET_NAME,
    evaluators=evaluators,
    experiment_prefix="gpt-4o-mini-final",
    max_concurrency=3,
)
print("gpt-4o-mini done:", results_mini)

results_4o = client.evaluate(
    target_gpt4o,
    data=DATASET_NAME,
    evaluators=evaluators,
    experiment_prefix="gpt-4o-final",
    max_concurrency=3,
)
print("gpt-4o done:", results_4o)