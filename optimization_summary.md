# Optimization Summary

We compared `gpt-4o-mini` and `gpt-4o` on the same 16-example AG News classification dataset, using identical prompts, temperature, and evaluators (`exact_match`, `plausibility`) to ensure a fair comparison. `gpt-4o-mini` won on every measured axis: 87.5% accuracy vs. 81.25% for `gpt-4o`, at roughly 1/17th the cost per correct answer ($0.0000255 vs. $0.0004579) — `gpt-4o` even introduced a new misclassification (a Business article read as World) that `gpt-4o-mini` didn't make, so the extra cost bought no accuracy benefit on this task. **`gpt-4o-mini` is the clear choice here in every scenario** — cost-constrained, performance-focused, or balanced — since it isn't a trade-off in this case: the cheaper model is also the more accurate one. We would only reconsider `gpt-4o` if a future dataset expansion introduced articles requiring deeper reasoning (e.g., multi-topic or highly nuanced classification) where `gpt-4o-mini`'s simpler category-vocabulary matching might start to break down; for straightforward 4-category news classification, `gpt-4o-mini` is both the performance and cost winner.

| Model | Accuracy | Cost / example | Cost / correct answer | Plausibility |
|---|---|---|---|---|
| gpt-4o-mini | 87.5% | $0.0000223 | $0.0000255 | 4.625 / 5 |
| gpt-4o | 81.25% | $0.0003720 | $0.0004579 | 4.6875 / 5 |

**LangSmith experiments:** `ab-gpt-4o-mini` and `ab-gpt-4o` in the `ag-news-content-classification` dataset.
