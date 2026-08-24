import os
from dotenv import load_dotenv
from langsmith import Client
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

# LangSmith tracing configuration — explicit so it's clear what's required,
# even though these can also live in .env
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ.setdefault("LANGCHAIN_ENDPOINT", "https://eu.api.smith.langchain.com")

PROJECT_NAME = "school-orders-extraction-eval"
os.environ["LANGCHAIN_PROJECT"] = PROJECT_NAME

langsmith_client = Client()
openai_client = wrap_openai(OpenAI())

print("LangSmith connected:", langsmith_client)

# Verification: a tiny traced call, so a successful run confirms tracing
# end-to-end, not just that the client object was created.
verification_response = openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Reply with the single word: ok"}],
    max_tokens=5,
)
print("Tracing verification call succeeded:", verification_response.choices[0].message.content)
print(f"Check the LangSmith UI under project '{PROJECT_NAME}' — this call should appear as a trace.")