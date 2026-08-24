"""Create the custom LangSmith dataset used by this lab.

The script is idempotent: if a dataset with the configured exact name already
contains examples, it reports the existing dataset and does not duplicate rows.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "evaluation_examples.json"
DEFAULT_DATASET_NAME = "llm-evaluation-strategy-selection-v1"
DATASET_DESCRIPTION = (
    "Twelve fictional AI-consulting scenarios for selecting HUMAN, AUTOMATED, "
    "or HYBRID LLM evaluation strategies, with reference rationales and metadata."
)
ALLOWED_STRATEGIES = {"HUMAN", "AUTOMATED", "HYBRID"}


def load_examples() -> list[dict]:
    """Load and validate the local source-of-truth examples."""
    examples = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not 10 <= len(examples) <= 20:
        raise ValueError("The lab dataset must contain between 10 and 20 examples.")

    case_ids: set[str] = set()
    for index, example in enumerate(examples, start=1):
        if set(example) != {"inputs", "outputs", "metadata"}:
            raise ValueError(f"Example {index} must contain inputs, outputs, and metadata.")
        case_id = example["inputs"].get("case_id")
        if not case_id or case_id in case_ids:
            raise ValueError(f"Example {index} has a missing or duplicate case_id.")
        case_ids.add(case_id)
        strategy = example["outputs"].get("strategy")
        if strategy not in ALLOWED_STRATEGIES:
            raise ValueError(f"Example {case_id} has an invalid strategy: {strategy}")
    return examples


def main() -> None:
    load_dotenv(ROOT / ".env")
    dataset_name = os.getenv("LANGSMITH_DATASET_NAME", DEFAULT_DATASET_NAME)
    examples = load_examples()
    client = Client()

    existing = next(client.list_datasets(dataset_name=dataset_name), None)
    if existing is not None:
        existing_examples = list(client.list_examples(dataset_id=existing.id))
        if existing_examples:
            print(
                f"Dataset already exists: {existing.name} "
                f"({len(existing_examples)} examples). No rows were added."
            )
            return
        dataset = existing
    else:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description=DATASET_DESCRIPTION,
        )

    client.create_examples(dataset_id=dataset.id, examples=examples)
    print(f"Created dataset: {dataset.name} ({len(examples)} examples)")


if __name__ == "__main__":
    main()

