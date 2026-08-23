# Steps 11–13: Custom Evaluator — Clarity & Actionability

## What It Measures
The built-in `correctness_evaluator` only checks factual accuracy against the
reference answer. `clarity_evaluator` (added in `langsmith_evaluation.py`) scores
a separate dimension: **can a working designer actually use this answer without
looking anything up?**

## Criteria
1. Could the answer be applied directly, with no further lookup?
2. Is it free of unnecessary jargon or filler?
3. Is the length appropriate to the question — not padded, not too terse?

## Scale
- **1** — clear, well-structured, immediately usable
- **0** — hard to parse, vague, or poorly structured (independent of whether the
  facts are correct)

## Why This Is a Useful Second Dimension
An answer can be factually correct but dense or poorly organized (e.g. a
list-based question answered as one unbroken paragraph), or it can be clear and
well-formatted while still missing a fact. Running both evaluators on the same
run lets you see where they diverge — that divergence is the actual signal a
single correctness score would hide.

## Status: Code implemented, not yet executed
`clarity_evaluator` is wired into `run_evaluation()` alongside
`correctness_evaluator`, so a normal run of `python langsmith_evaluation.py` will
now produce both `correctness` and `clarity_actionability` scores per example in
LangSmith and in the printed summary.

**I have not run this** — I don't have API/LangSmith access from this
environment, and I'm not going to invent scores or a comparison table. To
complete this deliverable:

1. Rotate your LangSmith key (the one pasted into this chat should be treated as
   compromised) and put the new one in `.env`.
2. Run `python langsmith_evaluation.py`.
3. Pull the `clarity_actionability` column from the LangSmith UI or
   `evaluation_results.json` and fill in the table below with your real numbers.

| Question | Correctness | Clarity/Actionability | Notes |
|---|---|---|---|
| _(fill in after running)_ | | | |

Once filled in, add 2–3 sentences here on whether the two scores tracked
together or diverged, and what that tells you about the target model's output
style.
