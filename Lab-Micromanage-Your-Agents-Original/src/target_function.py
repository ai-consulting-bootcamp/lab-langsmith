from dotenv import load_dotenv
from langsmith import traceable
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


@traceable
def target_function(inputs: dict) -> dict:
    """
    Classifies a TenderAI requirement.

    Input:
        {"requirement": "..."}

    Output:
        {"classification": "..."}
    """

    requirement = inputs["requirement"]

    prompt = f"""
You are a tender evaluation assistant.

Classify the following tender requirement into exactly ONE category:

SUPPORTED
PARTIALLY_SUPPORTED
INSUFFICIENT

Requirement:
{requirement}

Return ONLY the classification.
"""

    response = model.invoke(prompt)

    classification = response.content.strip()

    return {
        "classification": classification
    }


if __name__ == "__main__":
    test_inputs = [
        {
            "requirement": "The company must demonstrate experience delivering commercial nuclear reactors."
        },
        {
            "requirement": "The company must demonstrate experience delivering an offshore wind project above 100 MW."
        },
        {
            "requirement": "The company must demonstrate the ability to prepare structured tender responses."
        }
    ]

    for inputs in test_inputs:
        result = target_function(inputs)

        print("\nRequirement:")
        print(inputs["requirement"])

        print("Result:")
        print(result)