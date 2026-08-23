import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI



# Load environment variables

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)



# Read configuration

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")



# Validate required variables

required_variables = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "LANGSMITH_API_KEY": LANGSMITH_API_KEY,
    "LANGSMITH_ENDPOINT": LANGSMITH_ENDPOINT,
    "LANGSMITH_PROJECT": LANGSMITH_PROJECT,
    "LANGSMITH_TRACING": LANGSMITH_TRACING,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]

if missing_variables:
    raise ValueError(
        "Missing environment variables: "
        + ", ".join(missing_variables)
    )



# Initialize clients

langsmith_client = Client(
    api_key=LANGSMITH_API_KEY,
    api_url=LANGSMITH_ENDPOINT,
)

openai_client = wrap_openai(
    OpenAI(api_key=OPENAI_API_KEY)
)



# Connection / tracing test

@traceable(name="langsmith-connection-test")
def test_tracing() -> str:
    """
    Make a small OpenAI call and trace it in LangSmith.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Answer very briefly.",
            },
            {
                "role": "user",
                "content": (
                    "Reply exactly with: "
                    "LangSmith tracing works"
                ),
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()



# Run test only when config.py is executed directly

if __name__ == "__main__":

    print("Configuration loaded.")
    print(f"LangSmith endpoint: {LANGSMITH_ENDPOINT}")
    print(f"LangSmith project: {LANGSMITH_PROJECT}")
    print(f"Tracing enabled: {LANGSMITH_TRACING}")

    result = test_tracing()

    print(f"\nOpenAI response: {result}")

    # Ensure pending traces are sent before the script exits.
    langsmith_client.flush()

    print("\nConnection test complete.")