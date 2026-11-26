# Evaluation summary

I evaluated `gpt-6-luna` as a policy Q&A assistant on the custom LangSmith dataset [northwind-policy-qa-v1](https://smith.langchain.com/datasets/583cfc84-2536-4ee0-9e5d-25f19539ec66) (14 questions over two fictional operational-risk policies, including 2 out-of-scope questions that should be refused). The target function puts both policies into the system prompt and must cite the section; outputs were scored by an LLM-as-judge correctness evaluator (`gpt-6-luna`, compares key facts with the reference answer) and a code-based `grounded_citation` evaluator (correct section cited, or "Not covered" for out-of-scope). Correctness was **93% (13/14)** and grounded citation **100%**; the weakest category was **incident** (88%). Correctness failures: Q08 (details below). Limitations: 14 examples is a small sample, the judge comes from the same model family as the target (possible self-preference bias), and context stuffing only works because the corpus is tiny. Recommendation: add more multi-condition and out-of-scope questions and use a different judge model before relying on the score.

- Experiment: [policy-qa-gpt-6-luna-c33e9367](https://smith.langchain.com/o/a812ed56-6ad5-45f3-812e-9f43655131d1/projects/p/4a03fffa-1d9f-4ffa-9a9d-9d05065c2586)
- Median latency per question: 1.16 s

| Category | n | correctness |
|---|---|---|
| incident | 8 | 88% |
| out_of_scope | 2 | 100% |
| vendor | 4 | 100% |

| Difficulty | n | correctness |
|---|---|---|
| easy | 6 | 100% |
| hard | 3 | 67% |
| medium | 5 | 100% |

| ID | Question | Answer | correctness | citation | Judge comment |
|---|---|---|---|---|---|
| Q08 | A payment outage lasted 90 minutes and affected 500 clients, with no data breach. How should it be classified? | It should be classified as a Significant incident because it affected fewer than 1,000 clients and lasted under 4 hours (Incident Management Policy, Section 2). | 0 | 1 | The classification as Significant is correct, and the client count is below 1,000. However, the reference sets the outage threshold at under 2 hours, not under 4 hours, so the answer gives an unsupported criterion. |

Full per-example results: [results/eval_results.csv](results/eval_results.csv)
