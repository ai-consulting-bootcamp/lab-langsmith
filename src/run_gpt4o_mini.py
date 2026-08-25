"""Run the GPT-4o mini baseline for the Intellectus evaluation.

The existing GPT-5.4 mini and GPT-5.4 experiments are intentionally reused.
This script runs only the additional low-cost baseline so the three-model
comparison does not duplicate API spend.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_EVALUATION = PROJECT_ROOT / "src" / "run_evaluation.py"
TARGET_MODEL = "gpt-4o-mini"


def main() -> None:
    if not RUN_EVALUATION.exists():
        raise FileNotFoundError(f"Evaluation runner not found: {RUN_EVALUATION}")

    env = os.environ.copy()
    env["TARGET_MODEL"] = TARGET_MODEL

    print("=" * 72)
    print(f"Running Intellectus evaluation with TARGET_MODEL={TARGET_MODEL}")
    print("=" * 72)

    subprocess.run(
        [sys.executable, str(RUN_EVALUATION)],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )

    print()
    print("GPT-4o mini baseline completed.")
    print(
        "Compare this session in LangSmith with the existing "
        "gpt-5.4-mini and gpt-5.4 experiments."
    )


if __name__ == "__main__":
    main()
