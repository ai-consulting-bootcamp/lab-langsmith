# Custom Evaluator Design

**LAB | Micromanage your agents** — Optional Part 1, Steps 11–13
**Author:** Nnanyelugo Ahukannah

Correctness compares an answer to a reference answer. In this domain that leaves
two things unmeasured: whether the answer is actually supported by the clause it
points at, and whether the citation itself is any use to a reviewer. Four custom
evaluators cover that gap — one LLM judge and three deterministic checks.

## 1. `groundedness` — custom LLM-as-judge

**What it measures.** Whether every factual claim in the answer is supported by
the text of the clauses **the answer itself cited** — not by the reference answer,
and not by the model's general legal knowledge. A claim that is true in the real
world but absent from the cited clause is ungrounded, and that is the point:
the deployment is a grounded-QA system, so an answer that quietly leaves its
source is a defect even when it happens to be right.

**Design.** The judge receives the question, the answer, and the resolved text of
the clauses the answer cited. The rubric allows free paraphrase, condensation and
applying a stated rule to the facts in the question; it fails claims that state a
number, deadline, obligation or exception the cited text does not contain, or that
contradict it. Scoring is boolean with reasoning, via `openevals`'
`create_llm_as_judge` on `gpt-4o-mini`.

**What it caught that correctness did not.** On the `terse` configuration,
correctness was 0.909 and groundedness 0.318 — the answers were right and had
stopped resting on anything checkable.

### The rewrite, and why it is documented here

The first version of this prompt scored 0.409 on a configuration that deserved
around 0.95, and the failures did not survive inspection: on Q06 the judge
acknowledged both claims were supported and scored false anyway, on a quibble
about "framing". Auditing it properly gave a number: `openevals` instructs judges
to end their reasoning with "Thus, the score should be: X", so that sentence can
be parsed and compared to the score actually recorded. **My prompt disagreed with
itself on 7.8% of judgements (5 of 64), always scoring false while reasoning
true. The stock openevals correctness prompt was self-consistent on all 65.**
The harness was not at fault; the prompt was.

Two causes, both fixed: the prompt led with prohibitions ("You are NOT checking
whether the answer is correct…"), which biases a judge toward false, and it
specified an output format that `openevals` also controls, which additionally
broke the evaluator outright with a `KeyError: 'reasoning'`. Rewritten in the
stock `<Rubric>` / `<Instructions>` style, self-contradiction went to **0 of 65**
and groundedness on `mini` to 0.955. `analyze_results.py` re-measures the rate on
every run rather than assuming it stayed fixed.

## 2–4. The deterministic citation evaluators

No model, no cost, no opinions — and therefore the one set of numbers in this lab
that cannot itself be wrong about the corpus.

| Evaluator | Question it answers | `mini` | `gpt4o` | `terse` |
|---|---|---|---|---|
| `citation_fabricated_free` | Did it invent an authority that does not exist? | 1.000 | 1.000 | 1.000 |
| `citation_wellformed` | Could a reviewer look the citation up? | 1.000 | 1.000 | 0.364 |
| `citation_validity` | Did it point at the clauses the answer needs? | 0.909 | 0.955 | 0.318 |

**Why three and not one.** The first version was a single `citation_hallucination`
metric, and it reported **77% hallucination** on `terse`. That was wrong. The
model had cited `6` instead of `FC-6`: it found the right clause and dropped the
prefix. Nothing was fabricated in any run — across every configuration, zero
citations failed to correspond to a real clause. Collapsing "invented a source"
and "wrote the reference badly" into one number would have made a formatting bug
the headline finding of the lab.

They are kept apart because they have different fixes. A fabricated citation means
the model cannot be trusted. A malformed one means the prompt needs a format
instruction. And a citation of `6` still fails `citation_wellformed`, because
`RB-6`, `FC-6` and `CT-6` all exist and an auditor cannot tell which was meant —
unverifiable is a real failure, just not the one that was originally reported.

`citation_validity` scores on **resolved** IDs, so a prefix-less citation is not
punished twice; extra valid clauses are tolerated as untidy, and a missing one is
not.

## Controls

Every evaluator is tested before use (`python evaluators.py`): the deterministic
ones against constructed inputs covering exact match, extra-but-valid, missing,
prefix-dropped, ambiguous, fabricated and empty; the judge against a
grounded/ungrounded/applies-the-rule triple it must separate. All pass. The
prefix-dropped and ambiguous cases exist specifically because the first version
got them wrong.

## What the custom evaluators revealed

Correctness ranked `terse` (0.909) **above** `mini` (0.818). Every custom
evaluator ranked it far below. The configuration that looked best on the obvious
metric was the one that had stopped citing anything a compliance reviewer could
check — and no amount of running correctness again would have surfaced that.
