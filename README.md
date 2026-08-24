# Simple LangSmith Lab — OpenEvals Documentation Q&A

Author: Parisa Dehghani

This repository completes the mandatory parts of the LangSmith custom-dataset lab using a 10-example OpenEvals repository/documentation Q&A dataset. Optional custom-evaluator and cost/performance extensions are not included.

## What the project does

`run_lab.py` performs the complete required workflow:

1. Checks the LangSmith EU configuration and verifies a real connection.
2. Creates or verifies the `openevals-repo-qa-v2` LangSmith dataset.
3. Confirms that all 10 examples are present and match `examples.json`.
4. Tests the real LLM-backed target function on 3 examples.
5. Runs the full evaluation in LangSmith.
6. Uses OpenEvals `CORRECTNESS_PROMPT` as an LLM-as-judge evaluator.
7. Saves the experiment results to `results.csv`.
8. Creates `analysis.md` with metrics, topic analysis, and failure observations.
9. Rewrites `evaluation_summary.md` with the real results.
10. Saves the LangSmith dataset and experiment URLs in `langsmith_links.md`.

## Dataset

Domain: OpenEvals repository/documentation Q&A.

Source:
- https://github.com/langchain-ai/openevals/blob/main/README.md

Each example contains:
- a question;
- supporting documentation context;
- a reference answer;
- source, topic, and difficulty metadata.

The dataset intentionally focuses on OpenEvals itself rather than meta-questions about the lab.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to a new file named `.env`, then add your real keys:

```text
LANGSMITH_API_KEY=...
OPENAI_API_KEY=...
```

Do not commit `.env`.

## Run

Run the complete lab with one command:

```bash
python run_lab.py
```

A successful run prints:
- `LangSmith connection: OK`
- project name
- EU endpoint
- tracing state
- verified dataset count
- experiment name
- experiment URL
- dataset URL

## After the run

The script creates or updates:

- `results.csv` — per-example LangSmith evaluation results
- `analysis.md` — mean, median, pass rate, topic metrics, failures, and recommendation
- `evaluation_summary.md` — required short report with real metrics and links
- `langsmith_links.md` — dataset and experiment URLs

Also add one screenshot from the LangSmith experiment UI to the `screenshots/` folder before submission.

## File map

| File | Purpose |
|---|---|
| `README.md` | Setup, run instructions, and file map |
| `run_lab.py` | Complete dataset + target + evaluator + LangSmith experiment workflow |
| `examples.json` | 10 OpenEvals documentation Q&A examples |
| `part1_domain_writeup.md` | Domain, source, example selection, and data structure |
| `langsmith_setup.md` | EU endpoint, project, tracing, and connection verification |
| `.env.example` | Safe environment-variable template |
| `.gitignore` | Prevents secrets and local environment files from being committed |
| `requirements.txt` | Python packages |
| `evaluation_summary.md` | Required short report; automatically replaced after the live run |
| `results.csv` | Generated real experiment results |
| `analysis.md` | Generated result analysis |
| `langsmith_links.md` | Generated dataset and experiment URLs |
| `screenshots/` | LangSmith UI evidence |

## Submission check

Before committing, confirm that:
- the terminal showed `LangSmith connection: OK`;
- the dataset has 10 examples in LangSmith;
- the LangSmith experiment completed;
- `results.csv`, `analysis.md`, and `langsmith_links.md` exist;
- `evaluation_summary.md` contains real metrics instead of the starter text;
- one LangSmith UI screenshot is in `screenshots/`;
- `.env` is not committed.
