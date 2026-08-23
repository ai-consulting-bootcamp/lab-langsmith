import json
import os
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

DATASET_NAME = "should-cost-contract-extraction"

with open("dataset_examples.json", encoding="utf-8") as f:
    examples = json.load(f)

# Check for existing dataset before creating a new one, per lab guidance
existing = list(client.list_datasets(dataset_name=DATASET_NAME))
if existing:
    dataset = existing[0]
    print(f"Using existing dataset: {dataset.id}")
else:
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=(
            "Real U.S. federal defense-vehicle procurement contract awards "
            "(USAspending.gov, NAICS 336350/336330/336310/336399) reshaped "
            "into structured field-extraction examples: extract vendor name, "
            "award amount, and award ID from a natural-language contract notice."
        )
    )
    print(f"Created new dataset: {dataset.id}")

client.create_examples(
    inputs=[ex["input"] for ex in examples],
    outputs=[ex["output"] for ex in examples],
    metadata=[ex["metadata"] for ex in examples],
    dataset_id=dataset.id
)

print(f"Uploaded {len(examples)} examples to dataset '{DATASET_NAME}'")
print(f"View at: https://smith.langchain.com/o/-/datasets/{dataset.id}")