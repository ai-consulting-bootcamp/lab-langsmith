# Optimization Summary

I compared 3 models on the same 18-example retail chatbot dataset with `correctness_evaluator`: `gpt-4o-mini` (16/18, 89%, $0.0012 total, $0.000075 per correct answer), `gpt-4o` (17/18, 94%, $0.0186 total, $0.001094 per correct answer), and `gpt-5.6-luna` (18/18, 100%, $0.0022 total, $0.000122 per correct answer). `gpt-5.6-luna` is the best cost-performance trade-off here: it scored perfectly, at less than one eighth of `gpt-4o`'s cost, and only slightly more than `gpt-4o-mini`. I would pick `gpt-4o-mini` only under a strict budget ceiling where the 2 remaining error categories (policy accuracy, tone edge cases) are acceptable risk. I would pick `gpt-4o` only if `gpt-5.6-luna` were unavailable, since it is both more expensive and less accurate here. For this scenario, `gpt-5.6-luna` is the clear default choice, pending a larger test set to confirm 100% correctness holds beyond 18 examples, and one implementation note: `gpt-5.6-luna` does not support `temperature=0`, only the default, which should be accounted for in any reproducibility expectations.

| Model | Correct | Pass rate | Cost (18 examples) | Cost per correct |
|---|---|---|---|---|
| gpt-5.6-luna | 18/18 | 100% | $0.0022 | $0.000122 |
| gpt-4o-mini | 16/18 | 89% | $0.0012 | $0.000075 |
| gpt-4o | 17/18 | 94% | $0.0186 | $0.001094 |
