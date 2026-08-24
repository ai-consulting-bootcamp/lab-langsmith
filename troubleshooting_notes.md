# Troubleshooting Notes

Real issues hit while building `langsmith_evaluation.ipynb`, and how they were resolved, following the categories in `instructions.md`'s Tips & Troubleshooting section.

## Target Function Errors

`gpt-5.6-luna` rejected `temperature=0` with `Unsupported value: 'temperature' does not support 0 with this model. Only the default (1) value is supported.` This is a reasoning-style model that only allows the default temperature. Fixed by tracking which models do not support temperature control (`MODELS_WITHOUT_TEMPERATURE_CONTROL`) and only passing `temperature=0` for models that accept it. This also means reproducibility differs across models in the A/B comparison, `gpt-4o-mini` and `gpt-4o` run deterministically at temperature 0, `gpt-5.6-luna` does not, which is noted in `optimization_summary.md`.

## Evaluation Failures (prompt formatting)

`CORRECTNESS_JUDGE_PROMPT.format(...)` raised a `KeyError` at first, since the prompt's example JSON block used literal `{` and `}` characters, which Python's `.format()` treats as replacement fields. Fixed by escaping them as `{{` and `}}` in the template. The same fix was applied to `TONE_JUDGE_PROMPT`.

## Results Analysis Challenges

`client.evaluate()`'s return value (`ExperimentResults`) does not document its internal structure. Rather than guessing, a diagnostic cell (`first_result = experiment_results._results[0]`) was added first to inspect the actual shape, `{'run': ..., 'example': ..., 'evaluation_results': {'results': [EvaluationResult(...)]}}`, before writing the real analysis code. This avoided writing analysis code against an assumed structure that might not have matched reality.

## Verifying an unfamiliar model

When asked to add `gpt-5.6-luna` to the comparison, its documentation page came from `developers.openai.com`, not the previously known `platform.openai.com` domain, so its legitimacy could not be assumed from the page alone. Verified two ways before trusting it: a real API call confirmed the model is callable, and following `platform.openai.com/docs/pricing`'s own redirect confirmed `developers.openai.com` is now OpenAI's real docs domain with matching pricing. Only after both checks passed was the model's pricing added to the notebook.

## Best practices followed

- Tested each function (`retail_chatbot`, `correctness_evaluator`, `tone_evaluator`) on 2-3 examples before running the full 18-example dataset, catching the temperature and formatting bugs above cheaply, before a full 18-call run.
- Used `temperature=0` wherever supported, for consistent, reproducible scoring.
- Reviewed results in the LangSmith UI directly (see `langsmith_ui_review.md`), not only through notebook print statements, to sanity-check that the judge's stated reasoning matched what the trace actually showed.
