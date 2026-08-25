"""Create the Intellectus Operations/CX evaluation dataset in LangSmith.

The local JSON file is the source of truth for this lab. This script validates
the file, creates the remote dataset when needed, and uploads the examples in
one batch.

Re-running the script is safe: if the dataset already exists, it reports that
state instead of creating a duplicate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langsmith import Client


DATASET_NAME = "intellectus-operations-cx-evaluation-v1"
DATASET_DESCRIPTION = (
    "Custom evaluation dataset for evidence-grounded Operations/CX analysis. "
    "Cases are derived from the behavioural rules of Intellectus workflow "
    "53_OPERATIONS_CX_AGENT and test classification, grounding, domain "
    "filtering, contradiction handling, validation, and scope control."
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_FILE = PROJECT_ROOT / "data" / "evaluation_examples.json"
ENV_FILE = PROJECT_ROOT / ".env"

REQUIRED_TOP_LEVEL_FIELDS = {"id", "inputs", "outputs", "metadata"}


def load_examples(path: Path = DATASET_FILE) -> list[dict[str, Any]]:
    """Load and validate the local evaluation examples before any API call."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset source not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        examples = json.load(file)

    if not isinstance(examples, list) or not examples:
        raise ValueError("Dataset source must contain a non-empty JSON list.")

    seen_ids: set[str] = set()

    for position, example in enumerate(examples, start=1):
        if not isinstance(example, dict):
            raise ValueError(f"Example {position} must be a JSON object.")

        missing = REQUIRED_TOP_LEVEL_FIELDS - example.keys()
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise ValueError(
                f"Example {position} is missing required fields: {missing_fields}"
            )

        example_id = example["id"]
        if not isinstance(example_id, str) or not example_id.strip():
            raise ValueError(f"Example {position} has an invalid id.")

        if example_id in seen_ids:
            raise ValueError(f"Duplicate example id found: {example_id}")

        seen_ids.add(example_id)

        for field in ("inputs", "outputs", "metadata"):
            if not isinstance(example[field], dict):
                raise ValueError(
                    f"Example {example_id}: '{field}' must be a JSON object."
                )

    return examples


def get_existing_dataset(client: Client):
    """Return the existing dataset when the exact dataset name is already in use."""
    datasets = list(client.list_datasets(dataset_name=DATASET_NAME))
    return datasets[0] if datasets else None


def to_langsmith_example(example: dict[str, Any]) -> dict[str, Any]:
    """Keep local IDs as metadata while using LangSmith's expected example shape."""
    metadata = {
        **example["metadata"],
        "case_id": example["id"],
    }

    return {
        "inputs": example["inputs"],
        "outputs": example["outputs"],
        "metadata": metadata,
    }


def create_dataset(client: Client, examples: list[dict[str, Any]]):
    """Create the dataset and upload all validated examples in one request."""
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=DATASET_DESCRIPTION,
    )

    client.create_examples(
        dataset_id=dataset.id,
        examples=[to_langsmith_example(example) for example in examples],
    )

    return dataset


def main() -> None:
    # Project-local configuration should win over stale shell or Conda values.
    load_dotenv(ENV_FILE, override=True)

    examples = load_examples()
    client = Client()

    existing_dataset = get_existing_dataset(client)
    if existing_dataset:
        remote_examples = list(
            client.list_examples(dataset_id=existing_dataset.id)
        )

        print(f"Dataset already exists: {existing_dataset.name}")
        print(f"Remote examples: {len(remote_examples)}")
        print(f"Local examples:  {len(examples)}")

        if len(remote_examples) != len(examples):
            print(
                "Warning: local and remote example counts differ. "
                "Review the dataset before running evaluations."
            )
        return

    dataset = create_dataset(client, examples)

    print(f"Created dataset: {dataset.name}")
    print(f"Uploaded examples: {len(examples)}")
    print(f"Dataset ID: {dataset.id}")


if __name__ == "__main__":
    main()