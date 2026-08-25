# Evaluation Summary

We evaluated `gpt-4o-mini`'s ability to generate blog titles from ~400-word excerpts of 18
real Medium articles (14 distinct topics, sourced from `fabiochiu/medium-articles`), scored
by a custom LLM-as-judge correctness evaluator (`openai:gpt-4o-mini`, continuous 0–1 scale,
rewarding topical alignment while ignoring stylistic wording); the model achieved a mean
correctness of **0.88** (median 0.90, range 0.5–1.0, zero errors), with the dominant failure
mode being an **excerpt-scope mismatch** rather than style — on articles whose human title
encodes the author's stance or rhetorical framing rather than just the topic, that framing
often isn't established within the first 400 words, so the model titles the visible setup
instead (confirmed independent of the model's separate, consistent tendency toward longer
"SEO-style" phrasing via a length-gap-vs-score check); a second, optional evaluator scoring
**editorial style fit** (does the title read like a publishable headline, judged
independently of topic) found a mean of only **0.33** with essentially zero correlation to
correctness (**r = 0.025**), showing the model is topically reliable but rarely produces an
editor-ready title as-is. Key limitations: the sample is small (n=18, 1–2 examples per tag,
so per-category claims aren't statistically robust) and the judge shares a model family with
the target function, risking shared blind spots. **Recommendation:** extend the extracted
excerpt to include the article's concluding paragraph(s) alongside the opening — not just
the first 400 words — to expose stance-revealing content for opinion/personal-essay pieces.

## Key Metrics

| Metric | Value |
|---|---|
| N examples | 18 |
| Mean correctness | 0.878 |
| Median correctness | 0.90 |
| Std dev | 0.131 |
| Min / Max | 0.5 / 1.0 |
| Errors | 0 |

## Score Distribution

| Score | Count |
|---|---|
| 1.0 | 6 |
| 0.9 | 6 |
| 0.8 | 4 |
| 0.7 | 1 |
| 0.5 | 1 |

## Custom Evaluator: Correctness vs. Editorial Style Fit (optional)

| Metric | Correctness | Style Fit |
|---|---|---|
| Mean | 0.87 | 0.33 |
| Median | 0.90 | 0.30 |
| Correlation (r) | 0.025 | |

Full methodology, per-example results, and error analysis: see `domain_and_dataset.md`,
`README.md` ("Data Structure"), `data/step9_analysis.md`, and `data/custom_evaluator_summary.md`.
