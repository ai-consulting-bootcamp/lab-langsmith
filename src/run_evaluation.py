"""
run_evaluation.py

Runs the LangSmith evaluation experiment for the AG News classification
target function, scored by the exact_match_evaluator.

Usage:
    python src/run_evaluation.py
    python src/run_evaluation.py --prefix my-custom-name
"""

import argparse
import datetime as dt
import os

from dotenv import load_dotenv
from langsmith import Client

from target_functions import target_classifier
from evaluators import exact_match_evaluator
from custom_evaluator import plausibility_evaluator

load_dotenv()

DATASET_NAME = "ag-news-content-classification"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prefix",
        default=None,
        help="Experiment prefix identifying this run. Defaults to 'gpt-4o-mini-<timestamp>'.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=3,
        help="Concurrent requests during evaluation. Start low (2-3) to respect API rate limits.",
    )
    args = parser.parse_args()

    assert os.environ.get("LANGSMITH_API_KEY"), "Set LANGSMITH_API_KEY in your .env"
    assert os.environ.get("OPENAI_API_KEY"), "Set OPENAI_API_KEY in your .env"

    client = Client()

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    prefix = args.prefix or f"gpt-4o-mini-{timestamp}"

    print(f"[+] Running evaluation '{prefix}' on dataset '{DATASET_NAME}'...")
    print(f"[+] Max concurrency: {args.max_concurrency}")

    results = client.evaluate(
        target_classifier,
        data=DATASET_NAME,
        evaluators=[exact_match_evaluator, plausibility_evaluator],
        experiment_prefix=prefix,
        max_concurrency=args.max_concurrency,
        metadata={"model": "gpt-4o-mini", "task": "ag_news_classification"},
    )

    print("\n[OK] Evaluation complete.")
    print("Open LangSmith > Datasets & Experiments > ag-news-content-classification")
    print(f"to view the '{prefix}' experiment, its per-example scores, and traces.")

    return results


if __name__ == "__main__":
    main()
