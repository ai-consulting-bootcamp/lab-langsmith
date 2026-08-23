import os
from langsmith import Client
from dotenv import load_dotenv

from target_function import target_function
from evaluator import correctness_evaluator

load_dotenv()

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

DATASET_NAME = "should-cost-contract-extraction"

results = client.evaluate(
    target_function,
    data=DATASET_NAME,
    evaluators=[correctness_evaluator],
    experiment_prefix="gpt-4o-mini-extraction",
    max_concurrency=3,
    metadata={
        "model": "gpt-4o-mini",
        "task": "contract field extraction",
        "temperature": 0
    }
)

print("Evaluation complete.")
print(f"Experiment: {results.experiment_name}")