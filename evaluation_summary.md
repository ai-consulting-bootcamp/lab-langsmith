# Lab | Week 7 | Day 5 | Micromanage your agents

## John Adams

## Part 5: Analysis & Reporting

### Step 10: Create Evaluation Report

I evaluated gpt-4o-mini on a B2B SaaS lead-conversion prediction task: given a lead's 30-day engagement snapshot (industry, region, lead source, touch/session activity, estimated deal value), predict whether it converts within 90 days. The dataset was 18 real leads sampled from the LeadForge Lead Scoring Intro v1 dataset (Kaggle), stratified across three lead sources and both outcomes. Correctness was scored with an LLM-as-judge, first using openevals' generic QA-style `CORRECTNESS_PROMPT`, then a tightened binary-match prompt written specifically for this True/False task after the generic prompt appeared to be under-scoring correct answers. 

With the corrected prompt, gpt-4o-mini scored 12/18 correct (0.67), with errors balanced between false positives and false negatives (no systematic over- or under-prediction), and the weakest performance on `partner_referral` leads (0.50 vs. 0.83 for `sdr_outbound`). The single biggest finding was that evaluator prompt design mattered more than the model or the data: the generic rubric scored the same predictions at 0.39, a 28-point swing from prompt wording alone. 

Limitations: 18 examples is a small sample for reliable per-category conclusions, the dataset is fully synthetic (not real customer data), and the target function uses a single zero-shot prompt with no few-shot examples or fine-tuning. 

Recommendation: before trusting any correctness number from an LLM-as-judge, verify the judge prompt actually matches the output format being scored (open-ended vs. exact-match), since a mismatched rubric can silently misstate model performance by a wide margin.

- Dataset: 18 examples, LeadForge Lead Scoring Intro v1 (Kaggle), balanced across `lead_source` and outcome
- Model: gpt-4o-mini, temperature 0, zero-shot system prompt
- Correctness (corrected binary-match judge): 0.67 (12/18)
- Correctness (generic QA judge, same predictions): 0.39 (7/18)
- Weakest category: `partner_referral` (0.50)
- Strongest category: `sdr_outbound` (0.83)
- Full results and links: see `evaluation_results.md`
