# Evaluation Summary

A baseline evaluation of `gpt-4o-mini` was conducted on 15 curated clinical-trial eligibility screening examples derived from the NCBI TrialGPT Criterion Annotations dataset, covering inclusion and exclusion criteria, missing and ambiguous information, multi-criterion cases, temporal reasoning, boundary values, medical terminology, mixed evidence, and not-applicable cases. Performance was measured using deterministic criterion-level label accuracy and a custom LLM-as-judge correctness evaluator using `gpt-4.1-mini`. Mean label accuracy was **0.473**, with **6/15 (40%)** examples achieving fully correct labels, while the LLM judge also marked **6/15 (40%)** responses as fully correct. The clearest failure pattern was systematic over-prediction of `NOT MET`, especially for exclusion criteria, where the model frequently failed to apply the project-specific convention that an absent exclusion condition should be classified as `MET`; uncertainty and not-applicable cases also caused errors. Results should be interpreted cautiously because the dataset is small and several categories contain only one or two examples. The recommended next step is to rerun the same evaluation with a stronger target model and/or an improved prompt, using the unchanged dataset and evaluators so that performance can be compared directly.

## Key Metrics

| Metric | Result |
|---|---:|
| Examples | 15 |
| Mean label accuracy | 0.473 |
| Median label accuracy | 0.500 |
| Fully correct label cases | 6/15 (40%) |
| LLM-judge correctness | 6/15 (40%) |
| Most frequent error | `MET → NOT MET` (5 times) |