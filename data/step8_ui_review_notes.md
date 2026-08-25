# Step 8: Review Results in LangSmith UI

**Experiment:** `gpt-4o-mini-blog-title-55fcee73` (current — matches `data/eval_results_gpt-4o-mini.json`)
**Dataset:** `blog-title-generation-medium-articles` (18 examples)
**Dataset URL:** https://eu.smith.langchain.com/datasets/c55c213c-5c11-48e2-9bbd-04c91b31ba7d

## Aggregate Metrics (from the Experiments tab)

| Metric | Value |
|---|---|
| N | 18 |
| Mean correctness | 0.878 |
| Median correctness | 0.90 |
| Std dev | 0.131 |
| Min / Max | 0.5 / 1.0 |

Score distribution: six examples at 1.0, six at 0.9, four at 0.8, one at 0.7, one at 0.5.
No errors, no examples the target function failed to complete.

## Initial Observations

- Every generated title is topically *related* to its article — no scores below 0.5, no
  wildly off-topic generations. The model reliably identifies what the article is about.
- A consistent style gap: generated titles skew toward longer, "SEO-listicle" phrasing
  ("Unlocking the Power of...", "The Hidden Dangers of...", "How X Revolutionized Y") versus
  the more varied, sometimes terse or rhetorical style of the real Medium titles. This
  doesn't show up as a lower correctness score in most cases (the judge was designed in
  Step 6 to ignore stylistic differences), but it's a visible qualitative pattern across
  nearly every example.
- The lowest-scoring examples cluster around cases where the reference title is abstract,
  rhetorical, or personal-essay-style rather than descriptive (a question, a single striking
  phrase) — the model's default toward descriptive/explanatory titles seems to conflict most
  with the judge's "topical alignment" criteria in exactly these cases.

## Examples to Investigate Further (Step 9 candidates)

1. **Score 0.5 — "Can This Toxic Question Please Just Go Away?" (Creativity)** — generated
   "The Art of Writing: Balancing Passion and Profit in Your Creative Journey." Worth checking
   the full article excerpt: did the model latch onto a tangential theme, or is the reference
   title just unusually abstract/rhetorical relative to the body content?
2. **Score 0.7 — "Facing Three Fundamental Coronavirus Fears" (Health)** — generated "Will
   SARS-CoV-2 Become Just Another Common Cold? Understanding the Path to Endemicity." This
   reads as a genuine thematic drift (endemic-status framing vs. the article's actual
   "fears" framing), not just a style difference — a good candidate for a real failure-mode
   example in the report.
3. **Score 0.8 — "Four Exercises to Strengthen Your Writing" (Productivity)** — generated
   title added an unprompted "Writer's Block" angle not obviously in the reference framing.
4. **Score 1.0 — "Loss Aversion — how fear influences customer choice" (Marketing)** — a
   strong example for contrast: generated "Harnessing the Power of Loss Aversion: How Fear
   of Missing Out Drives Consumer Choices" is stylistically the same "SEO-listicle" pattern
   as the lower-scoring ones, but scored perfectly — showing the judge is genuinely tracking
   topical match, not penalizing the style pattern itself.

**Note:** items 1 and 2 above reproduced across multiple reruns of the pipeline (same
underlying reason, different exact wording each time due to `temperature=0.3`) — see
`data/step9_analysis.md` §4 for the full error analysis and why this looks like a structural
excerpt-scope limitation rather than one unlucky sample.

## Screenshots

See `lab_proof.md` — dataset examples view (Step 4), the Experiments comparison chart/table
(Step 7/12), and per-example output from `scripts/analyze_results.py` (Step 9).
