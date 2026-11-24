# Evaluation summary

The `northstar-support-policy-v1` dataset contains 16 customer-support questions from `policy.md` across 5 categories, including hard conditional and policy-boundary cases. The target used gpt-4o-mini with temperature 0 and a grounded system prompt; a stronger openai:gpt-5.4-mini correctness judge and a deterministic keyword/numeric-constraint check were evaluated. The LLM judge pass rate was 100.0%, versus 81.2% for the rule evaluator; the rule diagnostic found `policy-boundary` easiest and `support` hardest. Failures should be interpreted cautiously because this is a 16-example estimate and the keyword heuristic can disagree with valid paraphrases. The main recommendation is to review judge/rule disagreements and add more multi-condition and out-of-policy questions in dataset v2.

| Metric | Score |
|---|---|
| Correctness (LLM judge) | 100.0% |
| Keyword/numeric rule | 81.2% |
| Examples | 16 |

LangSmith experiment: https://eu.smith.langchain.com/o/d3d98841-0ad5-4b5f-846b-5f970118901c/datasets/218c778f-1d98-44b2-a246-c997678bdc16/compare?selectedSessions=7110b32c-9332-4b3d-b7cc-e3aedf35ba3b
