# Optimization Summary (Steps 14–16)

## Status: Code implemented, not yet executed

`run_ab_comparison()` in `langsmith_evaluation.py` runs the same 15-example
dataset and correctness evaluator across `gpt-4o-mini` and `gpt-4o`, tracks token
usage per model, and estimates cost using the pricing table at the top of that
function. Run it with:

```bash
python langsmith_evaluation.py --ab
```

This produces `ab_comparison_results.json` with, per model: average
correctness, total prompt/completion tokens, estimated cost, and elapsed time.

**I have not run this**, so I'm not filling in a recommendation paragraph with
invented numbers. The pricing table in the script is a snapshot at time of
writing — verify current per-token pricing at
https://openai.com/api/pricing/ before trusting any cost figure it produces,
since OpenAI pricing changes periodically.

## What to fill in after running `--ab`

Once `ab_comparison_results.json` exists, replace this section with one short
paragraph naming:
- Which model had the best correctness score on this dataset
- The cost difference between the two models for this 15-example run
- Whether the cheaper model's accuracy was close enough to justify using it by
  default, and when you'd reach for the more expensive model instead (e.g. only
  for questions requiring exact standards citations)

| Model | Avg. correctness | Est. cost (15 examples) | Elapsed time |
|---|---|---|---|
| gpt-4o-mini | _(fill in)_ | _(fill in)_ | _(fill in)_ |
| gpt-4o | _(fill in)_ | _(fill in)_ | _(fill in)_ |
