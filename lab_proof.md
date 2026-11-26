# Lab proof — LangSmith custom dataset and evaluation

## 1. Code
[`langsmith_evaluation.py`](./langsmith_evaluation.py) — one script for Steps 2–9:
- Step 2: tracing on (`LANGSMITH_TRACING=true`), model calls decorated with `@traceable(run_type="llm")`;
- Steps 3–4: 12 examples uploaded as the dataset `ai-act-gdpr-sme-qa-v1` (see [`dataset_documentation.md`](./dataset_documentation.md));
- Step 5: traced target function `target()`;
- Step 6: correctness evaluator with OpenEvals' `CORRECTNESS_PROMPT`;
- Step 7: `client.evaluate(...)` with `experiment_prefix="gemini-flash-baseline"`;
- Step 9: scores saved to `results/langsmith_results.json`.

## 2. One run with its input
26/11/2026, student's Windows machine, VS Code terminal:

```
cd lab-langsmith-ai-act-gdpr-qa
pip install -r requirements.txt
python langsmith_evaluation.py
```

Input of the first evaluation call (example 2 of the dataset):
> Can a company use AI cameras to detect whether its employees are stressed at work?

## 3. Evidence it produced
1. First attempt: LangSmith refused the API key.
   ```
   langsmith.utils.LangSmithError: Failed to GET /datasets in LangSmith API.
   HTTPError('403 Client Error: Forbidden for url: https://eu.api.smith.langchain.com/datasets?limit=1&name=ai-act-gdpr-sme-qa-v1' ...
   ```
2. After fixing the key (see failures), the script got past the dataset step and reached the model calls, which all failed:
   ```
   gemini-3.5-flash: HTTP 429: { "error": { "code": 429, "message": "You exceeded your current quota, please check your plan and billing details. ..."
   gemini-3-flash-preview: HTTP 429: { "error": { "code": 429, "message": "You exceeded your current quota, ..."
   ```

## 4. Final output
- **Done:** dataset created in LangSmith (12 examples with topic and difficulty metadata); tracing configured; target, evaluator and experiment code implemented; [`evaluation_summary.md`](./evaluation_summary.md) written.
- **Not done yet:** a scored experiment. No accuracy numbers are reported, because none were produced. To be completed in this same PR when the Gemini quota resets.

## 5. Failures and limitations
1. **403 Forbidden from LangSmith, twice.** First, the script was pointed at the EU endpoint while the account is on the US site (`smith.langchain.com`); removing `LANGSMITH_ENDPOINT` fixed the URL. Second, the value saved in `.env` was not a real key (it began `lsLAN…` instead of `lsv2_`: text pasted by mistake). A one-line check that prints only the key's length and first 5 characters found it without exposing the secret.
2. **429 quota exhausted on every Gemini model tried** (`gemini-3.5-flash`, `gemini-3-flash-preview`, `gemini-2.5-flash-lite`): the free daily quota had been spent on the LLM-judges lab earlier that morning. Lesson: one free key shared by several labs is a single point of failure.
3. **No OpenAI wrapper.** The class notebook uses `wrap_openai`; the OpenAI-compatible endpoint timed out on this machine, so model calls are plain `requests` calls traced with `@traceable`.
4. **Optional parts (custom evaluator, A/B comparison) not attempted.**
