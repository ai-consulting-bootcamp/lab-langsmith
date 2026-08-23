# Optimization Summary

Compared gpt-4o-mini and gpt-4o on the same 15-example real-data extraction
task (identical prompt, temperature 0, identical evaluator); both models
scored a perfect 1.00 average correctness, with gpt-4o-mini completing the
run in comparable wall-clock time (6.23s vs 5.08s for 15 calls) at roughly
15-17x lower per-token cost ($0.15/$0.60 per 1M input/output tokens vs
$2.50/$10.00 for gpt-4o, publicly listed OpenAI pricing at time of testing).
Since this specific extraction task is mechanical -- required fields are
stated verbatim in the input text -- the larger model provides no accuracy
benefit to justify its cost here: **gpt-4o-mini is the correct production
choice for this task**, and gpt-4o would only be worth considering if a
future, harder version of the dataset (ambiguous multi-party notices,
inconsistent formatting) showed a real accuracy gap favoring the larger
model, which this comparison did not test for.
