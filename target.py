import json
from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

openai_client = wrap_openai(OpenAI())

SYSTEM_PROMPT = """You extract structured school book orders from raw order messages sent to an Indian school book distributor.

Return ONLY valid JSON in this exact shape:
{"items": [{"school": string or null, "class": string, "title": string, "qty": integer or null}]}

Rules:
- If the school name is not mentioned in the message, set "school" to null. Never guess or invent a school name.
- If a quantity is not mentioned for an item, set "qty" to null. Never invent a quantity.
- Keep bundled catalogue-style lines (e.g. "Crown Maths B/R-1, B/R-2, Ruled-5, D/R-1") as a single item with one title, do not split them into separate items.
- Normalize class labels to how they appear in the message (e.g. "6th" stays "6th", "class 3" becomes "CLASS 3").
- Preserve book/item titles close to how they're written, with reasonable capitalization.
"""

def _extract(raw_message: str, model: str) -> dict:
    response = openai_client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_message},
        ],
    )
    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, KeyError, IndexError):
        return {"items": []}


@traceable(name="extract_school_order")
def target(inputs: dict) -> dict:
    return _extract(inputs["raw_message"], model="gpt-4o-mini")


@traceable(name="extract_school_order_gpt4o")
def target_gpt4o(inputs: dict) -> dict:
    return _extract(inputs["raw_message"], model="gpt-4o")


if __name__ == "__main__":
    test_messages = [
        "Sai Vidyanikethan, 6th class, white long notebook 500 nos",
        "njr class 1 — 18 sets of crown maths b/r-1, b/r-2, ruled-5, d/r-1",
        "class 5 — 20 hindi bharathi-5, 20 school diary-1, 20 slate-1",
    ]
    for msg in test_messages:
        print(msg)
        print(json.dumps(target({"raw_message": msg}), indent=2))
        print()