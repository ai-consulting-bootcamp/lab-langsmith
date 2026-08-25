# Optimization Summary

We ran the blog-title-generation task (same 18-example dataset, same correctness evaluator)
through both `gpt-4o-mini` and `gpt-4o` to compare cost and performance directly; `gpt-4o-mini`
scored a mean correctness of **0.906** at **$0.000095/example** (~$0.09 per 1,000 titles),
while `gpt-4o` scored **0.892** at **$0.001564/example** (~$1.56 per 1,000 titles) — a
**16.5x higher cost for a slightly lower score**. That score gap (-0.014) is well within the
run-to-run noise we've observed from the LLM-as-judge evaluator itself (±0.03 across reruns
of the *same* model), so the honest reading isn't "gpt-4o is worse" — it's that **gpt-4o
shows no measurable quality advantage on this task**, making its 16.5x cost premium
unjustified here. **Recommendation:** use `gpt-4o-mini` for all three scenarios (budget,
quality-max, and balanced) for this specific task — it isn't a compromise choice, it's the
dominant option on both axes for a task this size and complexity; `gpt-4o`'s extra capacity
would likely matter more for longer, more nuanced content-generation tasks than short
title generation, which this comparison doesn't test.

## Comparison

| Model | N | Mean Score | Total Cost (18 ex.) | Cost/Example | Cost per 1,000 | Mean Latency |
|---|---|---|---|---|---|---|
| `gpt-4o-mini` | 18 | 0.906 | $0.00170 | $0.000095 | $0.09 | 1.14s |
| `gpt-4o` | 18 | 0.892 | $0.02816 | $0.001564 | $1.56 | 1.10s |

Latency was essentially identical between the two (both single synchronous API calls); the
entire cost-performance gap is driven by per-token pricing, not by a speed/quality trade-off.

Full data: `data/ab_comparison_results.json`. Regenerate with `python3
scripts/run_ab_comparison.py` then `python3 scripts/analyze_cost_performance.py`.
