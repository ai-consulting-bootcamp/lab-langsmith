"""
Step 4: Create the LangSmith dataset and upload the structured examples
produced by scripts/extract_examples.py (data/blog_title_examples.json).

Usage:
    python3 scripts/create_dataset.py
"""

import json
import os

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

DATASET_NAME = "blog-title-generation-medium-articles"
DATASET_DESCRIPTION = (
    "Blog title generation task: given a ~400-word excerpt of a real Medium article, "
    "generate an engaging, accurate title. Ground truth is the article's actual "
    "published title. 18 examples spanning 14 topics (writing, marketing, productivity, "
    "health, personal essays, etc.), sourced from fabiochiu/medium-articles."
)
EXAMPLES_PATH = "data/blog_title_examples.json"


def main():
    client = Client()

    with open(EXAMPLES_PATH) as f:
        examples = json.load(f)

    existing = {d.name: d for d in client.list_datasets()}

    if DATASET_NAME in existing:
        dataset = existing[DATASET_NAME]
        print(f"Dataset '{DATASET_NAME}' already exists (id={dataset.id}) — skipping creation")
    else:
        dataset = client.create_dataset(DATASET_NAME, description=DATASET_DESCRIPTION)
        print(f"Created dataset '{DATASET_NAME}' (id={dataset.id})")

    current_examples = list(client.list_examples(dataset_id=dataset.id))
    if len(current_examples) >= len(examples):
        print(f"Dataset already has {len(current_examples)} examples — skipping upload")
    else:
        client.create_examples(
            inputs=[ex["inputs"] for ex in examples],
            outputs=[ex["outputs"] for ex in examples],
            metadata=[ex["metadata"] for ex in examples],
            dataset_id=dataset.id,
        )
        print(f"Uploaded {len(examples)} examples")

    # Verification
    uploaded = list(client.list_examples(dataset_id=dataset.id))
    print(f"\nVerification: dataset '{DATASET_NAME}' now contains {len(uploaded)} examples")
    sample = uploaded[0]
    print("Sample example:")
    print("  inputs keys: ", list(sample.inputs.keys()))
    print("  outputs keys:", list(sample.outputs.keys()))
    print("  metadata:    ", sample.metadata)

    ui_host = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com").replace("api.", "")
    print(f"\nDataset id: {dataset.id}")
    print(f"View in LangSmith UI: {ui_host}/datasets/{dataset.id}")


if __name__ == "__main__":
    main()
