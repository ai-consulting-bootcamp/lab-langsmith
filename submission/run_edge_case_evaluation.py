import os
from langsmith import Client
from dotenv import load_dotenv

from target_function import target_function
from evaluator import correctness_evaluator
from custom_evaluator import format_compliance_evaluator

load_dotenv()

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

EDGE_CASE_DATASET_NAME = "should-cost-contract-extraction-edge-cases"

results = client.evaluate(
    target_function,
    data=EDGE_CASE_DATASET_NAME,
    evaluators=[correctness_evaluator, format_compliance_evaluator],
    experiment_prefix="gpt-4o-mini-edge-cases",
    max_concurrency=3,
    metadata={
        "model": "gpt-4o-mini",
        "task": "contract field extraction - edge cases",
        "temperature": 0
    }
)

print("Edge case evaluation complete.")
print(f"Experiment: {results.experiment_name}")