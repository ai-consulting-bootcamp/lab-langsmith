"""
Step 11: Custom evaluator beyond correctness - "editorial style fit".

Step 9's analysis found that generated titles are consistently longer and more
"SEO-listicle" in style than real published titles (mean 79.9 vs 46.2 chars),
but that this pattern is *uncorrelated* with the Step 6 correctness score - by
design, since that evaluator explicitly ignores style. That means correctness
alone can't tell us whether the model is actually producing publishable,
editor-quality titles or just topically-accurate-but-bloated ones. This
evaluator measures that missing dimension directly.

Usage (smoke test on 3 examples):
    python3 scripts/custom_evaluator.py
"""

import json

from dotenv import load_dotenv
from openevals.llm import create_llm_as_judge

from target_function import generate_title

load_dotenv()

JUDGE_MODEL = "openai:gpt-4o-mini"

STYLE_FIT_PROMPT = """You are a senior editor at a publication like Medium, judging whether a \
generated title matches professional editorial style - independent of whether it is \
topically accurate (a separate evaluator already checks that).

<Rubric>
A title with strong editorial style fit:
- Is concise and punchy rather than long-winded (roughly similar length to real published \
headlines - typically well under 70 characters)
- Reads naturally, the way a human editor would actually phrase it
- Avoids generic clickbait/SEO-listicle patterns such as "Unlocking the Power of...", \
"The Hidden Secret to...", "How X Revolutionized Y", "The Ultimate Guide to...", or titles \
that stack two explanatory clauses together with a colon just to cram in more description

A title with weak editorial style fit:
- Is noticeably longer than necessary, over-explains itself, or reads like an SEO \
meta-description rather than a headline
- Relies on generic "unlock/harness/discover the power of" template phrasing
- Stacks a catchy hook + a literal explanation after a colon, when either alone would be a \
better title

<reference_outputs> below contains the article's real, published title - use it only as a \
reference point for what a natural, professionally-edited title in this style looks like, \
NOT as a required exact match. A generated title can score well even if it is completely \
different in wording from the reference, as long as it independently reads like a real, \
concise, editor-quality headline.
</Rubric>

<Instructions>
- Judge ONLY style fit (conciseness, naturalness, absence of generic template phrasing) - \
do NOT judge topical correctness, that is scored separately
- Do not penalize a title merely for differing in wording or subject emphasis from the \
reference; only judge whether it reads like a real, professionally-edited headline
</Instructions>

<output>
{outputs}
</output>

<reference_outputs>
{reference_outputs}
</reference_outputs>"""

_style_judge = create_llm_as_judge(
    prompt=STYLE_FIT_PROMPT,
    model=JUDGE_MODEL,
    feedback_key="style_fit",
    continuous=True,
)


def style_fit_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    return _style_judge(outputs=outputs, reference_outputs=reference_outputs)


def _smoke_test():
    with open("data/blog_title_examples.json") as f:
        examples = json.load(f)

    for ex in examples[:3]:
        generated = generate_title(ex["inputs"])
        result = style_fit_evaluator(
            inputs=ex["inputs"],
            outputs=generated,
            reference_outputs=ex["outputs"],
        )
        print("REFERENCE:  ", ex["outputs"]["title"])
        print("GENERATED:  ", generated["title"])
        print("STYLE SCORE:", result["score"])
        print("REASONING:  ", result["comment"])
        print("-" * 60)


if __name__ == "__main__":
    _smoke_test()
