"""
Step 5: Target function for the blog-title-generation task.

Takes a dataset example's `inputs` (an article excerpt) and returns `outputs`
in the same shape as the dataset's ground truth ({"title": ...}), so the
correctness evaluator (Step 6) can compare them directly.

Usage (smoke test on 3 examples):
    python3 scripts/target_function.py
"""

import json

from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

openai_client = wrap_openai(OpenAI())

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.3
MAX_TOKENS = 40

SYSTEM_PROMPT = (
    "You are an expert blog editor. Given the excerpt of a blog article, write a single, "
    "engaging, accurate title for it - the kind a human writer would actually publish on "
    "Medium. Reply with ONLY the title text: no quotes, no explanation, no \"Title:\" prefix."
)


@traceable(name="blog-title-target")
def generate_title(inputs: dict) -> dict:
    """inputs: {"article_text": str} -> outputs: {"title": str}

    Errors are caught and surfaced as an empty title + error field rather than
    raising, so a single failed API call doesn't abort the whole evaluation run.
    """
    article_text = inputs["article_text"]
    try:
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": article_text},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        title = response.choices[0].message.content.strip().strip('"')
        return {"title": title}
    except Exception as e:
        return {"title": "", "error": str(e)}


def _smoke_test():
    with open("data/blog_title_examples.json") as f:
        examples = json.load(f)

    for ex in examples[:3]:
        result = generate_title(ex["inputs"])
        print("REFERENCE TITLE:", ex["outputs"]["title"])
        print("GENERATED TITLE:", result["title"])
        print("PRIMARY TAG:    ", ex["metadata"]["primary_tag"])
        print("-" * 60)


if __name__ == "__main__":
    _smoke_test()
