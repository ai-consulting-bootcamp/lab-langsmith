# Lab proof — ShopCo support evaluation

## Scope and implementation

We evaluated a fictional online store's support assistant using
15 English questions about shipping, returns, and missing information.
Reference answers were drafted with AI assistance and manually reviewed
against the policy.

- [Completed notebook](02_langsmith.ipynb)
- [Source policy](data/shopco_policy.md)
- [Evaluation dataset](data/shopco_examples_v1.json)
- [Evaluation summary](evaluation_summary.md)

The notebook creates the LangSmith dataset, defines a traced target,
configures two evaluators, runs the experiment, and analyses results.

Target: gpt-4o-mini, temperature=0, max_tokens=250.
Evaluators: OpenEvals correctness with gpt-5.4-mini, and a deterministic
1–100-word response-length check.

## One observed run

**Input question:** Can I return my order?

**Input context:** The full ShopCo policy v1.0, linked above.

**Final model output:**

> I need more information to confirm if you can return your order.
> Could you please provide the delivery date and whether the product
> is unused and in its original packaging?

**Evaluation evidence:**

- Correctness: False.
- Response length: True.
- [Failed-case trace](outputs/experiment_failed_case.png)
- [Target trace](outputs/target_trace_shopco.png)
- [Experiment overview](outputs/experiment_overview.png)
- [Dataset screenshot](outputs/dataset_shopco.png)

## Failure and manual review

The answer requested clarification without confirming eligibility,
but omitted the return reason and proof of purchase.
We classified this as incomplete clarification under the
single-response completeness criterion.

The judge's explanation also contained an error: it suggested that
original packaging was missing, although the model asked about it.
We retained the original score and documented this issue.
This test does not evaluate collecting details over multiple turns.

## Overall results

| Metric | Passed / Scored | Pass rate |
|---|---|---|
| Correctness | 14/15 | 93.3% |
| Response length | 15/15 | 100% |

All 15 examples received scores from both evaluators.

- [Results](outputs/results_main.csv)
- [Results with metadata](outputs/results_with_metadata.csv)
- [Summary metrics](outputs/metrics_summary.csv)
- [Metrics by category](outputs/metrics_by_category.csv)
- [Metrics by difficulty](outputs/metrics_by_difficulty.csv)
- [Error analysis](outputs/error_analysis.csv)
- [Category chart](outputs/pass_rate_by_category.png)

## Limitations and next step

This was one run on 15 fictional, English-only cases.
The length check does not measure correctness, and the judge
requires human review. These results do not establish production
reliability.

Next step: add a clarification checklist and evaluate it on new
ambiguous-return cases. This improvement has not yet been tested.

## LangSmith experiment

[Open the experiment](https://eu.smith.langchain.com/o/17e08f1d-f35a-4236-b995-58ab83d3b83b/datasets/d2e58858-c5c6-4212-a8f5-1b48516a1f99/compare?selectedSessions=fe23cce8-fa82-47c2-bcfe-171917718478)