import os
import json
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

# Wrap the OpenAI client so every call is automatically traced to LangSmith
client = wrap_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))

MODEL = "gpt-4o-mini"

EXTRACTION_SYSTEM_PROMPT = """You are a procurement data extraction assistant.
Given a contract notice, extract the following fields:
- vendor_name: the company or organization that received the contract
- award_amount: the dollar amount of the award, as a number (no $ sign, no commas)
- award_id: the contract/award identifier

Respond ONLY with valid JSON in this exact format, no other text:
{
  "vendor_name": "<string>",
  "award_amount": <number>,
  "award_id": "<string>"
}
"""

@traceable(name="extract_contract_fields")
def target_function(inputs: dict) -> dict:
    """Extracts structured procurement fields from a natural-language 
    contract notice. Accepts a dict with 'contract_notice', returns a dict 
    with vendor_name, award_amount, award_id."""
    
    contract_notice = inputs["contract_notice"]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": contract_notice}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        result = {"vendor_name": None, "award_amount": None, "award_id": None}

    return result


def make_target_function(model: str):
    """Factory that returns a target function bound to a specific model, 
    so the same extraction logic can be A/B tested across models without 
    duplicating code."""

    @traceable(name=f"extract_contract_fields_{model}")
    def _target_function(inputs: dict) -> dict:
        contract_notice = inputs["contract_notice"]
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": contract_notice}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"vendor_name": None, "award_amount": None, "award_id": None}

    return _target_function


if __name__ == "__main__":
    # Quick sanity check on 2-3 examples before running the full evaluation
    test_input = {
        "contract_notice": "Contract W56HZV20C0124 awarded to RENK AMERICA LLC by Department of Defense for $902,580,413.82. Description: UCA HARDWARE THOR III HMPT XMS AND ANCILLARY HARDWARE"
    }
    result = target_function(test_input)
    print(json.dumps(result, indent=2))