"""Run the traced LangSmith experiment and export its result table.

Required local environment variables:
    LANGSMITH_API_KEY
    OPENAI_API_KEY

The target uses the OpenAI Responses API. LangSmith's OpenAI wrapper and the
@traceable decorator capture the model call and the surrounding application run.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langsmith import Client, traceable, wrappers
from openai import OpenAI
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ALLOWED_STRATEGIES = {"HUMAN", "AUTOMATED", "HYBRID"}
DEFAULT_DATASET_NAME = "llm-evaluation-strategy-selection-v1"

load_dotenv(ROOT / ".env")

TARGET_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
JUDGE_MODEL = os.getenv("OPENAI_JUDGE_MODEL", "o3-mini")
DATASET_NAME = os.getenv("LANGSMITH_DATASET_NAME", DEFAULT_DATASET_NAME)
EXPERIMENT_PREFIX = os.getenv(
    "LANGSMITH_EXPERIMENT_PREFIX", "strategy-selection-gpt5-mini"
)
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "2"))

SYSTEM_INSTRUCTIONS = """You are an AI evaluation consultant.
Choose exactly one evaluation strategy for the supplied scenario:
- HUMAN: expert or user judgment is the primary reliable method.
- AUTOMATED: deterministic or scalable automated checks are sufficient for the stated goal.
- HYBRID: automated coverage and human judgment are both materially necessary.

Return exactly two lines:
STRATEGY: HUMAN | AUTOMATED | HYBRID
RATIONALE: one concise sentence of no more than 45 words.
Do not add headings, bullets, caveats, or a second recommendation."""


def require_keys() -> None:
    missing = [
        name
        for name in ("LANGSMITH_API_KEY", "OPENAI_API_KEY")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Copy .env.example to .env and add the keys locally."
        )


def parse_model_output(text: str) -> dict[str, str]:
    """Parse the constrained two-line model response without hiding failures."""
    strategy = ""
    rationale = ""
    for line in text.splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            continue
        if key.strip().upper() == "STRATEGY":
            strategy = value.strip().upper()
        elif key.strip().upper() == "RATIONALE":
            rationale = value.strip()
    return {"strategy": strategy, "rationale": rationale, "raw_output": text.strip()}


def make_target(openai_client):
    @traceable(name="Select Evaluation Strategy", run_type="chain")
    def target(inputs: dict) -> dict:
        prompt = (
            f"Case ID: {inputs['case_id']}\n"
            f"Scenario: {inputs['scenario']}\n"
            f"Constraints: {inputs['constraints']}"
        )
        response = openai_client.responses.create(
            model=TARGET_MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=prompt,
        )
        return parse_model_output(response.output_text)

    return target


def strategy_exact_match(outputs: dict, reference_outputs: dict) -> dict:
    """Deterministically compare the predicted strategy with the gold label."""
    return {
        "key": "strategy_exact_match",
        "score": outputs.get("strategy") == reference_outputs.get("strategy"),
    }


def format_compliance(outputs: dict) -> dict:
    """Check the enum and the lab's one-sentence, 45-word rationale contract."""
    strategy = outputs.get("strategy", "")
    rationale = outputs.get("rationale", "").strip()
    word_count = len(rationale.split())
    valid = strategy in ALLOWED_STRATEGIES and 1 <= word_count <= 45
    return {"key": "format_compliance", "score": valid}


def make_correctness_evaluator():
    judge = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        model=f"openai:{JUDGE_MODEL}",
        feedback_key="semantic_correctness",
    )

    def semantic_correctness(
        inputs: dict, outputs: dict, reference_outputs: dict
    ) -> dict:
        return judge(
            inputs=inputs,
            outputs=outputs,
            reference_outputs=reference_outputs,
        )

    return semantic_correctness


def main() -> None:
    require_keys()
    openai_client = wrappers.wrap_openai(OpenAI())
    langsmith_client = Client()
    target = make_target(openai_client)

    experiment = langsmith_client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[
            strategy_exact_match,
            format_compliance,
            make_correctness_evaluator(),
        ],
        experiment_prefix=EXPERIMENT_PREFIX,
        max_concurrency=MAX_CONCURRENCY,
    )
    experiment.wait()

    frame: pd.DataFrame = experiment.to_pandas()
    result_path = DATA_DIR / "langsmith_evaluation_results_raw.csv"
    frame.to_csv(result_path, index=False)

    metadata = {
        "experiment_name": experiment.experiment_name,
        "experiment_id": str(experiment.experiment_id),
        "experiment_url": experiment.url,
        "dataset_name": DATASET_NAME,
        "target_model": TARGET_MODEL,
        "judge_model": JUDGE_MODEL,
        "result_rows": len(frame),
    }
    (DATA_DIR / "langsmith_run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()

