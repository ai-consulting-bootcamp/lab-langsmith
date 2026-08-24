from dotenv import load_dotenv
from langsmith import Client

from target_function import target_function
from evaluator import correctness_evaluator

load_dotenv()

client = Client()

DATASET_NAME = "TenderAI-Requirement-Evaluation-v1"

print("Starting LangSmith evaluation...")

results = client.evaluate(
    target_function,
    data=DATASET_NAME,
    evaluators=[correctness_evaluator],
    experiment_prefix="TenderAI-gpt-4.1-mini",
    max_concurrency=2,
)

print("\nEvaluation completed.")
print(results)