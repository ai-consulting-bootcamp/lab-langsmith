# Evaluation Summary

## Overview

This evaluation assessed GPT-4o-mini on 20 question-answer pairs covering all ten categories of the OWASP GenAI LLM Top 10 (2026). The target model used temperature=0 and was evaluated using two methods: an LLM-as-a-Judge correctness evaluator powered by GPT-5-mini and a deterministic keyword-overlap evaluator with a 25% threshold. The LLM Judge reported a 55% pass rate, while keyword overlap reached 95%. Manual analysis of the nine failed correctness evaluations identified six factual errors, two incomplete answers, and one hallucination. The dominant failure pattern involved incorrect OWASP terminology, classifications, and specific technical details. The small dataset, uneven category distribution, and potential limitations of automated judging restrict the generalizability of these findings. The recommended next step is to improve factual grounding using the official OWASP 2026 source material, followed by re-evaluation on a larger and more balanced dataset.

## Evaluation Metrics

| Metric | Result |
|---|---|
| Dataset size | 20 examples |
| OWASP risk categories covered | 10 |
| Target model | GPT-4o-mini |
| Judge model | GPT-5-mini |
| Correctness pass rate | 55% (11/20) |
| Keyword overlap pass rate | 95% (19/20) |
| Failed correctness evaluations | 9 |
| Wrong fact | 6 |
| Incomplete answer | 2 |
| Hallucination | 1 |

## Key Observations

- Risk Definition achieved 100% correctness (2/2).
- Risk Factors had the lowest pass rate at 25% (1/4).
- Easy questions achieved 100%, medium questions 30%, and hard questions 66.7%.
- Keyword overlap frequently accepted answers that the LLM Judge rejected.
- Manual review found no clear judge mistakes among the nine failed cases, but reference accuracy was not independently verified.

## LangSmith Experiment

https://eu.smith.langchain.com/o/30676eb8-0d5d-42d8-aa84-ca8c16dce2c5/datasets/f36ce8bb-1f79-441f-9c59-b78ca1a6929d/compare?selectedSessions=68548a5f-d128-4510-859b-3b6574eca64c
