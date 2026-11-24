# Lab proof

## Workflow

The notebook builds a 16-example LangSmith dataset from [`policy.md`](./policy.md), with `question` and full policy `context` as inputs, `answer` as the reference output, and category/difficulty/source metadata. The traced target uses `gpt-4o-mini`, temperature 0, and a grounded support prompt. The primary experiment uses a `gpt-5.4-mini` correctness judge plus a deterministic keyword/numeric-constraint evaluator.

## Evidence from the completed run

- Dataset: `northstar-support-policy-v1`, verified with 16 stored examples.
- Primary experiment: [LangSmith experiment](https://eu.smith.langchain.com/o/d3d98841-0ad5-4b5f-846b-5f970118901c/datasets/218c778f-1d98-44b2-a246-c997678bdc16/compare?selectedSessions=bc3b40dd-4236-4b05-a689-3725aa97112d).
- Custom evaluator experiment: [LangSmith comparison](https://eu.smith.langchain.com/o/d3d98841-0ad5-4b5f-846b-5f970118901c/datasets/218c778f-1d98-44b2-a246-c997678bdc16/compare?selectedSessions=10e8ad25-adda-4814-b73d-8df4b88a7747).
- A/B experiments: `mini` and `full` links are printed in the executed notebook and their aggregate is in [`outputs/ab_metrics.csv`](./outputs/ab_metrics.csv).
- Primary output: `gpt-4o-mini` answered the example `Can I return an unopened item 20 days after delivery?` with the 30-day/full-refund policy answer; the judge marked it correct.

## Results

The LLM correctness judge passed 16/16 examples (100%). The deterministic evaluator passed 12/16 (75%) because it intentionally penalizes some valid paraphrases and wording differences. The custom grounded-helpfulness evaluator correctly surfaced a borderline answer in its hand-made test: an answer that said express shipping “may cost extra” received 0.7 because it omitted the exact $18 surcharge. The completed A/B run found both models at 100% on this small set; `gpt-4o-mini` cost about $0.000086 per correct example versus about $0.000492 for `gpt-5.4-mini`.

## Limitation

The judge had no failed examples to inspect in the primary run, so the rule-evaluator disagreements are the useful error-analysis cases. The sample is only 16 fictional examples, and the price comparison uses one run per model. A dataset v2 should add more multi-condition, ambiguous, and genuinely unsupported questions. The LangSmith links above are the trace/experiment evidence; UI screenshots were not captured in this automated run.
