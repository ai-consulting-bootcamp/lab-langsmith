# Optimization Summary

For this coaching-assistant task, `gpt-4o-mini` is the clear best cost/performance trade-off:
it scored higher on correctness (0.73 vs 0.53), was comparably warm (2.13 vs 2.20 — not a
meaningful gap), responded faster (0.81s vs 0.91s P50), and cost 16x less ($0.0006 vs $0.0096
for the full 15-example run) than `gpt-4o`. Counter-intuitively, the larger, more expensive
model performed *worse* on correctness — its failures consistently embedded subtle suggestions
("what might be a first step you could take," "what might be some ways to gain...") that violate
the "no advice" rule, likely because `gpt-4o`'s stronger general helpfulness instinct pushes it
toward solution-oriented phrasing even when explicitly instructed not to. I would pick
`gpt-4o-mini` for this exact task in production, without reservation — there is no scenario in
this comparison where `gpt-4o`'s extra cost buys anything. I would only reconsider `gpt-4o` if
the system prompt were redesigned to more strongly suppress its suggestion-making tendency (e.g.
few-shot examples of purely reflective questions), since its warmth score suggests it isn't
meaningfully more empathetic either — the cost premium simply isn't justified here.

| Model | Correctness | Warmth | Cost (15 ex.) | Latency (P50) |
|---|---|---|---|---|
| gpt-4o-mini | 0.73 | 2.13 | $0.0006 | 0.81s |
| gpt-4o | 0.53 | 2.20 | $0.0096 | 0.91s |
