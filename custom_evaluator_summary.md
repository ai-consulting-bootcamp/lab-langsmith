# Custom Evaluator: Warmth/Empathy

## What it measures

The `warmth_evaluator` (LLM-as-judge, `gpt-4o-mini`, 1-5 scale) measures whether a coach
response feels human and validating — acknowledging what the employee shared — versus
clinical or interrogative, **independent of structural correctness**. It is explicitly
instructed not to penalize a response for being a single clean question (that's the
`correctness` evaluator's job); it grades tone only.

**Rubric:** 5 = warm acknowledgment + question feels like it comes from someone who was
listening · 3 = neutral/professional · 1 = clinical, robotic, feels like a form question.

## Results: correctness vs. warmth (experiment `coach-gpt4o-mini-with-warmth`)

| Metric | Value |
|---|---|
| Correctness (avg) | 0.80 (12/15 passed) |
| Warmth (avg) | 2.07 / 5 |
| Warmth range across all 15 examples | 2.00–3.00 (essentially flat) |

## What the comparison reveals

Correctness and warmth are **independent** dimensions with no visible correlation in this
run: examples that passed correctness (single, open, advice-free question) scored the same
warmth (2/5) as examples that failed it. Even the two correctness failures (rows 11, 15)
scored identically to the passes on warmth — a structurally flawed question isn't any
warmer or colder than a structurally sound one.

The consistently flat warmth score (2/5 on nearly every row, one 3/5) points to a specific,
fixable cause: the target function's system prompt instructs "keep it to a single sentence"
and "output only the question — no preamble." That structural constraint leaves no room for
an acknowledgment clause before the question, so the model produces analytically sound but
tonally cold questions by design — this is a prompt limitation, not a model limitation.

**Insight the custom evaluator adds that correctness alone would miss:** a response can be
100% structurally "correct" by this lab's definition and still read as cold and clinical to
an employee — correctness alone would never have surfaced this, since it only checks for
compound questions, yes/no framing, and embedded advice.

## Recommendation

Relax the "single sentence, no preamble" constraint in the target function's system prompt
to explicitly allow a short acknowledgment clause (e.g. "That sounds frustrating — what got
in the way?") before the question, and re-run both evaluators to confirm warmth improves
without correctness regressing.
