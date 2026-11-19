# Evaluation summary

I evaluated GPT-4o mini on 20 synthetic CloudDesk support questions across five balanced categories, using temperature 0, a 350-token completion limit, an OpenEvals correctness judge (GPT-5.4 mini), deterministic citation coverage, and a custom groundedness judge. The baseline passed correctness on 17/20 cases (85%), versus 16/20 (80%) for the policy-aware prompt; citation coverage was 95% versus 90%, and judged groundedness was 90% versus 85%, with no target or evaluator failures. Both configurations mishandled seat-minimum billing, renewal refund eligibility, and business-hour arithmetic; the longer prompt also incorrectly refused a three-member Team subscription. A policy audit found that the groundedness judge wrongly accepted Friday 20:00 as a four-business-hour response deadline, which should be Monday 12:00. The five calibration fixtures passed, but did not cover that failure. This small synthetic sample, one run per configuration, and same-provider judges limit generalization: the five-point correctness difference is one case, with a paired bootstrap interval of -15 to 0 points and exact McNemar p=1.00. My next step would be explicit billing and calendar calculations plus broader held-out boundary cases, rather than assuming more prompt text improves reliability.

| Metric | Baseline | Policy-aware |
|---|---:|---:|
| Correctness | 17/20 (85%) | 16/20 (80%) |
| Correctness 95% Wilson interval | 64.0%-94.8% | 58.4%-91.9% |
| Citation coverage | 19/20 (95%) | 18/20 (90%) |
| Groundedness, original judge scores | 18/20 (90%) | 17/20 (85%) |
| All three metrics pass | 17/20 (85%) | 15/20 (75%) |
| Target errors / missing evaluator scores | 0 / 0 | 0 / 0 |

[Baseline experiment](https://eu.smith.langchain.com/datasets/cb947ac6-2849-45de-854c-a589623941e0/compare?selectedSessions=ded79b54-4fb4-4472-b1ce-f6fe6e227850) · [Policy-aware experiment](https://eu.smith.langchain.com/datasets/cb947ac6-2849-45de-854c-a589623941e0/compare?selectedSessions=5ddbec33-d0ff-4ea4-9966-9067fa05bf6c) · [Failure analysis](docs/failure_analysis.md)
