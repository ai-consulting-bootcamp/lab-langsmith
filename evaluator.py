import json
from dotenv import load_dotenv
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

openai_client = wrap_openai(OpenAI())

JUDGE_PROMPT = """You are grading whether an extracted school book order matches the reference (ground truth) order.

Original message:
{raw_message}

Compare the ITEMS lists. Judge them as MATCHING if they are semantically equivalent, even if:
- capitalization differs (e.g. "class 1" vs "CLASS 1")
- minor whitespace or punctuation differs
- title wording is a close paraphrase (e.g. "Crown Maths B/R-1, B/R-2" vs "crown maths b/r-1, b/r-2")

Judge them as NOT matching if:
- an item is missing or extra
- school, class, or qty is wrong or null when it shouldn't be (or vice versa)
- the title refers to a genuinely different book/item, not just different formatting

Reference (ground truth):
{reference}

Extracted output:
{output}

Respond with ONLY valid JSON: {{"score": 1 or 0, "reasoning": "one sentence explaining the score"}}
"""

def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(
                raw_message=inputs.get("raw_message", ""),
                reference=json.dumps(reference_outputs, indent=2),
                output=json.dumps(outputs, indent=2),
            ),
        }],
    )
    try:
        result = json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, KeyError, IndexError):
        result = {"score": 0, "reasoning": "Judge response was not valid JSON."}

    return {
        "key": "correctness",
        "score": result.get("score", 0),
        "comment": result.get("reasoning", ""),
    }


COMPLETENESS_PROMPT = """You are checking whether an extraction captured every distinct item mentioned in a reference order, without dropping or adding items.

Original message:
{raw_message}

Ignore formatting differences (capitalization, phrasing). Ignore whether qty or school are exactly correct — focus ONLY on item coverage: does each item in the reference have a corresponding item in the extraction (same book/item, roughly matched by title), and are there no extra hallucinated items?

Reference items:
{reference}

Extracted items:
{output}

Respond with ONLY valid JSON: {{"missing_count": integer, "extra_count": integer, "total_reference_items": integer, "reasoning": "one sentence"}}
"""

def completeness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{
            "role": "user",
            "content": COMPLETENESS_PROMPT.format(
                raw_message=inputs.get("raw_message", ""),
                reference=json.dumps(reference_outputs, indent=2),
                output=json.dumps(outputs, indent=2),
            ),
        }],
    )

    parse_failed = False
    try:
        result = json.loads(response.choices[0].message.content)
        total = result.get("total_reference_items")
        missing = result.get("missing_count")
        extra = result.get("extra_count")
        if total is None or missing is None or extra is None or total <= 0:
            raise ValueError("Missing or invalid required fields in judge response")
        score = max(0.0, (total - missing - extra) / total)
    except (json.JSONDecodeError, KeyError, IndexError, ValueError, TypeError):
        parse_failed = True
        result = {"reasoning": "Judge response was malformed or missing required fields — not a genuine 0 score."}
        total, missing, extra = 0, 0, 0
        score = 0.0

    return {
        "key": "completeness",
        "score": round(score, 2),
        "comment": result.get("reasoning", ""),
        "metadata": {
            "missing_count": missing,
            "extra_count": extra,
            "total_reference_items": total,
            "judge_parse_failed": parse_failed,
        },
    }

if __name__ == "__main__":
    test_cases = [
        {
            "inputs": {"raw_message": "Sai Vidyanikethan, 6th class, white long notebook 500 nos"},
            "outputs": {"items": [{"school": "Sai Vidyanikethan", "class": "6th", "title": "white long notebook", "qty": 500}]},
            "reference_outputs": {"items": [{"school": "Sai Vidyanikethan", "class": "6th", "title": "White Long Notebook", "qty": 500}]},
        },
        {
            "inputs": {"raw_message": "njr class 1 — 18 sets of crown maths b/r-1, b/r-2, ruled-5, d/r-1"},
            "outputs": {"items": [{"school": None, "class": "class 1", "title": "crown maths b/r-1, b/r-2, ruled-5, d/r-1", "qty": 18}]},
            "reference_outputs": {"items": [{"school": "NJR EM School", "class": "CLASS 1", "title": "Crown Maths B/R-1, B/R-2, Ruled-5, D/R-1", "qty": 18}]},
        },
    ]
    for case in test_cases:
        result = correctness_evaluator(case["inputs"], case["outputs"], case["reference_outputs"])
        print(case["inputs"]["raw_message"])
        print(result)
        print()

    completeness_cases = [
        {
            "inputs": {"raw_message": "njr class 1 — 18 sets of crown maths b/r-1, b/r-2, ruled-5, d/r-1"},
            "outputs": {"items": [{"school": None, "class": "class 1", "title": "crown maths b/r-1, b/r-2, ruled-5, d/r-1", "qty": 18}]},
            "reference_outputs": {"items": [{"school": "NJR EM School", "class": "CLASS 1", "title": "Crown Maths B/R-1, B/R-2, Ruled-5, D/R-1", "qty": 18}]},
        },
        {
            "inputs": {"raw_message": "Sai Vidyanikethan 6th — telugu, english, science, social 40 sets each"},
            "outputs": {"items": [{"school": "Sai Vidyanikethan", "class": "6th", "title": "telugu", "qty": 40}]},
            "reference_outputs": {"items": [
                {"school": "Sai Vidyanikethan", "class": "6th", "title": "Telugu", "qty": 40},
                {"school": "Sai Vidyanikethan", "class": "6th", "title": "English", "qty": 40},
                {"school": "Sai Vidyanikethan", "class": "6th", "title": "Science", "qty": 40},
                {"school": "Sai Vidyanikethan", "class": "6th", "title": "Social", "qty": 40},
            ]},
        },
    ]
    for case in completeness_cases:
        result = completeness_evaluator(case["inputs"], case["outputs"], case["reference_outputs"])
        print(result)