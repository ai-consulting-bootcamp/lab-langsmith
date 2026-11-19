# Optimization summary

I compared three configurations of the EU AI Act risk classifier on the same 24-case LangSmith dataset with the same evaluators: A (gpt-4o-mini, prompt v1, baseline), B (gpt-5.4-mini, prompt v1, model change) and C (gpt-4o-mini, prompt v2 with a needs-more-info and Article 50 rule, prompt change). B-gpt-5.4-mini-v1 had the highest class match and C-gpt-4o-mini-v2 the lowest cost per correct answer. The best trade-off for this use case is B (gpt-5.4-mini): it got 96% of the classes right (23 of 24, including both hard scope traps) for $0.81 per 1,000 cases, and the $0.67 it costs more than C per 1,000 cases is negligible next to the cost of one wrong compliance classification. Pick B when the class goes to a client or decides obligations without a human check, C (gpt-4o-mini + prompt v2, 88%, cheapest per correct answer) for high-volume first screening that a person reviews, and A no longer, because C beats it at almost the same cost; the next test is B with prompt v2 plus a rule for the legal basis of needs-more-info answers, aimed at NMI-03, the case all three configs fail. Caveats: with 24 cases a gap of 1 to 2 correct answers (4 to 8 points) can be luck, B ran at default sampling and is judged by its own model family (class match is unaffected), and costs use OpenAI list prices checked on 19 Nov 2026 for the target calls only.

| Config | Model | Prompt | Class match | Correctness | Quality (mean) | Cost / 1,000 cases | Cost / 1,000 correct answers | Avg latency |
|---|---|---|---|---|---|---|---|---|
| A-gpt-4o-mini-v1 | gpt-4o-mini | v1 | 79% | 79% | 8.2 | $0.13 | $0.16 | 1.18 s |
| B-gpt-5.4-mini-v1 | gpt-5.4-mini | v1 | 96% | 92% | 9.3 | $0.81 | $0.85 | 1.16 s |
| C-gpt-4o-mini-v2 | gpt-4o-mini | v2 | 88% | 88% | 8.6 | $0.14 | $0.16 | 1.19 s |

LangSmith experiments: [A-gpt-4o-mini-v1](https://smith.langchain.com/o/02ee3189-6ecc-4e1c-b911-6d5a92d2b83c/datasets/3d9fb028-b731-46af-9323-2158b7d3d09d/compare?selectedSessions=c9c541cc-d56f-462b-96ce-45f6812c818d), [B-gpt-5.4-mini-v1](https://smith.langchain.com/o/02ee3189-6ecc-4e1c-b911-6d5a92d2b83c/datasets/3d9fb028-b731-46af-9323-2158b7d3d09d/compare?selectedSessions=a1656a6d-e791-438b-b14a-a254eea5588b), [C-gpt-4o-mini-v2](https://smith.langchain.com/o/02ee3189-6ecc-4e1c-b911-6d5a92d2b83c/datasets/3d9fb028-b731-46af-9323-2158b7d3d09d/compare?selectedSessions=3f893a5d-2d92-4ff6-8719-9c1b57f27db4)

Data and chart: `outputs/ab_comparison.csv`, `outputs/cost_vs_performance.png`
