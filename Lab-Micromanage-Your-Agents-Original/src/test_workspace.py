import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

workspace_id = os.getenv("LANGSMITH_WORKSPACE_ID")

print("Workspace ID present:", bool(workspace_id))
print("Workspace ID length:", len(workspace_id or ""))

client = Client()

try:
    datasets = list(client.list_datasets(limit=1))
    print("Dataset access: SUCCESS")
    print("Datasets found:", len(datasets))

except Exception as e:
    print("Dataset access: FAILED")
    print(type(e).__name__)
    print(e)