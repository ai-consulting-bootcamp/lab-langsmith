# Micromanage Your Agents — LangSmith Evaluation Lab

This repository contains the Ironhack lab **“LAB | Micromanage your agents.”** It builds a custom LangSmith dataset and evaluates an LLM target with deterministic ground truth.

## Domain

The use case is **SaaS support-ticket priority classification**. The model assigns exactly one label:

- `P1` — active outage, security/privacy incident, data loss, or revenue-critical failure without a practical workaround
- `P2` — major degradation or blocked important feature where the service or a workaround remains available
- `P3` — routine question, enhancement, cosmetic issue, or narrow bug with an easy workaround

This domain is intentionally small: the expected output is objective enough for exact-match scoring, while boundary cases still reveal whether the LLM follows the triage policy.

## Dataset

[`data/support_ticket_priority_examples.json`](data/support_ticket_priority_examples.json) contains 12 hand-written examples: four per class. Every row has an input ticket, reference priority, category, difficulty, and short labeling reason. The file is the version-controlled source of truth uploaded to the LangSmith dataset `ironhack-support-ticket-priority-v1`.

## Approach

[`ticket_priority_eval.py`](ticket_priority_eval.py) validates the local data, creates or reuses the LangSmith dataset, verifies its remote size, and runs the experiment. The LLM target uses the current OpenAI Responses API with `gpt-5.6-luna` by default, wraps the OpenAI client for LangSmith tracing, and is decorated with `@traceable`. The evaluator normalizes the generated label and assigns `priority_accuracy=1` only when it exactly matches the reference.

Tracing is enabled through `LANGSMITH_TRACING=true` and grouped under `LANGSMITH_PROJECT`. Secrets are loaded from `.env`, which is ignored by Git; [`.env.example`](.env.example) contains safe placeholders only.

## Setup and run

Python 3.9 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Add real `LANGSMITH_API_KEY` and `OPENAI_API_KEY` values to `.env`. If the LangSmith key belongs to multiple workspaces, also set `LANGSMITH_WORKSPACE_ID`.

Run all local checks without external credentials:

```bash
python ticket_priority_eval.py validate
pytest -q
```

Create/verify the hosted dataset and run the real experiment:

```bash
python ticket_priority_eval.py evaluate
```

The command is idempotent for an existing dataset with the expected 12 rows. It refuses to run against a same-named dataset with a different size rather than silently duplicating examples.

## LangSmith links and results

- **Dataset:** [`ironhack-support-ticket-priority-v1`](https://smith.langchain.com/o/90426365-e410-4629-9c60-e0e6f05ccf5d/datasets/b8d3b2a8-e09a-430e-8bba-dec2aa346dd9) — 12 verified examples
- **Experiment:** [`ticket-priority-baseline-32443137`](https://smith.langchain.com/o/90426365-e410-4629-9c60-e0e6f05ccf5d/datasets/b8d3b2a8-e09a-430e-8bba-dec2aa346dd9/compare?selectedSessions=96da469f-89b8-4c39-b851-114b11a97813)
- **Result:** 100% exact priority accuracy (12/12), zero run errors
- **Analysis:** [`evaluation_summary.md`](evaluation_summary.md)
- **Evidence record:** [`langsmith_evidence.md`](langsmith_evidence.md)

## File map

- [`README.md`](README.md) — domain, method, setup, run instructions, status, and links
- [`ticket_priority_eval.py`](ticket_priority_eval.py) — dataset upload, traced OpenAI target, evaluator, and experiment runner
- [`data/support_ticket_priority_examples.json`](data/support_ticket_priority_examples.json) — 12 input/reference/metadata examples
- [`tests/test_ticket_priority_eval.py`](tests/test_ticket_priority_eval.py) — dataset and evaluator tests
- [`evaluation_summary.md`](evaluation_summary.md) — required one-paragraph result summary
- [`langsmith_evidence.md`](langsmith_evidence.md) — hosted experiment evidence/status
- [`.env.example`](.env.example) — safe environment-variable template
- [`.gitignore`](.gitignore) — secret and build-artifact exclusions
- [`requirements.txt`](requirements.txt) — Python dependencies
- [`pyproject.toml`](pyproject.toml) — pytest import and test-discovery configuration

## Sources

- [LangSmith evaluation quickstart](https://docs.langchain.com/langsmith/evaluation-quickstart)
- [LangSmith programmatic dataset management](https://docs.langchain.com/langsmith/manage-datasets-programmatically)
- [OpenAI model documentation](https://developers.openai.com/api/docs/models)
