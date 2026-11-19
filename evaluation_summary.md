# Evaluation summary

We evaluated 22 grounded EU AI Act and GDPR Q&A examples across the EU AI Act and GDPR categories with gpt-4o-mini at temperature 0. The experiment used the LLM correctness evaluator and the deterministic reference-token F1 evaluator; 22 examples were flagged for review. The deterministic metric is reproducible and inexpensive, but token overlap can penalize valid paraphrases, while the LLM judge is model-dependent and neither metric replaces expert legal review. The biggest failure pattern should be confirmed by reviewing `outputs/error_analysis.csv`; the recommended next step is to inspect evaluator disagreements and add paraphrase-aware, expert-reviewed cases.

| Metric | Mean score | Pass rate (>= 0.5) | N |
|---|---:|---:|---:|
| correctness | 0.273 | 27.3% | 22 |
| reference_token_f1 | 0.203 | 0.0% | 22 |

Experiment prefix: `gpt-4o-mini-promptv1-llmcorrectness-tokenf1`
