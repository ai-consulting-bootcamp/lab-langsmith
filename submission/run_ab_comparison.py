import os
import time
from langsmith import Client
from dotenv import load_dotenv

from target_function import make_target_function
from evaluator import correctness_evaluator

load_dotenv()

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

DATASET_NAME = "should-cost-contract-extraction"

MODELS_TO_COMPARE = ["gpt-4o-mini", "gpt-4o"]

# Rough per-1M-token pricing for cost estimation (input/output, USD)
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00}
}

summary = []

for model in MODELS_TO_COMPARE:
    print(f"\nRunning evaluation for {model}...")
    fn = make_target_function(model)
    start = time.time()

    results = client.evaluate(
        fn,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator],
        experiment_prefix=f"ab-compare-{model}",
        max_concurrency=3,
        metadata={"model": model, "task": "contract field extraction - A/B"}
    )
    elapsed = time.time() - start

    summary.append({
        "model": model,
        "experiment_name": results.experiment_name,
        "wall_time_sec": round(elapsed, 2),
        "pricing_per_1m_input": PRICING[model]["input"],
        "pricing_per_1m_output": PRICING[model]["output"]
    })

print("\n" + "=" * 50)
for row in summary:
    print(row)