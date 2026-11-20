# Evaluation summary

I evaluated an EU AI Act risk classifier (gpt-4o-mini, temperature 0, JSON mode) on a custom LangSmith dataset of 24 AI use cases from 23 sectors with 5 labels (prohibited, high-risk, limited, minimal, needs-more-info); each input is a use-case description plus two passages from Regulation (EU) 2024/1689: the deciding provision and a near-miss. Three evaluators scored every answer: an OpenEvals correctness judge (gpt-5.4-mini, True/False), an exact match on the class, and the same judge prompt on a 1 to 10 scale. Correctness was 79%, class match 79% and the quality score averaged 8.2 (median 10.0); prohibited was the easiest class (100% class match) and needs-more-info the hardest (0%). The biggest failure pattern was overconfidence on missing details: all 3 vague cases were answered high-risk instead of needs-more-info (3 of the 5 failures; e.g. NMI-03 assumed life or health insurance, the only kind listed in Annex III point 5(c)), while the other two were a workplace emotion ban applied to a shopping mall (HR-04) and a missed Article 50(1) chatbot duty (LIM-05). Limitations: only 24 hand-written cases (one failure moves a pass rate by about 4 points), a single run, hand-picked passages instead of a real retriever, one LLM judge whose 1 to 10 scale has no defined anchors, and passages shortened from the official text. Recommendation: Add one prompt rule (answer needs-more-info when a missing fact would change the class, and check Article 50 after ruling out Annex III), re-run it as gpt-4o-mini-ctx-v2 on the same dataset so only the prompt changes, and then add more vague cases in a -v2 dataset, because 3 cases are too few to trust that class.

| Metric | Score |
|---|---|
| Correctness (LLM judge, True/False) | 79% (n = 24) |
| Class match (exact) | 79% (n = 24) |
| Quality score (1 to 10) | mean 8.2, median 10.0, range 1 to 10 |

- LangSmith dataset: [ai-act-risk-classifier-v1](https://smith.langchain.com/o/02ee3189-6ecc-4e1c-b911-6d5a92d2b83c/datasets/3d9fb028-b731-46af-9323-2158b7d3d09d)
- LangSmith experiment: [gpt-4o-mini-ctx-v1-ca7bd507](https://smith.langchain.com/o/02ee3189-6ecc-4e1c-b911-6d5a92d2b83c/datasets/3d9fb028-b731-46af-9323-2158b7d3d09d/compare?selectedSessions=c31cf717-253c-49d5-8747-3c212ed0a1cc)
- Charts and data: `outputs/` (quality_score_distribution.png, pass_rate_by_category.png, results_main.csv, metrics_summary.csv, failures.csv)
