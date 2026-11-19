# LangSmith review notes

The Experiments tab shows both `clouddesk-baseline-20261119T162817Z-3fd7a8e7` and `clouddesk-policy_aware-20261119T162817Z-08dc032b`, with 20/20 target runs and zero target errors. The interface includes feedback, latency, token and cost charts.

The initial experiment overview displayed partial feedback coverage after all target calls had finished. For example, policy-aware correctness was shown as 0.82 over 17 evaluated cases. This was an aggregation delay: the individual feedback records already contained all 60 scores per experiment. Subsequent aggregate read-back confirmed 20 scored cases for every metric: baseline correctness/citation coverage/groundedness = 0.85/0.95/0.90, and policy-aware = 0.80/0.90/0.85. The final counts and averages are recorded in [aggregate verification](../outputs/ui_aggregate_verification.json). No new experiments or replacement feedback were created to resolve the delay.

S04 and S07 are useful examples of answers that quote policy IDs but violate eligibility or billing conditions. S19 is the key judge disagreement: the response deadline is wrong, correctness fails, and groundedness passes. The exact answers, reference outputs and judge comments are retained in [flagged examples](../outputs/flagged_examples.csv), with selected nested traces under [trace evidence](../outputs/traces/). The [failure analysis](failure_analysis.md) explains the policy checks and distinguishes judge errors from target errors.

The complete dataset fields were verified through the API, and 40 target runs plus 120 feedback scores were read back and matched to local exports. These read-back checks are recorded separately from the interface observations, so partial UI aggregation does not silently change the analysis denominator.

## Captured interface evidence

| Screenshot | Observation |
|---|---|
| [Experiment overview](../outputs/screenshots/experiments_overview.png) | Both experiments have 20/20 runs. Baseline correctness is 0.85, citation coverage 0.95 and groundedness 0.90. Policy-aware scores are 0.80, 0.90 and 0.85 respectively. Both error rates are 0%. |
| [Dataset examples](../outputs/screenshots/dataset_examples.png) | All 20 rows appear with inputs, reference outputs, case IDs, categories, difficulty, policy IDs and reference rationales. |
| [S19 feedback](../outputs/screenshots/baseline_S19_feedback.png) | The baseline target has a nested GPT-4o mini call. Feedback is citation coverage 1.00, correctness 0.00 and groundedness 1.00. The output records 353 prompt tokens, 83 completion tokens, a normal stop and no error. Collapsed answer fields are available in full in the JSON trace export. |
| [S19 attributes](../outputs/screenshots/baseline_S19_attributes.png) | Case S19 is a hard API/support example. Attributes confirm temperature 0, GPT-4o mini target, GPT-5.4 mini judge, dataset v1, EU endpoint and enabled tracing. |

The screenshots preserve the interface as captured, without visual edits. Latency cards in the overview display P50/P99, whereas the optimization summary reports mean target latency; these are different statistics. The displayed Git revision identifies the checkout at execution time; exact prompts and settings are retained in the archived run manifest.
