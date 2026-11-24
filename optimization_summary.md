# Optimization summary

Among these two runs, `mini` (gpt-4o-mini) had the lowest observed cost per correct answer at the measured pass rate. The mini configuration is the sensible default when its accuracy meets the support quality bar; the full model is worth the extra cost when conditional questions or policy-boundary handling require the higher observed pass rate. This comparison is directional because it uses only 16 examples and one run per model.

| Config | Model | Pass rate | Cost / correct answer | Avg latency |
|---|---|---:|---:|---:|
| mini | gpt-4o-mini | 100.0% | $0.000087 | 1.00 |
| full | gpt-5.4-mini | 100.0% | $0.000492 | 1.11 |
