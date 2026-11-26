# Evaluation summary

**Status on 26/11/2026: dataset and pipeline built and connected to LangSmith; the scored experiment did not finish because the free Gemini quota was used up.** The 12-example dataset `ai-act-gdpr-sme-qa-v1` is in LangSmith, the traced target function and the correctness evaluator (OpenEvals' `CORRECTNESS_PROMPT`, LLM-as-judge) are implemented, and `client.evaluate()` started; every model call then returned HTTP 429 on three Gemini models in a row (`gemini-3.5-flash`, `gemini-3-flash-preview`, `gemini-2.5-flash-lite`), because the same day's quota had been spent on the LLM-judges lab. So there are **no accuracy figures yet**, and I am not reporting any. The same command will produce them once the quota resets; the results go to `results/langsmith_results.json` and to the LangSmith experiment `gemini-flash-baseline-*`.

**Method (as built):** target = Gemini answering in at most three sentences, no compliance claims; evaluator = binary correctness judged against the reference answer; concurrency 1 for free-tier limits; results broken down by `topic` and `difficulty` metadata.

**What the analysis will look at:** accuracy overall, by topic and by difficulty; the wrong answers with the judge's comment; mean latency. Expected risk areas, based on the LLM-judges run: dates after the Digital Omnibus (example 4) and edge cases like legitimate interest for health data (example 10).

**Recommendations so far:**
- Run evaluations on a paid tier or a separate key, so one lab does not starve the next.
- Use a judge from a different model family to avoid self-preference bias.
- Keep the 12 examples as a regression set and re-run them whenever the law or the prompt changes.
