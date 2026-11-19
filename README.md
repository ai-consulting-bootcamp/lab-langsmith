# LAB | Micromanage your agents: EU AI Act risk classifier evaluation with LangSmith

Ayhan Demir · Ironhack AI Consulting & Integration Bootcamp

## Domain and dataset
EU AI Act risk classification: given an AI use case and the legal passages a search step would return, the model names the risk class (prohibited, high-risk, limited, minimal or needs-more-info), the deciding provision and a short reason. The LangSmith dataset `ai-act-risk-classifier-v1` holds 24 hand-written cases from 23 sectors (5 prohibited, 6 high-risk, 5 limited, 5 minimal, 3 needs-more-info), 7 of them hard trap cases. Source: Regulation (EU) 2024/1689, consolidated version 27.07.2026 ([EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng/pdf)).

## Approach
- **Target:** gpt-4o-mini, temperature 0, JSON mode; input = case + 2 legal passages (deciding provision + near-miss); traced with `@traceable` and `wrap_openai`.
- **Evaluators:** OpenEvals correctness judge (gpt-5.4-mini, True/False), exact match on the class, and the same judge prompt on a 1 to 10 scale.
- **Experiment:** one LangSmith experiment (`gpt-4o-mini-ctx-v1`), then analysis in pandas: pass rates, mean / median / distribution, results by class and difficulty, confusion table, hand-labelled failures.
- **Results:** see [`evaluation_summary.md`](evaluation_summary.md).


## How to Run

### Prerequisites

- Python 3.12 and Jupyter (JupyterLab, Notebook, or VS Code notebooks)
- An OpenAI API key and a LangSmith API key with access to the LangSmith workspace

Create a `.env` file in the repository root with:

```dotenv
OPENAI_API_KEY=your-openai-api-key
LANGSMITH_API_KEY=your-langsmith-api-key
```

The file is ignored by Git. The notebooks install their Python packages in the first code cell using `%pip install`.

Both notebook files are present in this working tree, but `.gitignore` currently excludes `*.ipynb`. A fresh Git checkout will not contain the notebooks unless they are included separately.

### Main evaluation

1. Open `langsmith_eval_ai_act_risk_classifier.ipynb` and run its cells from top to bottom.
2. The notebook loads `data/ai_act_cases_v1.json`, creates the LangSmith dataset `ai-act-risk-classifier-v1` if it does not already exist, runs the evaluation, and writes result exports and charts under `outputs/`.
3. The notebook is configured for the US LangSmith endpoint. If your workspace is in the EU, switch to the EU endpoint in the setup cell before running.

Each run creates a new LangSmith experiment. Existing datasets are reused.

### Optional evaluator and model comparison

After the main notebook has created the LangSmith dataset, open `langsmith_eval_ai_act_custom_evaluator_ab_test.ipynb` and run its cells from top to bottom. It runs the groundedness evaluator and the three-configuration model/prompt comparison, then saves their exports and charts under `outputs/`. It uses the same API keys and endpoint setting as the main notebook.

The notebooks make API calls and create LangSmith experiments, which may incur usage charges.

## Repository map

### Root files

| Path | Purpose |
|---|---|
| `.gitignore` | Excludes local secrets, macOS metadata, notebook checkpoints, and Jupyter notebooks from Git. |
| `README.md` | Repository overview and lab submission information. |
| `README2.md` | Run instructions and this file/folder map. |
| `instructions.md` | Assignment brief and required deliverables. |
| `rubric.md` | Evaluation rubric for the lab. |
| `langsmith_eval_ai_act_risk_classifier.ipynb` | Main workflow: setup, dataset, target, evaluators, experiment, analysis, and exports. |
| `langsmith_eval_ai_act_custom_evaluator_ab_test.ipynb` | Optional workflow: groundedness evaluator and model/prompt cost-performance comparison. |
| `evaluation_summary.md` | Evaluation narrative and key evaluation metrics. |
| `optimization_summary.md` | Optimization narrative and configuration comparison. |

### Folders

| Path | Contents |
|---|---|
| `data/` | Source evaluation cases. |
| `outputs/` | CSV exports and charts produced by the notebooks. |
| `outputs/screenshots/` | LangSmith dataset, experiment, and trace screenshots. |

### Data and output files

| Path | Purpose |
|---|---|
| `data/ai_act_cases_v1.json` | The 24 evaluation cases, including inputs, expected outputs, and metadata. |
| `outputs/results_main.csv` | Main experiment results, one row per case. |
| `outputs/metrics_summary.csv` | Aggregate metrics for the main evaluators. |
| `outputs/failures.csv` | Cases that failed evaluation, with failure labels. |
| `outputs/quality_score_distribution.png` | Distribution of main-run quality scores. |
| `outputs/pass_rate_by_category.png` | Main-run pass rate by expected risk category. |
| `outputs/custom_eval_results.csv` | Per-case correctness and groundedness results. |
| `outputs/groundedness_vs_correctness.png` | Groundedness scores grouped by correctness. |
| `outputs/ab_comparison.csv` | Comparison metrics for the three model/prompt configurations. |
| `outputs/cost_vs_performance.png` | Cost and class-match comparison chart. |
| `outputs/screenshots/01_dataset.png` | Screenshot of the LangSmith dataset. |
| `outputs/screenshots/02_experiment.png` | Screenshot of a LangSmith experiment. |
| `outputs/screenshots/03_trace.png` | Screenshot of an individual trace. |

The evaluation and optimization narratives are in [`evaluation_summary.md`](evaluation_summary.md) and [`optimization_summary.md`](optimization_summary.md), respectively.
