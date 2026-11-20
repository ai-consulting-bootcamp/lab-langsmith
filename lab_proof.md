# Lab proof: LangSmith evaluation of a "Living in Germany" assistant

## 1. Code / workflow

All the code is in `living_in_germany_langsmith_evaluation.ipynb`:

```
19 examples (question + context + reference answer + metadata)
   → LangSmith dataset "living-in-germany-qa-v1" (EU)
   → target(): gpt-4o-mini, temperature 0, "answer only from the context"   [@traceable]
   → evaluators: correctness (LLM judge, gpt-5.4-mini) + key_facts_match (rule-based)
   → client.evaluate(..., experiment_prefix="gpt-4o-mini-promptv1")
   → results_main.csv → metrics, pass rate by category / difficulty, error analysis
```

## 2. One run with its input

- **Input:** the full dataset `living-in-germany-qa-v1` (19 examples) was run through the target with both evaluators.
- **Example input** (one of the 19):
  - **Question:** "What is the minimum wage in Germany right now?"
  - **Context:** "Since 1 January 2026, the statutory minimum wage in Germany is 13.90 euros gross per hour. On 1 January 2027 it will rise to 14.60 euros. In 2026, the earnings limit for a mini-job is 603 euros per month."
  - **Reference answer:** "13.90 euros gross per hour (since 1 January 2026)."

## 3. Evidence it produced

- **LangSmith experiment:** https://eu.smith.langchain.com/o/3a0834ef-79bf-4dc2-80d3-2f65dcd44277/a/-/datasets/96bc0a98-d200-4547-94ab-9c46ad9d7d0f/compare?selectedSessions=a26327ee-9f7d-4e1b-8b69-2c839490c92e
- **Screenshots:**
  - `outputs/screenshot_dataset.png`: dataset with inputs, reference outputs and metadata
  - `outputs/screenshot_experiment.png`: the experiment table with both scores for all 19 examples
  - `outputs/screenshot_trace.png`: the trace of the minimum wage question
- **Data:** `outputs/results_main.csv` (19 rows, 0 errors)

## 4. Final output

| Metric | Score |
|---|---|
| Correctness (LLM judge) | 15/19 = **79 %** |
| Key facts match (rule-based) | 14/19 = **74 %** |
| Trap questions handled correctly | 3/3 |
| Hallucinations | 0 |
| Hardest category | work & taxes (33 %) |

Full write-up: `evaluation_summary.md`. Chart: `outputs/pass_rate_by_category.png`.

## 5. One failure / limitation I hit

**Failure (wrong refusal):** for the minimum wage question above, the model answered *"The context does not contain this information. Please check with the responsible office."*, although the context clearly says 13.90 euros. The judge marked it incorrect and explained that the context states the value explicitly. The same pattern caused all 4 failures (minimum wage, tax ID, ICE, health insurance). Likely cause: the strict "if not in context, say so" instruction, plus "right now" against two years in the context.

**Limitation:** I wrote both the dataset and the prompt, using the same refusal sentence, so the trap questions are easier than real user questions. The rule-based check was also too strict once: it failed a correct Rundfunkbeitrag answer because the answer did not repeat "18.36".
