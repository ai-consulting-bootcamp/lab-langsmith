# LangSmith Custom Evaluation Lab — AI Coaching Assistant

## Domain

An AI coaching assistant for employee goal-setting and performance conversations, modeled on
ICF-style coaching (reflective open questions, no advice-giving). Each dataset example is a
single coaching turn — an employee's message (with optional prior conversation history) paired
with an expected single-question coach response. The dataset mixes single-turn and multi-turn
(2-3 turn) threads across five categories: goal-setting, clarity, motivation,
feedback-resistance, perspective.

## Approach

1. Built a 15-example dataset by hand, structured for multi-turn context (`conversation_history`
   + `latest_message` as inputs, `expected_output` as the reference).
2. Uploaded it to LangSmith (EU region) as `coaching-eval-dataset`.
3. Implemented a target function (`gpt-4o-mini`, ICF-style system prompt) that generates a coach
   response given the inputs.
4. Built two evaluators:
   - **Correctness** (LLM-as-judge, pass/fail): is the response a single, open-ended,
     advice-free question?
   - **Warmth** (LLM-as-judge, 1-5, custom/optional): does the response feel human and
     validating, independent of structural correctness?
5. Ran the full evaluation, analyzed results, and wrote `evaluation_summary.md`.
6. Ran an optional A/B cost/performance comparison (`gpt-4o-mini` vs `gpt-4o`) and wrote
   `optimization_summary.md`.

## How to run

Requires a `.env` file (not committed) with:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://eu.api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=coaching-eval-lab
OPENAI_API_KEY=your_openai_api_key
```

```bash
pip install langsmith openai python-dotenv

python setup_check.py              # verify LangSmith + OpenAI connection
python dataset_upload.py           # create dataset + upload the 15 examples (safe to re-run)
python target_function.py          # quick manual test of the coach target function
python evaluator.py                # quick manual test of the correctness evaluator
python warmth_evaluator.py         # quick manual test of the warmth evaluator
python evaluation_run.py           # full evaluation: correctness + warmth vs. all 15 examples
python ab_evaluation_run.py        # optional: gpt-4o-mini vs gpt-4o cost/performance comparison
```

## LangSmith links

- Dataset: `coaching-eval-dataset` — https://eu.smith.langchain.com/datasets
- Main experiment: `coach-gpt4o-mini-with-warmth`
- A/B experiments: `coach-gpt4o-mini-ab`, `coach-gpt4o-ab`

## File map

| File | Purpose |
|---|---|
| `dataset_examples.py` | The 15 hand-built coaching examples (inputs/outputs/metadata) |
| `dataset_upload.py` | Creates the LangSmith dataset and uploads the examples |
| `setup_check.py` | Verifies the LangSmith + OpenAI connection |
| `target_function.py` | Coach target function (`gpt-4o-mini`) — generates responses to evaluate |
| `evaluator.py` | Correctness evaluator (LLM-as-judge, pass/fail) |
| `warmth_evaluator.py` | Custom warmth/empathy evaluator (LLM-as-judge, 1-5) — optional part |
| `evaluation_run.py` | Runs the full evaluation with both evaluators against all 15 examples |
| `target_function_comparaison.py` | Parametrized target function (`gpt-4o-mini` / `gpt-4o`) for the A/B comparison |
| `ab_evaluation_run.py` | Runs the cost/performance A/B comparison — optional part |
| `evaluation_summary.md` | Required deliverable: methodology, results, analysis, recommendation |
| `custom_evaluator_summary.md` | Optional deliverable: warmth evaluator design + correctness-vs-warmth comparison |
| `optimization_summary.md` | Optional deliverable: cost/performance recommendation |

## Key findings

- Baseline correctness (gpt-4o-mini): **80%** (12/15) — all 3 failures occurred on multi-turn
  examples, none on turn-1, suggesting the model drifts toward subtle advice-giving once it has
  more conversational context.
- Warmth is essentially decoupled from correctness (avg 2.07/5, flat across passes and
  failures) — a structurally correct response can still read as clinical. Root cause: the
  system prompt's "single sentence, no preamble" constraint leaves no room for acknowledgment.
- Cost/performance A/B: `gpt-4o-mini` beat `gpt-4o` on every axis (correctness, warmth, latency,
  cost) — see `optimization_summary.md` for detail.
