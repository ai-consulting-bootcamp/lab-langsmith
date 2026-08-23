import json
from pathlib import Path

from config import langsmith_client


# ---------------------------------------------------------
# Configuration


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "curated_examples.json"
)

DATASET_NAME = "clinical-trial-eligibility-curated-v1"

DATASET_DESCRIPTION = (
    "15 curated clinical-trial eligibility screening examples "
    "derived from the NCBI TrialGPT Criterion Annotations dataset. "
    "Examples include clear inclusion/exclusion cases, missing "
    "information, ambiguous evidence, multiple criteria, temporal "
    "reasoning, boundary values, medical terminology, mixed evidence, "
    "and not-applicable cases."
)


# ---------------------------------------------------------
# Load local examples


def load_examples() -> list[dict]:
    """Load the curated local JSON dataset."""

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        examples = json.load(file)

    if len(examples) != 15:
        raise ValueError(
            f"Expected 15 curated examples, found {len(examples)}."
        )

    return examples


# ---------------------------------------------------------
# Find existing LangSmith dataset


def get_existing_dataset():
    """
    Return the dataset if it already exists,
    otherwise return None.
    """

    datasets = list(
        langsmith_client.list_datasets(
            dataset_name=DATASET_NAME
        )
    )

    if not datasets:
        return None

    return datasets[0]


# ---------------------------------------------------------
# Prepare examples for LangSmith


def prepare_langsmith_examples(
    local_examples: list[dict],
) -> list[dict]:
    """
    Convert our local JSON structure into LangSmith examples.
    """

    langsmith_examples = []

    for example in local_examples:

        metadata = {
            **example["metadata"],
            "case_id": example["id"],
        }

        langsmith_examples.append(
            {
                "inputs": example["inputs"],
                "outputs": example["outputs"],
                "metadata": metadata,
            }
        )

    return langsmith_examples


# ---------------------------------------------------------
# Main


def main():

    print("Loading curated examples...")

    local_examples = load_examples()

    print(
        f"Loaded {len(local_examples)} local examples."
    )

    # Check whether dataset already exists
    dataset = get_existing_dataset()

    if dataset is None:

        print(
            f"\nCreating LangSmith dataset: "
            f"{DATASET_NAME}"
        )

        dataset = langsmith_client.create_dataset(
            dataset_name=DATASET_NAME,
            description=DATASET_DESCRIPTION,
        )

        print(
            f"Dataset created with ID: {dataset.id}"
        )

    else:

        print(
            f"\nDataset already exists: "
            f"{DATASET_NAME}"
        )

        print(
            f"Dataset ID: {dataset.id}"
        )

    # Check existing examples before uploading
    existing_examples = list(
        langsmith_client.list_examples(
            dataset_id=dataset.id
        )
    )

    if len(existing_examples) == 15:

        print(
            "\nDataset already contains 15 examples."
        )

        print(
            "No upload performed to avoid duplicates."
        )

    elif len(existing_examples) > 0:

        raise ValueError(
            f"Dataset already contains "
            f"{len(existing_examples)} examples. "
            "Stopping to avoid creating a mixed "
            "or duplicated dataset."
        )

    else:

        print("\nUploading examples...")

        langsmith_examples = (
            prepare_langsmith_examples(
                local_examples
            )
        )

        langsmith_client.create_examples(
            dataset_id=dataset.id,
            examples=langsmith_examples,
        )

        print(
            f"Uploaded "
            f"{len(langsmith_examples)} examples."
        )

    # -----------------------------------------------------
    # Final verification
   

    uploaded_examples = list(
        langsmith_client.list_examples(
            dataset_id=dataset.id
        )
    )

    print(
        f"\nExamples currently in LangSmith: "
        f"{len(uploaded_examples)}"
    )

    if len(uploaded_examples) != 15:
        raise ValueError(
            "LangSmith dataset does not contain "
            "exactly 15 examples."
        )

    print("\nDataset verification successful.")
    print(f"Dataset name: {dataset.name}")
    print(f"Dataset ID: {dataset.id}")


if __name__ == "__main__":
    main()



'''
Loaded 15 local examples.

Creating LangSmith dataset: clinical-trial-eligibility-curated-v1
Dataset created with ID: 4444cbaf-f232-4c07-a4de-d0a4c1c4bad5

Uploading examples...
Uploaded 15 examples.

Examples currently in LangSmith: 15

Dataset verification successful.
Dataset name: clinical-trial-eligibility-curated-v1
Dataset ID: 4444cbaf-f232-4c07-a4de-d0a4c1c4bad5
'''