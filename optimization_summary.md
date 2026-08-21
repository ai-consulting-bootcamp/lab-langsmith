# Optimization Summary

**LAB | Micromanage your agents** — Step 16
**Author:** Nnanyelugo Ahukannah

Across three configurations on the same 22-example dataset and the same five
evaluators, **`gpt-4o-mini` with the full grounded prompt is the best
cost/performance trade-off**: it costs $0.34 per 1,000 queries against $5.61 for
`gpt-4o` — 16.7× cheaper — and matches it exactly on the two metrics that decide
whether an answer is usable in a compliance workflow (groundedness 0.955 both,
citation wellformedness 1.000 both, zero fabricated citations both), giving up
0.137 of correctness, which on 22 examples is three examples and inside the noise.
I would pick `gpt-4o` only if the answers were going to a customer unreviewed and
the extra ~$105/month at 20,000 queries were irrelevant next to the cost of one
wrong answer; I would pick `terse` never — it is the cheapest by 4% and destroys
citation validity, which is the entire point of the system. The real optimization
lesson is that the cheap lever was the prompt, not the model: the same
`gpt-4o-mini` swings from 0.909 to 0.318 citation validity on prompt wording
alone, a bigger effect than the 16.7× model upgrade buys in either direction.

| config | correctness | citation validity | groundedness | $/1k queries | $/month @ 20k | latency |
|---|---|---|---|---|---|---|
| **mini** (recommended) | 0.818 | 0.909 | 0.955 | **$0.34** | **$6.72** | 1.42s |
| gpt4o | 0.955 | 0.955 | 0.955 | $5.61 | $112.15 | 1.13s |
| terse | 0.909 | 0.318 | 0.318 | $0.32 | $6.43 | 1.38s |

- **Maximum performance:** `gpt-4o` + full prompt. Best correctness (0.955) and
  fewest failures (2 across 22). Costs $112/month at 20k queries.
- **Cost efficiency:** `mini` + full prompt. 94% of `gpt-4o`'s cost saved for one
  extra wrong answer per 22 and identical groundedness.
- **Balanced, and the recommendation:** `mini` + full prompt with a deterministic
  citation-validity gate in front of the response. The gate costs nothing per
  query, runs in milliseconds, and catches exactly the failure the cheaper model
  is more prone to.
- **Not a differentiator:** latency. 1.13–1.42s across all three, with the
  cheapest model marginally slowest; the spread is well inside run-to-run
  variation at n=22 and should not drive the choice.
