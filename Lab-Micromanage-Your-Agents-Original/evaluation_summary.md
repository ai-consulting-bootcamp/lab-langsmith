# TenderAI Evaluation Summary

The TenderAI evaluation tested `gpt-4.1-mini` on a custom LangSmith dataset of 15 tender requirements using a traced target function and an exact-match correctness evaluator. The LangSmith experiment `TenderAI-gpt-4.1-mini-10852ed7` processed all 15 examples and achieved an average correctness score of **0.40 (40%)**, with **6 correct classifications and 9 incorrect classifications**. The main failure pattern was a strong tendency to classify requirements as `INSUFFICIENT`, producing false negatives for several requirements expected to be `SUPPORTED`, particularly renewable-energy capabilities and experience. The experiment also recorded latency and token usage, with a reported median latency of approximately **0.745 seconds**. These results show that the evaluated prompt/model configuration is not reliable enough for production tender classification without additional company evidence, improved prompting, or a stronger evaluation/grounding approach. A key limitation is that the target function evaluated the requirement text without providing the underlying TenderAI knowledge-base evidence; therefore, the results measure classification behavior rather than full evidence-grounded tender assessment.

* Dataset: `TenderAI-Requirement-Evaluation-v1`
* Examples: 15
* Model: `gpt-4.1-mini`
* Evaluator: Exact-match correctness
* Accuracy: 40% (6/15)
* Median latency: ~0.745 seconds
* Experiment: `TenderAI-gpt-4.1-mini-10852ed7`
