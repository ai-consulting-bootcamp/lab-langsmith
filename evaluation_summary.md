# Evaluation summary

We evaluated ShopCo's customer-support assistant on 15 English examples based on a fictional policy, with manually reviewed reference answers. The dataset covers shipping, returns, and missing information. The target used gpt-4o-mini with temperature=0 and max_tokens=250. OpenEvals correctness, judged by gpt-5.4-mini, passed 14/15 cases (93.3%); the 1–100-word rule passed 15/15 (100%), with no missing scores. Shipping and returns passed all cases, while missing information passed 2/3. The only rejected answer asked for clarification but omitted the return reason and proof of purchase. The judge also made a comment error: the model did ask about original packaging. We kept the original score under the single-response completeness criterion. This small, fictional, English-only dataset and single run do not establish production reliability or multi-turn performance; the length rule does not measure correctness. We recommend adding a clarification checklist and testing it on new ambiguous-return cases.

| Metric | Passed / Scored | Pass rate |
|---|---|---|
| Correctness (LLM judge) | 14/15 | 93.3% |
| Response length | 15/15 | 100% |

## Evidence

- [Results](outputs/results_main.csv)
- [Metrics](outputs/metrics_summary.csv)
- [Error analysis](outputs/error_analysis.csv)
- [Category chart](outputs/pass_rate_by_category.png)
- [Experiment screenshot](outputs/experiment_overview.png)

## LangSmith experiment

https://eu.smith.langchain.com/o/17e08f1d-f35a-4236-b995-58ab83d3b83b/datasets/d2e58858-c5c6-4212-a8f5-1b48516a1f99/compare?selectedSessions=fe23cce8-fa82-47c2-bcfe-171917718478
