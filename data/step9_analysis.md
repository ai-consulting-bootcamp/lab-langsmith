# Step 9: Analysis of Evaluation Results

Source: `data/eval_results_gpt-4o-mini.json` (experiment `gpt-4o-mini-blog-title-55fcee73`,
18 examples, `openai:gpt-4o-mini` as both target and judge model). Regenerate this analysis
with `python3 scripts/analyze_results.py`.

## 1. Aggregate Metrics

| Metric | Value |
|---|---|
| N | 18 |
| Mean correctness | 0.878 |
| Median correctness | 0.900 |
| Std dev | 0.131 |
| Min / Max | 0.5 / 1.0 |
| Distribution | 1.0 ×6, 0.9 ×6, 0.8 ×4, 0.7 ×1, 0.5 ×1 |

No target-function errors; every example produced a scoreable output.

## 2. Categorical Analysis (by `primary_tag`)

| Tag | n | Mean |
|---|---|---|
| Self Improvement | 1 | 1.00 |
| Brain | 1 | 1.00 |
| Society | 1 | 1.00 |
| Work | 1 | 1.00 |
| Marketing | 2 | 0.95 |
| People | 1 | 0.90 |
| Writing | 1 | 0.90 |
| Mental Health | 2 | 0.90 |
| Entrepreneurship | 1 | 0.90 |
| Productivity | 2 | 0.85 |
| Health | 2 | 0.80 |
| Lifestyle | 1 | 0.80 |
| Books | 1 | 0.80 |
| Creativity | 1 | 0.50 |

**Caveat:** with only 1–2 examples per tag, none of these per-tag means are statistically
reliable on their own — a single example fully determines most rows. This tells us where to
look qualitatively (see below), not a defensible "the model is worse at Creativity" claim.

## 3. Ruling Out the Obvious Explanation: Title Length/Style

Every generated title is stylistically similar — longer, more "descriptive/SEO" in tone
(mean 83.5 chars) than the real Medium titles (mean 46.2 chars), a gap of roughly +37 chars
on every single example. If this style pattern were what the judge penalized, low scores
should correlate with a bigger length gap. **They don't** (Pearson r = -0.009, essentially
zero): the smallest length gap in the whole set (+6 chars) scored 0.9, while several of the
largest gaps (+61 to +72 chars) scored 0.8 to 1.0, and the actual 0.5 outlier has a
below-average gap (+29 chars). This confirms the Step 6 evaluator is doing what it was
designed to do — scoring topical alignment, not penalizing the model's consistent stylistic
tendency toward longer, more explanatory titles.

## 4. Error Analysis: What Actually Drives Low Scores

Reading the judge's reasoning on the two lowest-scoring examples reveals a consistent,
specific failure mode — not random noise:

**Example A (score 0.5)** — Ref: *"Can This Toxic Question Please Just Go Away?"* →
Generated: *"The Art of Writing: Balancing Passion and Profit in Your Creative Journey"*
The article's opening excerpt sets up a debate ("should we write because we must, or for
money?") but the human title is a rhetorical reaction *to* that debate (frustration with the
question itself), which only becomes clear as the author's stance later in the full article.
The model, working only from the excerpt, produced an accurate *description* of the debate's
topic rather than the author's *rhetorical stance* on it.

**Example B (score 0.7)** — Ref: *"Facing Three Fundamental Coronavirus Fears"* →
Generated: *"Will SARS-CoV-2 Become Just Another Common Cold? Understanding the Path to
Endemicity"*
Same pattern: the visible excerpt opens with background on immunity duration, and the model
titled that visible content accurately — but the reference title reflects the article's
broader "three fears" framing, which is presumably structured later in the piece.

**Failure mode identified: excerpt-scope mismatch.** Our ~400-word excerpts (Step 3) capture
enough for the model to correctly identify the article's *subject matter* in all 18 cases
(nothing scored low enough to suggest topical confusion), but for articles whose title
reflects the author's stance/angle/structure rather than just their subject — opinion
pieces, personal essays, "N reasons/fears/questions" framings — that angle isn't always
established within the first 400 words. The model can only title what it's shown, and what
it's shown is sometimes just the setup.

This is a dataset/task-design limitation, not a model capability failure: a human given only
the same 400-word excerpt would likely have the same difficulty guessing the specific
rhetorical framing of the full piece.

**Note on reproducibility:** this exact failure mode (same two examples, same underlying
reason) reproduced consistently across multiple reruns of the target function despite
`temperature=0.3` producing different generated wording each time — e.g. the aggregate mean
shifted from 0.85 to 0.878 between runs, but the *qualitative* pattern was identical. That's
a useful signal in itself: the excerpt-scope limitation looks structural, not incidental to
one unlucky sampling.

## 5. Performance Insights Summary

- **Strength:** gpt-4o-mini reliably identifies article subject matter from a partial
  excerpt — no example scored low enough to indicate genuine topical confusion.
- **Consistent stylistic tendency:** generated titles run ~1.8x longer and more
  "explanatory/SEO" than real published titles, but this tendency is not what the evaluator
  penalizes (verified via the length-gap check above, r ≈ 0) — it's a separate, real
  qualitative difference worth noting for anyone using this model for actual title-writing.
- **Real weakness:** on articles where the human title captures a stance, angle, or
  structural framing that only emerges later in the piece, the model defaults to
  summarizing the visible setup instead — an excerpt-scope limitation more than a model
  limitation.
- **Sample size:** n=18 with 14 distinct tags is enough to spot qualitative patterns (as
  above) but too small for confident per-category comparisons or for treating the 0.878 mean
  as a precise population estimate.
