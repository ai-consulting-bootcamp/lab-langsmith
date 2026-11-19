# Evaluation summary

I evaluated gpt-4o-mini (temperature 0) as a Q&A assistant for the EU AI Act, using my own dataset `eu-ai-act-qa-v1`: 19 business questions across 6 categories (prohibited practices, high-risk, transparency, penalties/obligations, scope/timeline, unanswerable), with 6 "hard" trap cases (exceptions, the SME fine rule, and questions the context cannot answer). Each input includes a short summary of the relevant article as context. Two evaluators were used: an LLM judge (gpt-5.4-mini, OpenEvals correctness prompt) and a rule-based check that the answer cites the same article as the reference. In the final run the model scored 100% on both (19/19). Across three runs correctness was 100%, 95% and 100%: in one run the model gave an incomplete answer on a multi-part rule (for an HR form-checking tool it applied the Article 6(3) exception but omitted the Article 6(4) duty to document the assessment), and the same question passed in the other runs. Limitations: 19 examples is small (one failure = about 5 points), the context summaries already contain most of the answer so the dataset is too easy to separate good from great, and the rule-based check verifies citations, not completeness. Testing also caught a substring bug in my rule-based evaluator, which I fixed before the final runs. **Recommendation:** build a `-v2` with more multi-part and borderline questions (where the context is close but not sufficient), and run each experiment more than once before comparing results.

| Metric | Final run | Range over 3 runs |
|---|---|---|
| Correctness (LLM judge) | 100% (19/19) | 95–100% |
| Cites correct article (rule-based) | 100% (19/19) | 100% |

LangSmith experiment (final run): https://eu.smith.langchain.com/o/6a443e3e-a646-46d2-8426-409f0215ab77/datasets/516fe224-9104-44fa-99fd-fd6dfd3bf85a/compare?selectedSessions=eefea85a-9afb-4420-b164-c0021d1d4f89
