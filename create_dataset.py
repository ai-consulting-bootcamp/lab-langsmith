"""Upload the AML Q&A examples to LangSmith as a dataset."""
import json
from dotenv import load_dotenv
load_dotenv()

from langsmith import Client

client = Client()
DATASET_NAME = "aml-compliance-qa-v1"

with open("data/examples.json") as f:
    raw = json.load(f)

# Flatten in case the file is nested ([[...]])
examples = []
def collect(x):
    if isinstance(x, list):
        for item in x:
            collect(item)
    elif isinstance(x, dict):
        examples.append(x)
collect(raw)
print(f"Loaded {len(examples)} examples from file")

if client.has_dataset(dataset_name=DATASET_NAME):
    dataset = client.read_dataset(dataset_name=DATASET_NAME)
else:
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="EU AML compliance questions (AMLD4/5, AMLR, FATF) with article-referenced reference answers.",
    )

existing = len(list(client.list_examples(dataset_id=dataset.id)))
if existing == 0:
    client.create_examples(
        dataset_id=dataset.id,
        inputs=[e["inputs"] for e in examples],
        outputs=[e["outputs"] for e in examples],
        metadata=[e.get("metadata", {}) for e in examples],
    )
    print("Uploaded examples.")
else:
    print(f"Dataset already has {existing} examples, skipping upload.")

count = len(list(client.list_examples(dataset_id=dataset.id)))
print(f"{count} examples in dataset (expected {len(examples)})")