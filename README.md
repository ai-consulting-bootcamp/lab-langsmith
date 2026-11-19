# CloudDesk support evaluation with LangSmith

**Review entry point: [lab_proof.md](lab_proof.md).**

This project evaluates support answers for a fictional workspace SaaS using 20 source-backed questions across plans, billing, account access, data management, and API/support. A paired comparison changes only the system prompt, with GPT-4o mini as the target and GPT-5.4 mini as the independent correctness and groundedness judge. A deterministic evaluator checks citation coverage. Narrative findings are in [evaluation_summary.md](evaluation_summary.md) and [optimization_summary.md](optimization_summary.md).

## Recorded experiments

- [Dataset: clouddesk-support-v1](https://eu.smith.langchain.com/datasets/cb947ac6-2849-45de-854c-a589623941e0)
- [Baseline experiment](https://eu.smith.langchain.com/datasets/cb947ac6-2849-45de-854c-a589623941e0/compare?selectedSessions=ded79b54-4fb4-4472-b1ce-f6fe6e227850)
- [Policy-aware experiment](https://eu.smith.langchain.com/datasets/cb947ac6-2849-45de-854c-a589623941e0/compare?selectedSessions=5ddbec33-d0ff-4ea4-9966-9067fa05bf6c)
- Tracing project: `lab-clouddesk-support`
- LangSmith endpoint: `https://eu.api.smith.langchain.com`
- Archived suite: `20261119T162817Z`; live links require access to the owning LangSmith workspace. Local exports contain the evidence needed for an offline review.

## Execution

Python 3.14.7 was used for the archived run. Exact direct dependency versions are recorded in `requirements.txt`, with a resolved dependency snapshot in `requirements-lock.txt`.

```bash
python -m venv .venv
```

The environment's Python executable is `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on macOS/Linux. The commands below run with that environment active.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.run_experiments --validate-only
python -m src.analyze_results
```

Offline validation and analysis do not call provider APIs. `clouddesk_support_evaluation.ipynb` is executed and includes tables, figures, calibration evidence and completed analysis. Its default `RUN_LIVE = False` reloads the archived experiment evidence and regenerates analysis without charging for new model calls.

Live execution reads `OPENAI_API_KEY` and `LANGSMITH_API_KEY` from a local `.env` file; `.env.example` documents the names without secrets. The `.env` file is ignored by Git. The live commands create or verify the versioned dataset, create new experiments, and incur OpenAI usage charges:

```bash
python -m src.run_experiments
python -m src.verify_remote
python -m src.analyze_results
```

Each suite writes to a new timestamped folder. `outputs/latest_run.json` selects the run used by analysis. Reports describe the recorded suite above; a new live run creates new evidence and rebuilt tables rather than silently rewriting the narrative findings. Dataset content changes require a new version name. The tested SDK versions remain pinned for reproducibility.

## File map

| Path | Purpose |
|---|---|
| `lab_proof.md` | Reviewer entry point, concrete input/output, evidence and failure |
| `clouddesk_support_evaluation.ipynb` | Executed end-to-end notebook with saved-result and live-run modes |
| `evaluation_summary.md` | One-paragraph evaluation narrative and compact metric table |
| `optimization_summary.md` | One-paragraph cost/performance recommendation |
| `config.json` | Model settings, endpoint, dataset identity and dated prices |
| `data/*.md` | Five synthetic versioned source policies |
| `data/support_examples.json` | Twenty questions, contexts, references and metadata |
| `docs/dataset.md` | Domain, sources, schema, quality and scope |
| `docs/evaluators.md` | Target design, judge criteria, calibration and cost method |
| `docs/langsmith_review.md` | Interface observations, aggregation delay and verification |
| `docs/failure_analysis.md` | Case-level errors, judge mistakes, successful cases and limitations |
| `src/evaluation.py` | Dataset validation/upload, traced targets and evaluators |
| `src/run_experiments.py` | Calibration, smoke tests, LangSmith experiments and exports |
| `src/analyze_results.py` | Offline metrics, paired statistics and figures |
| `src/verify_remote.py` | Remote feedback verification and portable trace exports |
| `tests/test_evaluation.py` | Offline corpus, scoring, cost and error-handling tests |
| `outputs/20261119T162817Z/` | Archived results, manifest, calibration, smoke tests and API usage |
| `outputs/screenshots/` | Completed experiment overview, all dataset examples and S19 trace evidence |
| `outputs/traces/` | Selected target spans with nested OpenAI traces |
| `outputs/*verification.json` | Dataset and experiment read-back receipts |
| `outputs/*.csv` | Aggregates, costs, category/difficulty groups and policy audit |
| `outputs/*.png` | Metric, category and cost/performance figures |
| `outputs/paired_statistics.json` | Paired bootstrap and exact McNemar results |
| `requirements.txt`, `requirements-lock.txt` | Direct dependencies and resolved tested dependency snapshot |
| `.env.example`, `.gitignore` | Environment variable names and local-file exclusions |
| `instructions.md`, `rubric.md` | Original assignment and grading criteria |

## Technical references

[LangSmith evaluation quickstart](https://docs.langchain.com/langsmith/evaluation-quickstart) · [OpenEvals](https://github.com/langchain-ai/openevals) · [GPT-4o mini pricing](https://developers.openai.com/api/docs/models/gpt-4o-mini) · [GPT-5.4 mini pricing](https://developers.openai.com/api/docs/models/gpt-5.4-mini)
