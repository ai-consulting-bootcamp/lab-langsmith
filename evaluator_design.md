# Evaluator design

The experiment uses three complementary evaluators:

| Evaluator | Type | Measures |
|---|---|---|
| `strategy_exact_match` | Deterministic code | Whether the predicted enum exactly matches the reference strategy |
| `format_compliance` | Custom deterministic code | Whether the enum is valid and the rationale contains 1–45 words |
| `semantic_correctness` | OpenEvals LLM-as-judge | Whether the complete strategy and rationale are correct relative to the scenario and reference answer |

Exact match is intentionally strict and cheap. It makes label accuracy reproducible but cannot recognize a sound rationale attached to an incorrect label or diagnose *why* a choice failed. Format compliance checks the response contract independently so a semantically plausible but unusable response is visible. The semantic judge adds nuance by comparing the model output with the reference output, but it is not treated as ground truth because an LLM judge can be biased or inconsistent.

The custom evaluation dimension is **format compliance**. It is implemented in `src/run_evaluation.py` without another model call, making the result deterministic and cost-free. Together, the three metrics separate classification accuracy, interface reliability, and semantic quality.

