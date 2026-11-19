# Optimization summary

The baseline was the best observed cost/performance trade-off: 85% correctness at an estimated USD 0.000096 per correct answer and 1.18 seconds mean target latency, versus 80%, USD 0.000132 and 1.40 seconds for the policy-aware prompt. The longer prompt cost 28.8% more per example and produced one additional correctness failure, so I would retain the baseline for a supervised prototype and choose the policy-aware variant only if a larger held-out comparison demonstrated an offsetting benefit on critical policy cases. Neither result justifies unsupervised billing decisions. These are two prompt configurations of the same model, with a single paired run of 20 synthetic cases; the observed difference does not establish a statistically reliable quality advantage. Costs below cover target inference only, calculated from actual returned token usage and published rates; judge and smoke-test costs are recorded separately.

| Configuration | Correctness | Target cost, 20 cases (USD) | Cost/example (USD) | Cost/correct answer (USD) | Mean latency |
|---|---:|---:|---:|---:|---:|
| Baseline | 85% | 0.00163875 | 0.00008194 | 0.00009640 | 1.18 s |
| Policy-aware | 80% | 0.00211035 | 0.00010552 | 0.00013190 | 1.40 s |

[Full cost and token table](outputs/comparison_summary.csv) · [Suite costs including judges](outputs/suite_costs.csv) · [Pricing method](docs/evaluators.md#cost-and-timing)
