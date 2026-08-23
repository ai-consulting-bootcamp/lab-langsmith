"""
custom_evaluator.py (Optional Part 1)

Custom LLM-as-judge evaluator measuring PLAUSIBILITY: whether the model's chosen category is a defensible 
classification given the article's actual content, independent of whether it matches AG News's official reference
label.

This is a different question than exact_match_evaluator (evaluators.py) answers. exact_match asks 
"did the model match the dataset's label?" plausibility asks "is the model's answer reasonable given the article,
even if it doesn't match the official label?" A prediction can be INCORRECT (wrong per the dataset) but still PLAUSIBLE 
(a defensible human judgment call), or INCORRECT and IMPLAUSIBLE (a genuine reasoning error).
This distinction matters for AG News specifically because several categories (e.g. a tech-company retail story vs. 
a business story) sit on genuinely ambiguous boundaries.

Scoring: integer 1-5
    1 = the assigned category makes no sense given the article content
    2 = a weak or strained connection to the assigned category
    3 = a defensible but not obviously the best fit
    4 = a solid, well-supported fit
    5 = a clearly correct and unambiguous fit

Evaluator function signature follows LangSmith's convention:
    evaluator(inputs, outputs, reference_outputs) -> dict
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

JUDGE_MODEL = os.environ.get("PLAUSIBILITY_JUDGE_MODEL", "gpt-4o-mini")
VALID_CATEGORIES = {"World", "Sports", "Business", "Sci/Tech"}

_client = OpenAI()

PLAUSIBILITY_PROMPT = """You are grading whether a news category assignment is PLAUSIBLE
given the article's content -- NOT whether it matches any particular official label.

Article text (with instructions prefix already included):
{question}

Category the classifier assigned: {predicted_category}

Judge whether "{predicted_category}" is a defensible category for this article's actual
subject matter, considering that some articles genuinely sit on a boundary between two
categories (e.g. a tech company's retail sale could plausibly read as Business or Sci/Tech).

Score from 1 to 5:
1 = the assigned category makes no sense given the article content
2 = a weak or strained connection to the assigned category
3 = defensible, but probably not the best fit
4 = a solid, well-supported fit
5 = a clearly correct and unambiguous fit

Respond ONLY with JSON: {{"score": <int 1-5>, "reasoning": "<one sentence>"}}"""


def plausibility_evaluator(inputs: dict, outputs: dict, reference_outputs: dict = None) -> dict:
    """Custom evaluator: scores whether the model's predicted category is a
    defensible read of the article, independent of the reference label.

    reference_outputs is accepted for signature compatibility with
    LangSmith's evaluator convention but is intentionally NOT used in the
    scoring logic -- that's what makes this evaluator distinct from
    exact_match_evaluator.
    """
    question = inputs.get("question", "")
    predicted_category = outputs.get("expected_output", "")

    if predicted_category not in VALID_CATEGORIES:
        return {
            "key": "plausibility",
            "score": 0,
            "comment": "Model output '{}' is not one of the four valid categories.".format(predicted_category),
        }

    prompt = PLAUSIBILITY_PROMPT.format(question=question, predicted_category=predicted_category)

    response = _client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
        score = int(parsed["score"])
        reasoning = parsed.get("reasoning", "")
    except (json.JSONDecodeError, KeyError, ValueError):
        score, reasoning = 0, "Failed to parse judge output"

    return {"key": "plausibility", "score": score, "comment": reasoning}


if __name__ == "__main__":
    # Test 1: a correct, unambiguous prediction -> should score high
    test_1 = plausibility_evaluator(
        inputs={"question": "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: Olympics: Thorpe Beats Phelps as U.S. Fights Gold Gap. Australian swimmer Ian Thorpe beat arch-rival Michael Phelps in the men's 200-meter freestyle."},
        outputs={"expected_output": "Sports"},
    )
    print("Test 1 (clear Sports article, predicted Sports):", test_1)

    # Test 2: one of our known failures -- wrong per exact_match, but is it plausible?
    test_2 = plausibility_evaluator(
        inputs={"question": "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: 'Madden,' 'ESPN' Football Score in Different Ways. EA Sports would like to think it was because \"Madden NFL 2005\" came out that day, and some fans of the football simulation are rabid enough to take a sick day to play it."},
        outputs={"expected_output": "Sports"},  # model's actual prediction; true label is Sci/Tech
    )
    print("Test 2 (Madden article, predicted Sports, true label Sci/Tech):", test_2)

    # Test 3: nonsense category -> should score 0 automatically, no API call needed
    test_3 = plausibility_evaluator(
        inputs={"question": "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: Some article about anything."},
        outputs={"expected_output": "Politics"},  # not a valid category
    )
    print("Test 3 (invalid category):", test_3)
