# Lab | Week 7 | Day 5 | Micromanage your agents

## John Adams

## Part 4: Run Evaluation

### Step 7: Execute Evaluation Experiment

First run (generic openevals `CORRECTNESS_PROMPT`): `gpt-4o-mini-lead-scoring-0494fe3b`. Full raw results: `Outputs/gpt-4o-mini-lead-scoring-0494fe3b.csv`.

Rerun after tightening the evaluator prompt (see Step 9 note below): `gpt-4o-mini-lead-scoring-d70eabbf`.

Link: https://eu.smith.langchain.com/o/30e98d46-c47a-47c0-ad74-25a7832452c5/datasets/b294578b-5f9a-427c-83b9-542b448a3780/compare?selectedSessions=9c9defca-c69a-41b1-89ff-3fc2f620f30b

Full raw results: `Outputs/gpt-4o-mini-lead-scoring-d70eabbf.csv`. All 18 examples ran successfully in both runs (no errors).

### Step 8: Review Results in LangSmith UI

**Notes from review:**
- 18/18 examples completed with `status: success`, no errors, in both runs.
- First run correctness (generic QA-style judge prompt): 7/18 correct, mean 0.39.
- Rerun correctness (tightened binary-match judge prompt): 12/18 correct, mean 0.67.
- Cost and latency were effectively unchanged between the two evaluator prompts (~$0.00045 total, ~0.7s avg latency), the swing in score came entirely from the evaluator prompt, not the target model or predictions.

## Part 5: Analysis & Reporting

### Step 9: Analyze Results

**Note on evaluator prompt:** the first run used openevals' generic `CORRECTNESS_PROMPT`, built for open-ended QA (checks terminology, completeness, logical consistency). On our strict True/False task that rubric added noise, for example it could mark a correctly-matching boolean as wrong over phrasing. We rewrote it as a tight binary-match prompt (Step 6) and reran. The analysis below uses the corrected rerun (`d70eabbf`).

**Aggregate metrics:**
- Correctness: 12/18 correct (0.67 mean), on a task with a balanced actual split (9 True / 9 False).
- Confusion matrix (actual vs. predicted): 6 true negatives, 6 true positives, 3 false positives, 3 false negatives. No directional bias, errors are evenly split both ways. (Unchanged from the first run, the model's predictions never changed, only the judge's scoring did.)

**Categorical analysis by lead_source:**
- `sdr_outbound`: 5/6 correct (0.83)
- `inbound_marketing`: 4/6 correct (0.67)
- `partner_referral`: 3/6 correct (0.50)

**Error analysis:**
- `partner_referral` remains the weakest channel, but the corrected score (0.50) shows the earlier 0.00 was mostly a judge-prompt artifact, not a real model failure.
- Errors are balanced (3 false positives, 3 false negatives), so this isn't a lazy default-answer bug, the model is engaging with the input but performs modestly worse on partner-sourced leads.
- Likely cause: partner_referral leads may have a different touch/session pattern (e.g. fewer inbound touches by nature of being referred) that the prompt doesn't call out how to weigh, so the model may be applying inbound-marketing intuitions to a channel that converts differently.

**Performance insight:** the biggest single factor in our results was the evaluator prompt, not the model or the data. A generic LLM-as-judge rubric applied to a strict classification task can silently understate accuracy by roughly 28 points here. `lead_source` is a secondary, real signal, `partner_referral` leads are the hardest for the model to score correctly.

## Optional Part 2: Cost & Performance Optimization

### Step 14: Run A/B Comparison

Compared `gpt-4o-mini` against `gpt-4o` on the same dataset and evaluator (tightened binary-match prompt).

Experiment: `gpt-4o-lead-scoring-62598ef8`. Link: https://eu.smith.langchain.com/o/30e98d46-c47a-47c0-ad74-25a7832452c5/datasets/b294578b-5f9a-427c-83b9-542b448a3780/compare?selectedSessions=e7c533b2-ceb5-47d1-9860-c86574d142e2

Full raw results: `Outputs/gpt-4o-lead-scoring-62598ef8.csv`. All 18 examples ran successfully, no errors.

| Model | Correctness | Total cost (18 examples) | Avg latency |
|---|---|---|---|
| gpt-4o-mini | 0.67 (12/18) | $0.00045 | 0.75s |
| gpt-4o | 0.61 (11/18) | $0.00755 | 0.66s |

gpt-4o-mini scored higher and cost about 17x less than gpt-4o on this task. Latency was comparable. On this dataset there is no accuracy benefit to the larger model, gpt-4o-mini is the better choice on both quality and cost.

### Step 15: Analyze Cost-Performance Trade-offs

gpt-4o-mini is the better cost-performance choice on this dataset: higher correctness (0.67 vs. 0.61) at about 1/17th the cost of gpt-4o, with comparable latency (0.75s vs. 0.66s). There is no scenario in this run where gpt-4o's cost is justified, it did not improve accuracy over the smaller model. For a budget-priority use case, gpt-4o-mini is the clear choice. For a performance-priority use case, gpt-4o-mini is still the better choice here since it also scored higher, gpt-4o would only be worth revisiting if a larger, more diverse dataset showed it consistently outperforming on harder cases.

## Optional Part 1: Custom Evaluator Design

### Step 11: Design Custom Evaluator

Not attempted.

### Step 12: Run Evaluation with Custom Evaluator

Not attempted.

### Step 13: Document Custom Evaluator

Not attempted.
