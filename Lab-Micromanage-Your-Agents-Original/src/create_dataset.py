import json

from dotenv import load_dotenv
from langsmith import Client

# Load API keys and LangSmith configuration from .env
load_dotenv()

# Connect to LangSmith
client = Client()

# Name of our evaluation dataset
dataset_name = "TenderAI-Requirement-Evaluation-v1"

# Check whether this dataset already exists
existing_datasets = list(
    client.list_datasets(dataset_name=dataset_name)
)

if existing_datasets:
    dataset = existing_datasets[0]
    print("Dataset already exists.")
    print("Dataset name:", dataset.name)
    print("Dataset ID:", dataset.id)
else:
    # Load our local dataset
    with open(
        "data/tender_evaluation_dataset.json",
        "r",
        encoding="utf-8",
    ) as file:
        examples = json.load(file)

    # Create the LangSmith dataset
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=(
            "Synthetic evaluation dataset for TenderAI. "
            "Each example tests whether an AI system can correctly "
            "classify tender requirements as SUPPORTED, "
            "PARTIALLY_SUPPORTED, or INSUFFICIENT."
        ),
    )

    # Upload examples
    for example in examples:
        client.create_example(
            inputs={
                "requirement": example["requirement"]
            },
            outputs={
                "expected_classification": (
                    example["expected_classification"]
                )
            },
            dataset_id=dataset.id,
            metadata={
                "requirement_id": example["id"],
                "category": example["category"],
                "difficulty": example["difficulty"],
            },
        )

    print("Dataset created successfully.")
    print("Examples uploaded:", len(examples))
    print("Dataset name:", dataset.name)
    print("Dataset ID:", dataset.id)