# Micromanage your agents — custom LangSmith evaluation lab

This repository contains a reproducible LangSmith evaluation workflow for a custom **LLM evaluation strategy selection** dataset. The model receives fictional AI-consulting scenarios and must recommend `HUMAN`, `AUTOMATED`, or `HYBRID` evaluation with a concise rationale.

## Dataset and approach

The dataset contains 12 balanced examples with reference answers and metadata. The target function uses the OpenAI Responses API with LangSmith tracing. Evaluation combines deterministic exact-match and format checks with an OpenEvals semantic correctness judge. All examples are fictional and contain no personal or production data.

- **Dataset name:** `llm-evaluation-strategy-selection-v1`
- **Experiment prefix:** `strategy-selection-gpt5-mini`
- **Default target model:** `gpt-5-mini`
- **Default judge model:** `o3-mini`
- **LangSmith dataset link:** generated after the authenticated upload
- **LangSmith experiment link:** saved automatically after the authenticated run

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Add `LANGSMITH_API_KEY` and `OPENAI_API_KEY` to `.env`, then run:

```bash
python src/offline_validate.py
pytest -q
python src/create_dataset.py
python src/run_evaluation.py
python src/analyze_results.py
```

The `.env` file is ignored by Git and must never be committed. For EU-hosted LangSmith, change `LANGSMITH_ENDPOINT` in `.env` to `https://eu.api.smith.langchain.com`.

## Current evidence

The local dataset and scoring path have been validated without credentials. Fixed fixtures produced 75% exact strategy accuracy and 100% format compliance. These fixtures are explicitly labelled as offline test data and are not represented as model or LangSmith results. See `experiment_status.md` for the exact boundary between completed and credential-dependent work.

## File map

| Path | Purpose |
|---|---|
| `dataset_documentation.md` | Domain choice, sources, fields, coverage, and data-quality criteria |
| `evaluator_design.md` | Exact-match, format, and semantic evaluator rationale |
| `evaluation_summary.md` | Required short analysis paragraph and compact metrics |
| `experiment_status.md` | Honest completion/evidence status and pending live-run fields |
| `data/evaluation_examples.json` | Twelve LangSmith-ready inputs, reference outputs, and metadata |
| `data/offline_fixture_outputs.json` | Fixed credential-free outputs used only to test the scoring path |
| `data/offline_validation_results.csv` | Row-level offline validation export |
| `data/offline_validation_metrics.json` | Aggregate offline validation metrics |
| `src/create_dataset.py` | Idempotent LangSmith dataset creation and upload |
| `src/run_evaluation.py` | Traced target, evaluators, experiment execution, and result export |
| `src/offline_validate.py` | Credential-free dataset and scoring validation |
| `src/analyze_results.py` | Compact analysis of offline or live result exports |
| `tests/test_dataset.py` | Dataset integrity and coverage tests |
| `docs/live_run_checklist.md` | Exact authenticated run and UI-review steps |
| `.env.example` | Safe environment-variable template with no secrets |
| `requirements.txt` | Python dependencies |

## References

- [LangSmith evaluation quickstart](https://docs.langchain.com/langsmith/evaluation-quickstart)
- [LangSmith OpenAI tracing](https://docs.langchain.com/langsmith/trace-openai)
- [OpenAI API quickstart](https://developers.openai.com/api/docs/quickstart)

