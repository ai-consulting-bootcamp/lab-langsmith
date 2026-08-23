import os
import sys
from dotenv import load_dotenv
from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI


def initialize_langsmith():
    """Load environment variables, configure LangSmith, and return initialized clients."""
    # 1. Load environment variables from .env file
    load_dotenv()

    # Validate essential keys
    if not os.getenv("LANGSMITH_API_KEY"):
        print("[X] Error: LANGSMITH_API_KEY is missing from your .env file.")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print("[X] Error: OPENAI_API_KEY is missing from your .env file.")
        sys.exit(1)

    # 2. Set environment defaults if not set in .env
    os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
    project_name = os.getenv("LANGSMITH_PROJECT", "content-creation-eval")
    os.environ["LANGSMITH_PROJECT"] = project_name

    print(f"[+] Initializing LangSmith Client for project: '{project_name}'...")

    # 3. Initialize LangSmith client and wrapped OpenAI client
    client = Client()
    openai_client = wrap_openai(OpenAI())

    return client, openai_client


@traceable(name="verify_langsmith_connection")
def verify_connection(openai_client):
    """Run a test traceable completion to verify LangSmith connection."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a setup verification assistant."},
            {"role": "user", "content": "Respond with 'LangSmith system operational!'"},
        ],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()


def main():
    client, openai_client = initialize_langsmith()

    print("[+] Executing verification run...")
    result = verify_connection(openai_client)

    print(f"[✓] Output: {result}")
    print(f"[✓] Connection successful! Trace logged under project '{os.getenv('LANGSMITH_PROJECT')}'.")


if __name__ == "__main__":
    main()