"""
Creates (or reuses) the LangSmith dataset for the coaching-eval-lab and
uploads the 15 examples from dataset_examples.py.

Run this once. Re-running is safe: it checks for an existing dataset
with the same name before creating a new one.
"""

from dotenv import load_dotenv
from langsmith import Client

from dataset_examples import EXAMPLES

load_dotenv()

DATASET_NAME = "coaching-eval-dataset"
DATASET_DESCRIPTION = (
    "Coaching-assistant evaluation examples. Each example is one coaching "
    "turn (employee statement/question, optional prior conversation "
    "history) paired with an expected single-question coach response, "
    "modeled on ICF-style reflective coaching (no advice-giving, no "
    "compound questions). Includes single-turn and multi-turn (2-3 turn) "
    "threads across categories: goal-setting, clarity, motivation, "
    "feedback-resistance, perspective."
)


def get_or_create_dataset(client: Client):
    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        print(f"Dataset '{DATASET_NAME}' already exists — reusing it.")
        return existing[0]

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=DATASET_DESCRIPTION,
    )
    print(f"Created dataset '{DATASET_NAME}'.")
    return dataset


def upload_examples(client: Client, dataset_id):
    # Skip upload if the dataset already has examples, to avoid duplicates
    # on re-run.
    existing_examples = list(client.list_examples(dataset_id=dataset_id))
    if existing_examples:
        print(
            f"Dataset already has {len(existing_examples)} example(s) — "
            "skipping upload. Delete them in the UI first if you want to "
            "re-upload."
        )
        return

    client.create_examples(
        inputs=[ex["inputs"] for ex in EXAMPLES],
        outputs=[ex["outputs"] for ex in EXAMPLES],
        metadata=[ex["metadata"] for ex in EXAMPLES],
        dataset_id=dataset_id,
    )
    print(f"Uploaded {len(EXAMPLES)} examples to dataset '{DATASET_NAME}'.")


if __name__ == "__main__":
    client = Client()
    dataset = get_or_create_dataset(client)
    upload_examples(client, dataset.id)
    print(f"Done. View it at: {client._host_url}/datasets")
