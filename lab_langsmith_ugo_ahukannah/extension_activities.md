# Extension Activities

**LAB | Micromanage your agents**
**Author:** Nnanyelugo Ahukannah

The lab lists five optional extensions. Three are complete, one is partial, one
was not done — recorded as not done rather than stretched to fit.

## 1. Multiple evaluators — **done**, and it is what the lab turned on

Five evaluators run on every example: openevals' stock correctness judge, a custom
`groundedness` LLM judge, and three deterministic citation checks.

| Evaluator | Model? | What it answers | `mini` | `gpt4o` | `terse` |
|---|---|---|---|---|---|
| `correctness` | yes (stock) | Does it match the reference answer? | 0.818 | 0.955 | 0.909 |
| `groundedness` | yes (custom) | Is every claim supported by the cited clause text? | 0.955 | 0.955 | 0.318 |
| `citation_validity` | no | Did it point at the right clauses? | 0.909 | 0.955 | 0.318 |
| `citation_wellformed` | no | Could an auditor look the citation up? | 1.000 | 1.000 | 0.364 |
| `citation_fabricated_free` | no | Did it invent an authority? | 1.000 | 1.000 | 1.000 |

**Comparing them is the finding.** Correctness ranks `terse` *above* `mini`; every
other evaluator ranks it far below. The configuration that looked second-best on
the obvious metric was the one that had stopped citing anything checkable. Design
rationale, and the two evaluator bugs found and fixed along the way, are in
[`custom_evaluator.md`](custom_evaluator.md).

## 2. Domain-specific analysis — **done**

Dataset metadata (`category`, `difficulty`, `n_clauses`) exists so results can be
cut by it, and `analyze_results.py` reports both.

**By difficulty**, correctness for `mini`: easy 0.86 (n=7), medium **0.67** (n=9),
hard **1.00** (n=6). Difficulty is *inverted* — the edge cases built to be hard
(business credit, an internal target that does not displace a regulatory deadline,
a reason a reviewer believes but that is not in the record) were answered
correctly, and the misses clustered in mid-difficulty items.

**By category**, correctness for `mini`: `fcra` 1.00, `internal_policy` 1.00,
`edge_case` 0.75, `regulation_b` **0.67** — the weakest cell in the run. Regulation
B is where the corpus draws the finest distinctions (what counts as adverse action
versus what does not), and that is where a grounded model slips.

Two caveats on reading these: cell sizes are 4–9 examples, so a single example
moves a cell by 0.11–0.25; and correctness here is the metric shown above to be
blind to the citation failure, so these breakdowns describe prose quality only.

## 3. Cost and performance optimization — **done**

Full write-up in [`optimization_summary.md`](../optimization_summary.md).
Per-call tokens and cost recorded on every generation, priced from a stated list
table. `gpt-4o` costs **16.7x** more per query than `gpt-4o-mini`
($5.61 vs $0.34 per 1,000; $112.15 vs $6.72 monthly at 20,000) for +0.137
correctness and identical groundedness. Latency (1.13–1.42s) is not a
differentiator and the ordering moved between runs.

The optimization lesson is that **the prompt was the larger and cheaper lever**:
the same model swings 0.591 on citation validity from prompt wording alone, more
than the 16.7x model upgrade buys in either direction.

## 4. Expand the dataset — **partial**

22 examples against the lab's floor of 10 and its suggested 15–20, spread across
four categories, three difficulty levels, and 24 of the corpus's 27 clauses. Three
clauses (`CT-2`, `FC-1`, `RB-6`) are unexercised, and the corpus is deliberately
small enough to pass whole as context, which keeps the evaluation about grounded
answering rather than retrieval. Not expanded further, because at this size the
binding constraint is **statistical**, not coverage — see below.

## 5. Reproducibility study — **not done**

The lab suggests running the same evaluation several times and analysing the
variance. Each of the three configurations was run **once** (the suite was
executed twice in total, but the first round is not comparable — it used the two
evaluators that were later found to be wrong and rewritten).

This is the honest gap, and it is the one that matters most, because the headline
comparison rests on it. **The `mini` 0.818 versus `terse` 0.909 correctness gap is
two examples out of 22.** Without repeat runs there is no variance estimate, so
that gap cannot be distinguished from noise — which is why every write-up here
states it rather than treating it as a result. The large effects (citation
validity 0.909 → 0.318, a 13-example swing) are far outside any plausible noise
band; the small ones are not, and are not claimed.

Doing it properly is cheap — three configurations x three repeats is about $0.42
and 15 minutes — and it is the first thing I would run next.

## Beyond the lab's list

- **A judge self-consistency audit.** openevals mandates that judges end their
  reasoning with "Thus, the score should be: X", so that sentence can be parsed and
  compared to the stored score. It found a real defect (7.8% self-contradiction in
  my custom prompt against 0% in the stock one) and now runs on every analysis pass.
- **Controls on the dataset builder.** Four deliberately corrupted inputs, each of
  which must be caught and attributed to the right example.
- **Deterministic evaluators as a check on the judges.** Three of the five metrics
  use no model, so they cannot be wrong about the corpus in the way a judge can.

## What I would do next

1. **The reproducibility study above** — three repeats per configuration, report
   variance, and either promote or retire the small differences.
2. **One line added to the terse prompt** ("cite the full clause ID including its
   prefix") and re-measure. If citation validity returns to ~0.9, that proves the
   entire failure was one sentence of prompt, which is the strongest version of
   the finding.
3. **A stronger judge model** for the groundedness evaluator, to test whether 0%
   self-contradiction holds or whether the prompt rewrite was lucky.
