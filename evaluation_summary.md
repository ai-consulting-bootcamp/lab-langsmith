# Evaluation summary

The credential-free validation exercised the full 12-case scoring path with clearly labelled fixed fixtures—not live model outputs—and achieved 9/12 exact strategy matches (75%) and 12/12 format-compliant responses (100%); accuracy was 100% for AUTOMATED cases, 75% for HUMAN cases, and 50% for HYBRID cases. The main failure pattern was underestimating mixed requirements: the fixtures missed cases where deterministic checks provide coverage but regulated, creative, or fairness-sensitive judgments still require human review. The principal limitation is that no LangSmith/OpenAI keys were available in the execution environment, so latency, token cost, judge scores, and an experiment URL remain pending rather than being fabricated. The recommended next step is to run the supplied one-command LangSmith experiment, review all HYBRID disagreements first, and calibrate the semantic judge against human decisions before scaling it.

| Metric | Offline validation |
|---|---:|
| Cases | 12 |
| Exact strategy accuracy | 75% |
| Format compliance | 100% |
| Failed cases | `case_003`, `case_005`, `case_012` |

