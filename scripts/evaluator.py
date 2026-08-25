"""
Step 6: Correctness evaluator for the blog-title-generation task.

Built on openevals' create_llm_as_judge scaffold, but with a custom rubric
instead of the built-in CORRECTNESS_PROMPT: that prompt is written for
factual QA ("addresses all parts of the question", "factual errors"), which
doesn't map cleanly onto judging a generated title against a reference title.
There's rarely one single "correct" title for an article - multiple phrasings
can be equally good - so the rubric below asks the judge to score topical/
factual alignment with the article and reference, not exact-match wording.

Usage (smoke test on 3 examples):
    python3 scripts/evaluator.py
"""

import json

from dotenv import load_dotenv
from openevals.llm import create_llm_as_judge

from target_function import generate_title

load_dotenv()

JUDGE_MODEL = "openai:gpt-4o-mini"

BLOG_TITLE_CORRECTNESS_PROMPT = """You are an expert blog editor evaluating whether a generated title \
is a correct, publishable title for the given article excerpt.

<Rubric>
A correct title:
- Accurately represents the article's actual topic and content (no factual mismatch)
- Would be a reasonable title a human editor could publish for this article
- Captures the same core subject as the reference title, even if the wording differs

Note: there is rarely one single "correct" title. Do NOT penalize a title just for using \
different words, a different structure, or a different length than the reference - only \
penalize it for being topically inaccurate, misleading, or unrelated to what the article \
actually discusses.

When scoring, you should penalize:
- Titles that misrepresent or contradict the article's actual content
- Titles that are generic to the point of being meaningless (e.g. "An Article About Life")
- Titles that are unrelated to the reference title's subject matter
</Rubric>

<Instructions>
- Read the article excerpt in <input>, the generated title in <output>, and the reference \
title in <reference_outputs>
- Judge topical/factual alignment with the article and reference - not stylistic similarity
</Instructions>

<input>
{inputs}
</input>

<output>
{outputs}
</output>

<reference_outputs>
{reference_outputs}
</reference_outputs>"""

_judge = create_llm_as_judge(
    prompt=BLOG_TITLE_CORRECTNESS_PROMPT,
    model=JUDGE_MODEL,
    feedback_key="correctness",
    continuous=True,
)


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    return _judge(inputs=inputs, outputs=outputs, reference_outputs=reference_outputs)


def _smoke_test():
    with open("data/blog_title_examples.json") as f:
        examples = json.load(f)

    for ex in examples[:3]:
        generated = generate_title(ex["inputs"])
        result = correctness_evaluator(
            inputs=ex["inputs"],
            outputs=generated,
            reference_outputs=ex["outputs"],
        )
        print("REFERENCE: ", ex["outputs"]["title"])
        print("GENERATED: ", generated["title"])
        print("EVAL RESULT:", result)
        print("-" * 60)


if __name__ == "__main__":
    _smoke_test()
