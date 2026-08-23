# Evaluation Summary

We evaluated gpt-4o-mini as a SaaS customer support agent against 20 tickets from the Bitext customer support dataset, covering account, subscription, payment, refund, and invoice categories. A Claude Haiku correctness judge compared each model response to the reference answer. Mean correctness score came out to 0.30. The biggest failure pattern showed up in the account category, where the model scored 0 out of 6. Reference answers in this dataset give long, scripted, step-by-step instructions. The model gives short, general answers that are accurate in substance but skip the procedural detail the judge expects, most visible on password reset and PIN retrieval questions. Refund and payment tickets scored better, likely because those questions have simpler, more direct answers. The main limitation is sample size: 20 examples is enough to spot a pattern, not enough to generalize with confidence, and only one model was tested. Recommendation: add explicit step-by-step formatting instructions to the target function's system prompt, then rerun the same evaluation to check if the score improves, particularly on account tasks.

## Metrics

| Category | Mean Score | Count |
|---|---|---|
| ACCOUNT | 0.00 | 6 |
| INVOICE | 0.33 | 3 |
| PAYMENT | 0.67 | 3 |
| REFUND | 0.50 | 6 |
| SUBSCRIPTION | 0.00 | 2 |
| **Overall** | **0.30** | **20** |


## Custom evaluator: actionability

Correctness alone doesn't catch whether a customer can actually act on a response. We built a second judge, actionability, scoring whether the response gives specific steps (named menus, fields, or actions) versus a vague pointer like "check your settings" or "reach out to us." Same model and prompt structure as the correctness judge, different criterion.

Ran both evaluators together on the same 20 examples (experiment `gpt-4o-mini-support-dual-606c9af0`). Correctness mean 0.35, actionability mean 0.35, but the two only agree on 50% of examples. Half the responses are correct but not actionable, or actionable but not strictly correct against the reference. That's a real gap correctness alone misses: a factually fine answer that still leaves the customer without a next step, and vice versa. For a support-agent use case, actionability is arguably the more useful signal, since customers act on instructions, not correctness scores.


**Model:** gpt-4o-mini (target), claude-haiku-4-5-20251001 (judge)
**Dataset:** saas-support-tickets, LangSmith
**Experiment:** gpt-4o-mini-support-ebd06ada