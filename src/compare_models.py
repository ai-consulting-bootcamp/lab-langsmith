"""Run a controlled A/B model comparison for the Intellectus evaluation.

Each model is evaluated in a fresh Python process so model-specific LangSmith
metadata, tracing, and token-cost attribution remain isolated and reproducible.

The comparison intentionally keeps the dataset, prompt, evaluators, and
concurrency unchanged. Only TARGET_MODEL changes between runs.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_EVALUATION = PROJECT_ROOT / "src" / "run_evaluation.py"

MODELS = (
    "gpt-5.4-mini",
    "gpt-5.4",
)


def run_model(model: str) -> None:
    """Run one evaluation experiment with an isolated target-model setting."""
    env = os.environ.copy()
    env["TARGET_MODEL"] = model

    print()
    print("=" * 72)
    print(f"Running Intellectus evaluation with TARGET_MODEL={model}")
    print("=" * 72)

    subprocess.run(
        [sys.executable, str(RUN_EVALUATION)],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )


def main() -> None:
    if not RUN_EVALUATION.exists():
        raise FileNotFoundError(f"Evaluation runner not found: {RUN_EVALUATION}")

    for model in MODELS:
        run_model(model)

    print()
    print("A/B runs completed.")
    print("Open LangSmith → Datasets & Experiments and compare the two new sessions.")
    print(
        "Use target-run token/cost data for model cost comparison; "
        "judge cost is shared evaluation overhead."
    )


if __name__ == "__main__":
    main()
