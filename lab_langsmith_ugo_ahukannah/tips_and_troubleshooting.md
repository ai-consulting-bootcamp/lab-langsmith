# Tips & Troubleshooting — what actually happened

**LAB | Micromanage your agents**
**Author:** Nnanyelugo Ahukannah

The lab names four categories of common issue. Three of them came up. This
records what each looked like in practice, plus three failures the lab does not
warn about — two of which were in my own evaluators and would have become the
headline finding if they had gone unnoticed.

## 1. Dataset creation problems

**What the lab warns about:** badly structured examples, inconsistent field names,
wrong format for LangSmith.

**What was done.** The dataset is never hand-assembled. `build_dataset.py` joins
`questions.json` against clauses parsed out of the corpus and **refuses to emit
anything unsound**, exiting non-zero if a citation does not resolve, an example ID
repeats, a question repeats, a required field is empty, or fewer than 10 examples
survive.

Field-name consistency is structural rather than hoped for: every example is built
by the same function, so `inputs.question` / `outputs.answer` / `outputs.clause_ids`
cannot drift between examples.

**The upload is idempotent.** `run_evaluation.py` checks whether the dataset
already exists by name and reuses it. Re-creating a dataset between experiments
either errors or silently forks the examples out from under an earlier run, which
makes two experiments incomparable without ever announcing it. `--refresh` is the
deliberate override, and after any upload the example count is read back and the
run aborts if it does not match.

**And the validator itself is tested.** A validator that never rejects anything
looks exactly like one that works, so it is run against four deliberately
corrupted inputs — fabricated citation, duplicate ID, empty answer, duplicate
question — and each is caught and attributed to the right example.

## 2. Target function errors

**What the lab warns about:** wrong input format, wrong field extraction, wrong
output format, tracing not configured.

**What was done.** The target takes `inputs["question"]` and returns a dict, and
tracing is wired two ways — `wrap_openai` on the client and `@traceable` on each
target — so every call lands in the project without per-call instrumentation.

Output format is enforced with `response_format={"type": "json_object"}`, and an
unparseable response degrades rather than crashing: the raw text becomes the
answer, citations become empty, and the evaluators mark it down. **Errors are
returned, not raised** — a single failure cannot abort a 22-example experiment:

```python
except Exception as exc:
    return {"answer": "", "clause_ids": [], "error": f"{type(exc).__name__}: {exc}"}
```

Zero errors occurred across all 66 runs, and the field is recorded per row so a
silent failure would be visible rather than showing up as a mysteriously low score.

## 3. Evaluation failures

**What the lab warns about:** evaluator signature mismatch, missing reference
outputs, missing dataset fields, rate limits.

**This is the one that actually bit, and the cause is not in the lab's list.** The
custom judge crashed with:

```
KeyError: 'reasoning'
  File ".../openevals/llm.py", line 271, in get_score
    return (response["score"], response["reasoning"])
```

The signature was correct. The cause was that **my prompt specified its own output
format**. `create_llm_as_judge` builds its own structured-output schema —
`reasoning` first, then `score` — and instructs the judge to end its reasoning with
"Thus, the score should be: X". A prompt that also demands JSON overrides that
schema, the `reasoning` key disappears, and openevals cannot read its own result.

**Never specify an output format in an openevals judge prompt.** Write the rubric
and say nothing about output.

Rate limits were handled by keeping `max_concurrency` at 3, as the lab suggests.

## 4. Results analysis challenges

**What the lab warns about:** get results into an analysable format, use the UI,
consider visualisations, look for patterns in successes and failures.

**What was done.** Every experiment is flattened to JSON with per-example scores,
comments, tokens, latency and cost, then `analyze_results.py` produces headline
metrics, breakdowns by category and difficulty, a failure-mode census naming the
example IDs, and two charts. The LangSmith UI was used for the three-way
comparison view; screenshots are in `screenshots/`.

The pattern that mattered came out of the by-metric view rather than the by-example
one: `terse` scoring *above* `mini` on correctness while collapsing on every
citation metric is only visible when the metrics sit side by side.

---

## Three the lab does not warn about

### A metric that merges two failure modes will name the wrong cause

The first citation evaluator reported **77% hallucination** on `terse`. It never
happened. The model cited `6` instead of `FC-6` — right clause, missing prefix.
Classifying every citation showed **0 unresolvable, 23 ambiguous-bare, 2
unambiguous-bare, 6 exact**. Nothing was fabricated in any run.

"The model invented a source" and "the model formatted a field badly" need
opposite fixes, so they are now three separate metrics. Had this shipped, the
lab's headline would have been a formatting bug misreported as dishonesty.

### A judge can disagree with itself, and you can measure it for free

My groundedness judge scored 0.409 on answers that looked fine. On one example its
reasoning ended **"Thus, the score should be: true"** while the recorded score was
false.

Because openevals *mandates* that closing sentence, it can be parsed and compared
against the score actually stored. My prompt: **5 self-contradictions in 64
(7.8%)**, always false-while-reasoning-true. The stock correctness prompt: **0 in
65**. So the harness was fine and the prompt was not. Two causes — it led with
prohibitions ("You are NOT checking…"), which biases a judge toward false, and it
specified an output format. Rewritten in the stock `<Rubric>` style: **0 of 65**,
and groundedness moved to 0.955. `analyze_results.py` re-measures the rate every
run rather than assuming it stayed fixed.

### An EU workspace 403s against the default endpoint

A LangSmith key from an EU workspace authenticates against
`https://api.smith.langchain.com` and then returns `403 Forbidden` on **every**
call. It reads as a bad key or a permissions problem, and neither is true. The fix
is one environment variable:

```
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

Probe both endpoints before debugging anything else.
