# Steps 11–13: Custom Evaluator — Editorial Style Fit

## What It Measures and Why

Step 9's analysis found that generated titles are consistently longer and more
"SEO-listicle" in style than the real published titles (mean 83.5 vs 46.2 characters), but
that this pattern is *uncorrelated* with the Step 6 correctness score — by design, since
that evaluator explicitly rewards topical alignment regardless of style. That leaves a real
question unanswered: **is the model actually producing titles a human editor would publish,
or just topically-accurate-but-bloated ones?** The custom evaluator measures exactly that
dimension, independent of correctness.

**Dimension:** *Editorial style fit* — does the title read like a concise, professionally
edited headline, or like an SEO meta-description?

## Evaluator Design

Implemented in [`scripts/custom_evaluator.py`](../scripts/custom_evaluator.py) using the same
`openevals.create_llm_as_judge` scaffold as the correctness evaluator (Step 6), judged by
`openai:gpt-4o-mini`, `feedback_key="style_fit"`, continuous 0–1 scoring.

- **Criteria for a high score:** concise (typically well under 70 characters), reads
  naturally, avoids generic template phrasing ("Unlocking the Power of...", "The Hidden
  Secret to...", "How X Revolutionized Y"), doesn't stack a catchy hook + a literal
  explanation after a colon.
- **Criteria for a low score:** over-explained, SEO-meta-description tone, relies on
  "unlock/harness/discover" template phrasing, colon-separated double-clause titles.
- **Explicitly instructed to ignore:** topical/wording differences from the reference
  title — the reference is used only as a length/style exemplar, not a required match. This
  keeps it orthogonal to the correctness evaluator by design, rather than just a
  differently-worded copy of it.
- **Edge case handling:** the prompt explicitly tells the judge not to penalize a title for
  differing in subject emphasis from the reference, so a stylistically excellent but
  topically different title isn't unfairly punished on this dimension (that's correctness's
  job).

Smoke-tested on 3 examples before the full run — all three scored 0.4, each flagged for the
exact colon + explanatory-clause pattern the rubric was written to catch.

## Results: Running Both Evaluators Together (Step 12)

Ran via [`scripts/run_evaluation_with_custom.py`](../scripts/run_evaluation_with_custom.py)
(experiment `gpt-4o-mini-blog-title-multi-eval-993d4c7e`), both evaluators scoring the same
18 generated titles in one pass:

| Metric | Correctness | Style Fit |
|---|---|---|
| Mean | 0.87 | **0.33** |
| Median | 0.90 | 0.30 |

**Pearson correlation between the two scores: r = 0.025** — essentially zero. Every single
example scored substantially higher on correctness than on style fit (average gap +0.5),
regardless of how well or poorly it scored on correctness. The biggest gaps were on
otherwise "perfect" examples: `"Loss Aversion — how fear influences customer choice"` scored
1.0 on correctness but only 0.3 on style, generating *"Harnessing Loss Aversion: The Secret
Weapon in Marketing"* — topically flawless, stylistically exactly the generic pattern the
rubric penalizes.

## What the Custom Evaluator Reveals

Correctness alone (Step 7–9) told a reassuring story: mean 0.878, the model reliably gets the
topic right. That story is **incomplete**. Style fit reveals a systematic, near-universal
problem invisible to the correctness metric: this model, prompted this way, does not
produce titles that would pass a human editor's bar for concision — it defaults to
explanatory, template-driven phrasing on almost every example, independent of topical
accuracy. The near-zero correlation confirms these are genuinely two different failure
surfaces, not two views of the same problem — a deployment relying on correctness alone
would ship titles that are accurate but not publishable as-is.
