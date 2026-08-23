# Optimization Summary

We compared gpt-4o-mini and gpt-4o as the target model for SaaS support responses, same 20-example dataset, same correctness judge. gpt-4o scored 0.57 correctness versus gpt-4o-mini's 0.35, a real improvement, but gpt-4o cost $0.0143 total against gpt-4o-mini's $0.00075, about 19x more. On a cost-per-correct-answer basis, gpt-4o-mini comes out around $0.0001 per correct answer versus gpt-4o's $0.0013, roughly 12x cheaper per correct response despite the lower raw score. Latency was close, 1.03s vs 1.23s average, not a deciding factor either way.

**Best cost efficiency:** gpt-4o-mini. Pick this for high-volume, budget-constrained support deployments where a lower per-ticket accuracy is acceptable, especially if paired with better prompt engineering, since our earlier analysis found the accuracy gap is partly a prompt issue (missing procedural detail), not a model capability ceiling.

**Best raw performance:** gpt-4o. Pick this for lower-volume, higher-stakes tickets, or as an escalation tier when gpt-4o-mini's confidence or actionability score is low.

**Best balanced option:** gpt-4o-mini with an improved system prompt (explicit step-by-step formatting instruction), retested before committing to gpt-4o's cost. Cheap to test, likely to close part of the correctness gap without the 19x cost jump.

| Model | Correctness | Total Cost (20 runs) | Cost / Correct Answer | Avg Latency |
|---|---|---|---|---|
| gpt-4o-mini | 0.35 | $0.00075 | $0.000107 | 1.03s |
| gpt-4o | 0.57 | $0.0143 | $0.001254 | 1.23s |