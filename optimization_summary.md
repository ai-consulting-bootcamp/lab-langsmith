# Optimization Summary

We compared gpt-4o-mini and gpt-4o on the same 13-example school order extraction dataset, using the same correctness and completeness evaluators. gpt-4o-mini won on every axis tested: correctness (0.62 vs 0.38), completeness (1.00 vs 0.96), latency (1.12s vs 1.28s P50), and cost (~$0.001 vs ~$0.015 for the 13-example run, roughly a 15x difference consistent with OpenAI's published per-token pricing). This is not a typical cost-vs-performance trade-off scenario — there is no configuration in this test where gpt-4o was worth its added cost, since it was both slower and less accurate on this specific extraction task. **Recommendation: use gpt-4o-mini for this task** in all scenarios (budget-constrained or performance-prioritized alike); we found no case favoring gpt-4o. Caveat: this is based on a 13-example dataset with some observed run-to-run score variance on gpt-4o-mini (0.54–0.62 across repeated runs at temperature 0) — the direction of the result (mini ≥ 4o) held consistently across all runs, but a larger dataset would be needed to rule out gpt-4o performing better on harder or more varied cases than the ones tested here.

**Comparison**
| Metric | gpt-4o-mini | gpt-4o |
|---|---|---|
| Correctness | 0.62 | 0.38 |
| Completeness | 1.00 | 0.96 |
| P50 Latency | 1.12s | 1.28s |
| Cost (13 examples) | ~$0.001 | ~$0.015 |


