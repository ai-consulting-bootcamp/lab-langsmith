# W7D5_LAB_Micromanage_your_agents
- Week 7 / Day 5
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-23
---

# Chosen Domain
This project evaluates an LLM that answers factual, source-grounded questions about EU maritime environmental compliance. Each example provides a short source excerpt and a question; the expected answer is a concise answer supported only by that excerpt. The dataset contains author-created questions and reference answers based on publicly available official guidance, current as of August 2026.

# Evaluation Summary

I evaluated a context-grounded question-answering system for EU ETS and FuelEU Maritime requirements using a custom LangSmith dataset of 20 examples derived from official European Commission transport and climate-policy material. The target function used `gpt-4o-mini` to answer each question using only the provided context, and an LLM-as-a-judge correctness evaluator compared each output with its reference answer. The experiment achieved 19 correct answers out of 20, for a mean correctness score and accuracy of 0.95. Mean execution time was 0.815 seconds and median execution time was 0.712 seconds. The main failure occurred on a conditional 2030 on-shore-power question: although the context included the necessary condition, the model incorrectly returned the insufficient-context fallback. This shows that the model generally answered direct factual questions well but can miss date- and condition-based exceptions. The evaluation is limited by its small, custom dataset and by using correctness as the only quality measure. A next improvement would be to strengthen the system prompt so it explicitly checks dates, conditions, and exceptions before using the fallback response.

## Key Metrics

| Metric | Result |
|---|---:|
| Dataset size | 20 examples |
| Correct answers | 19 |
| Incorrect answers | 1 |
| Accuracy / mean correctness | 0.95 |
| Median correctness | 1.00 |
| Mean execution time | 0.815 seconds |
| Median execution time | 0.712 seconds |

## Supporting Files

- `dataset-Screenshot-2026-08-23-205349.jpg` — LangSmith custom dataset with 12 initial examples and metadata.
- `experiment-results-20-Screenshot-2026-08-23-215446-6.jpg` — 20-example experiment with overall 0.95 correctness.
- `failed-row-Screenshot-2026-08-23-223449-3.jpg` — pandas error analysis showing the failed conditional-requirement example.
- `experiment-results-Screenshot-2026-08-23-223432-4.jpg` — pandas summary metrics.