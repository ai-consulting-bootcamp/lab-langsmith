# FRAMES Evaluation Summary

Evaluated 20 FRAMES multi-hop QA examples with gpt-4o-mini (temperature 0), using gpt-4o-mini as an LLM-as-judge for correctness. The mean score was 0.150, the median was 0.000, and the pass rate at 0.5 was 15.0%. The lowest-scoring example was 042f3d1a-5dc0-41ac-a1d7-9bfacbb307bb (0.000); evaluator feedback: The model output provides an analysis that suggests Bronte Tower, with a height of 824 feet, would not be among the tallest buildings in New York City. However, it does not provide an accurate ranking or specific placement among the tall... The sample contains only 20 of the 824 test examples, and the target receives questions without retrieved Wikipedia article text, so results measure parametric answering rather than retrieval. Next, inspect low-scoring cases and test retrieval-augmented context before drawing conclusions about the full benchmark.

- Dataset: `FRAMES-Multi-Hop-QA-Evaluation` (20 examples)
- Experiment: [frames-gpt-4o-mini-20261123-2123-197c6eca](https://eu.smith.langchain.com/o/edab2a5d-9667-472c-96d6-b273cacdf453/datasets/dc312e9b-cd59-4b89-9214-3e1ccd0d80d7/compare?selectedSessions=cb28b7ef-282e-40cf-9659-509a81d7ce74)
- Scores: mean 0.150; median 0.000; pass rate 15.0%
- Detailed per-example scores: `frames_evaluation_scores.csv`
- Aggregate metrics: `frames_evaluation_metrics.json`
