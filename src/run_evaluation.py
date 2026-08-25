"""Run the full Intellectus Operations/CX evaluation in LangSmith.

This script evaluates the LLM target against the custom LangSmith dataset using
semantic correctness, groundedness, and deterministic contract checks.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

from evaluators import EVALUATORS
from target import operations_cx_target


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

DATASET_NAME = "intellectus-operations-cx-evaluation-v1"
EXPERIMENT_PREFIX = "intellectus-operations-cx"

load_dotenv(ENV_FILE, override=True)


def build_experiment_name() -> str:
    """Create a readable experiment label for LangSmith."""
    model = os.getenv("TARGET_MODEL", "gpt-5.4-mini")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    return f"{EXPERIMENT_PREFIX}-{model}-{timestamp}"


def main() -> None:
    client = Client()
    experiment_name = build_experiment_name()

    print(f"Dataset: {DATASET_NAME}")
    print(f"Experiment: {experiment_name}")
    print(f"Target model: {os.getenv('TARGET_MODEL', 'gpt-5.4-mini')}")
    print(f"Judge model: {os.getenv('JUDGE_MODEL', 'gpt-5.4')}")
    print("Evaluators: correctness, groundedness, contract_compliance")
    print()

    results = client.evaluate(
        operations_cx_target,
        data=DATASET_NAME,
        evaluators=EVALUATORS,
        experiment_prefix=experiment_name,
        max_concurrency=2,
    )

    print()
    print("Evaluation completed.")
    print(f"Experiment: {experiment_name}")
    print("Open LangSmith to review aggregate metrics, traces, and failed cases.")

    return results


if __name__ == "__main__":
    main()
