# Lab | Week 7 | Day 5 | Micromanage your agents

## John Adams

## Optional Part 2: Cost & Performance Optimization

### Step 16: Create Optimization Report

I compared gpt-4o-mini against gpt-4o on the same 18-example lead-conversion dataset and the same corrected correctness evaluator. gpt-4o-mini scored 0.67 (12/18) at a total cost of $0.00045 for all 18 predictions, while gpt-4o scored lower at 0.61 (11/18) and cost $0.00755, about 17x more, with comparable latency (0.75s vs. 0.66s average).

On this task the larger model provided no accuracy benefit and cost substantially more, so gpt-4o-mini is the best cost/performance trade-off here: pick gpt-4o-mini by default for this type of structured binary classification task, and only consider a larger model if a future dataset shows it actually improving accuracy, since size alone did not help.

| Model | Correctness | Total cost (18 examples) | Avg latency |
|---|---|---|---|
| gpt-4o-mini | 0.67 (12/18) | $0.00045 | 0.75s |
| gpt-4o | 0.61 (11/18) | $0.00755 | 0.66s |
