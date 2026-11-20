# Evaluation summary

I evaluated **gpt-4o-mini** (temperature 0, context-only system prompt v1) as an assistant for newcomers **living in Germany**, using my own LangSmith dataset `living-in-germany-qa-v1`: **19 questions** in 6 categories (registration, work & taxes, transport, household costs, everyday life, health & safety), each with a short context written from official sources (figures checked November 2026) and a reference answer. It includes 3 trap questions not answered by the context and 2 calculation questions. Two evaluators scored the answers: an **LLM judge** (OpenEvals `CORRECTNESS_PROMPT`, gpt-5.4-mini) and a free **rule-based key-facts check**. The model reached **79 % correctness**. Its **biggest failure pattern was wrong refusals**: in all 4 failures it said "The context does not contain this information" although the answer was there (e.g. the minimum wage of 13.90 euros), most likely because our strict "if not in context, say so" instruction makes it over-cautious. The same caution explains why hard/trap questions scored 100 % but easy questions only 75 %; there were **no hallucinations**. **Limitations:** only 19 examples (one more failure moves the score by about 5 points); I wrote both the dataset and the prompt, using the same refusal phrase, which makes the trap test easier than real life; and the rule check was too strict once (it failed a correct yes/no answer). **Recommendation:** soften the refusal rule in a prompt v2 (e.g. "only say the information is missing if nothing in the context is relevant; answer yes/no questions directly"), rerun the same dataset, and check that the wrong refusals disappear without new hallucinations on the trap questions.

| Metric | Score |
|---|---|
| Correctness (LLM judge, gpt-5.4-mini) | 15/19 = **79 %** |
| Key facts match (rule-based) | 14/19 = **74 %** |
| Trap questions handled correctly | 3/3 = **100 %** |
| Wrong refusals | **4** (all failures) |
| Hallucinations | **0** |
| Hardest category | work & taxes (33 %) |

LangSmith experiment: https://eu.smith.langchain.com/o/3a0834ef-79bf-4dc2-80d3-2f65dcd44277/a/-/datasets/96bc0a98-d200-4547-94ab-9c46ad9d7d0f/compare?selectedSessions=a26327ee-9f7d-4e1b-8b69-2c839490c92e
