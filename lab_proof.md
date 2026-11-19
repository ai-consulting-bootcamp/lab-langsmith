# Lab proof: LangSmith evaluation workflow

## Scope

This lab evaluates a grounded Q&A target for EU AI Act and GDPR compliance material. The source dataset contains 22 examples: 10 EU AI Act examples and 12 GDPR examples, with foundational, intermediate, and advanced difficulty levels.

## What was implemented

1. Imported `qa_dataset.json` and validated the minimum example count, consistent schema, non-empty questions and answers, and category/difficulty distributions.
2. Created or reused the LangSmith dataset `eu-ai-act-gdpr-qa-v1`, uploading questions, reference answers, and metadata including category, difficulty, source file, section, and record ID.
3. Implemented the traced `gpt-4o-mini` target with temperature 0 and per-example error handling:

   ```python
   return {"answer": "", "error": str(e)}
   ```

4. Configured two evaluators:
   - `correctness_evaluator`: LLM-as-judge correctness feedback.
   - `rule_evaluator`: deterministic reference-token F1, with no additional LLM call.
5. Ran the Step 7 experiment with both evaluators and `max_concurrency=2`.
6. Added Part 5 analysis for aggregate metrics, category/difficulty comparisons, failed examples, charts, CSV exports, and `evaluation_summary.md`.
7. Added Part 6 comparison code for custom response-quality checks and model cost/performance analysis.

## Observed results

The saved evaluation results processed all 22 examples:

| Evaluator | Mean | Median | Pass rate (score ≥ 0.5) | Failed |
|---|---:|---:|---:|---:|
| LLM correctness | 0.273 | 0.000 | 27.3% | 16 |
| Deterministic token F1 | 0.203 | 0.207 | 0.0% | 22 |

The model comparison output recorded:

| Model | Mean correctness | Mean token F1 | Average latency |
|---|---:|---:|---:|
| `gpt-4o-mini` | 0.273 | 0.203 | 2.05 s/example |
| `gpt-5.4-mini` | 0.000 | 0.005 | 0.81 s/example |

The cost output currently reports zero because provider token prices were not configured in the environment. The Part 6 code supports `GPT4O_MINI_INPUT_USD_PER_M`, `GPT4O_MINI_OUTPUT_USD_PER_M`, `GPT54_MINI_INPUT_USD_PER_M`, and `GPT54_MINI_OUTPUT_USD_PER_M` environment variables.

## Analysis and interpretation

The strongest observed issue was insufficiently grounded answers: several responses declined to answer even when the reference contained the required course facts, while others gave broad GDPR or AI Act guidance that did not match the specific decision rule in the reference. This explains the low correctness and token-overlap scores. The deterministic evaluator is reproducible and useful for identifying weak lexical coverage, but it penalizes valid paraphrases and does not assess legal nuance. The LLM judge captures broader correctness but is itself model-dependent. Results should therefore be treated as diagnostic rather than legal certification.

The next improvement should be to provide the target with retrieved source context or the relevant reference material, then add expert-reviewed paraphrase cases and inspect disagreements between the LLM judge and deterministic evaluator. The 22-example sample is also small, so modest score differences should not be treated as statistically conclusive.

## Evidence files

- [`lab_langsmith.ipynb`](./lab_langsmith.ipynb) — executable implementation.
- [`qa_dataset.json`](./qa_dataset.json) — source dataset.
- [`evaluation_summary.md`](./evaluation_summary.md) — generated Step 10 report.
- [`outputs/evaluation_metrics.csv`](./outputs/evaluation_metrics.csv) — aggregate evaluator metrics.
- [`outputs/evaluation_results_with_metadata.csv`](./outputs/evaluation_results_with_metadata.csv) — scores joined with category and difficulty metadata.
- [`outputs/error_analysis.csv`](./outputs/error_analysis.csv) — failed examples for manual review.
- [`outputs/pass_rate_by_category.png`](./outputs/pass_rate_by_category.png) — category comparison chart.
- [`outputs/model_comparison_summary.csv`](./outputs/model_comparison_summary.csv) — model comparison results.
- [`outputs/cost_performance_summary.csv`](./outputs/cost_performance_summary.csv) — Part 6 cost/performance table.

To reproduce the reports, configure the required OpenAI and LangSmith credentials, run the notebook cells in order, and rerun the Part 5 and Part 6 report cells after the evaluations complete.
