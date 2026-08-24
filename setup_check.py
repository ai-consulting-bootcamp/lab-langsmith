from dotenv import load_dotenv
from langsmith import Client
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

langsmith_client = Client()
openai_client = wrap_openai(OpenAI())

# Sanity check: confirm the connection and print what we get back
datasets = list(langsmith_client.list_datasets(limit=1))
print(f"✅ Connected to LangSmith. Found {len(datasets)} existing dataset(s).")
print(f"Project configured: {langsmith_client.info}")