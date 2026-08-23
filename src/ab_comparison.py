"""
ab_comparison.py (Optional Part 2, Step 14)

Runs the SAME dataset and SAME evaluators (exact_match_evaluator,
plausibility_evaluator) against multiple models, so the only variable
that changes between runs is the model itself. This keeps the comparison
fair per the lab's requirement.

Usage:
    python src/ab_comparison.py
    python src/ab_comparison.py --models gpt-4o-mini gpt-4o
"""

import argparse
import os

from dotenv import load_dotenv
from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

from evaluators import exact_match_evaluator
from custom_evaluator import plausibility_evaluator

load_dotenv()

DATASET_NAME = "ag-news-content-classification"

# Same system prompt used in target_functions.py -- kept identical here so
# the model is the only variable changing between runs.
SYSTEM_PROMPT = (
    "You are an expert news classifier. Classify the user's text into "
    "exactly one of these categories: World, Sports, Business, Sci/Tech. "
    "Reply ONLY with the exact category name. Do not add any punctuation, "
    "explanation, or extra text."
)

_openai_client = wrap_openai(OpenAI())


def make_target_function(model_name: str):
    """Builds a @traceable target function bound to a specific model,
    keeping everything else (prompt, temperature, max_tokens) identical
    to target_functions.py's target_classifier.
    """

    @traceable(name=f"news-classifier-target-{model_name}")
    def target(inputs: dict) -> dict:
        try:
            response = _openai_client.chat.completions.create(
                model=model_name,
                temperature=0.0,
                max_tokens=10,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": inputs.get("question", "")},
                ],
            )
            predicted_category = response.choices[0].message.content.strip()
            return {"expected_output": predicted_category}
        except Exception as e:  # noqa: BLE001 -- surfaced as a failed run, not a crash
            return {"expected_output": "Error", "error_details": str(e)}

    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gpt-4o-mini", "gpt-4o"],
        help="Models to compare. Default: gpt-4o-mini vs gpt-4o.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=3,
    )
    args = parser.parse_args()

    assert os.environ.get("LANGSMITH_API_KEY"), "Set LANGSMITH_API_KEY in your .env"
    assert os.environ.get("OPENAI_API_KEY"), "Set OPENAI_API_KEY in your .env"

    client = Client()

    print(f"[+] Comparing models: {args.models}")
    print(f"[+] Dataset: {DATASET_NAME}")
    print(f"[+] Evaluators: exact_match_evaluator, plausibility_evaluator (same for all models)\n")

    experiment_names = {}

    for model_name in args.models:
        prefix = f"ab-{model_name}"
        target_fn = make_target_function(model_name)

        print(f"[+] Running evaluation for '{model_name}'...")
        results = client.evaluate(
            target_fn,
            data=DATASET_NAME,
            evaluators=[exact_match_evaluator, plausibility_evaluator],
            experiment_prefix=prefix,
            max_concurrency=args.max_concurrency,
            metadata={"model": model_name, "task": "ag_news_classification", "purpose": "ab_comparison"},
        )
        print(results) # added to print the results of each model evaluation after AI feedback
        experiment_names[model_name] = prefix
        print(f"[OK] '{model_name}' run complete.\n")

    print("=" * 60)
    print("All runs complete. Experiment prefixes created:")
    for model_name, prefix in experiment_names.items():
        print(f"  {model_name:<15} -> {prefix}")
    print("=" * 60)
    print(
        "\nOpen LangSmith > Datasets & Experiments > "
        f"{DATASET_NAME} to compare exact_match, plausibility, latency, "
        "tokens, and cost side-by-side across these experiments (LangSmith "
        "auto-tracks cost per run via the wrapped OpenAI client, no manual "
        "pricing table needed)."
    )


if __name__ == "__main__":
    main()
