import os
import json
from dotenv import load_dotenv
from langsmith import Client

def main():
    load_dotenv()
    client = Client()

    dataset_name = "ag-news-content-classification"
    json_path = "data/content_creation_dataset.json"

    if not os.path.exists(json_path):
        print(f"[X] Error: Could not find '{json_path}'.")
        return

    # 1. Load local JSON containing the 'difficulty' field
    with open(json_path, "r", encoding="utf-8") as f:
        local_examples = json.load(f)

    print(f"[+] Loaded {len(local_examples)} examples from '{json_path}'.")

    # 2. Find and delete the existing dataset on LangSmith
    existing_datasets = list(client.list_datasets(dataset_name=dataset_name))
    for ds in existing_datasets:
        print(f"[!] Deleting old dataset on LangSmith (ID: {ds.id})...")
        client.delete_dataset(dataset_id=ds.id)

    # 3. Create fresh dataset container
    print(f"[+] Creating fresh dataset '{dataset_name}' in LangSmith...")
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="AG News 4-category classification benchmark with difficulty metadata."
    )

    # 4. Upload updated inputs, outputs, AND metadata
    client.create_examples(
        inputs=[e["inputs"] for e in local_examples],
        outputs=[e["outputs"] for e in local_examples],
        metadata=[e["metadata"] for e in local_examples],
        dataset_id=dataset.id
    )

    print(f"[✓] Successfully uploaded {len(local_examples)} examples with 'difficulty' metadata to LangSmith!")

if __name__ == "__main__":
    main()