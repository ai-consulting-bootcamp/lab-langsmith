# OWASP GenAI LLM Top 10 (2026) – LangSmith Evaluation

## Project Overview

This project was developed for the Ironhack **Micromanage Your Agents** LAB.

The goal is to evaluate how accurately an LLM answers security-related questions based on the OWASP GenAI LLM Top 10 (2026).

## Dataset

- **Dataset:** `owasp-llm-top10-2026-v1`
- **Size:** 20 question-answer pairs
- **Coverage:** All 10 OWASP GenAI LLM risk categories
- **Metadata:** Question category, difficulty, and source document
- **Source material:** Official OWASP GenAI LLM Top 10 (2026) documentation

The dataset includes definitions, risk factors, technical explanations, and scenario-based questions.

## Evaluation Approach

**Target model:** `gpt-4o-mini`

**Evaluators:**
1. LLM-as-a-Judge correctness evaluation using `gpt-5-mini`.
2. Rule-based keyword overlap using a 25% threshold.

LangSmith is used for experiment execution, tracing, and feedback collection.

## Results

| Metric | Result |
|---|---|
| Evaluated examples | 20 |
| LLM Judge correctness | 55% (11/20) |
| Keyword overlap | 95% (19/20) |
| Factual errors | 6 |
| Incomplete answers | 2 |
| Hallucinations | 1 |

The main failure pattern involves incorrect OWASP terminology, security classifications, and missing technical details.

See [evaluation_summary.md](evaluation_summary.md) for the full analysis.

## How to Run

1. Install the required Python packages: `langsmith`, `openai`, `openevals`, `python-dotenv`, `pandas`, and `matplotlib`.
2. Create a local `.env` file with `OPENAI_API_KEY` and `LANGSMITH_API_KEY`.
3. Ensure that your API project has access to the target and judge models.
4. Open the evaluation notebook in Jupyter or VS Code.
5. Execute the required LAB sections in order, from setup through reporting.

The notebook connects to the EU LangSmith endpoint. Evaluation runs generate API costs.

## Project Files

- `lab_langsmith.ipynb` – Evaluation implementation and analysis
- `data/owasp_sources/` – OWASP source documents
- `outputs/results_main.csv` – Evaluation results
- `outputs/pass_rate_by_category.png` – Category performance visualization
- `evaluation_summary.md` – Evaluation findings
- `lab_proof.md` – Execution evidence and limitations

## LangSmith Experiment

[View evaluation experiment](https://eu.smith.langchain.com/o/30676eb8-0d5d-42d8-aa84-ca8c16dce2c5/datasets/f36ce8bb-1f79-441f-9c59-b78ca1a6929d/compare?selectedSessions=68548a5f-d128-4510-859b-3b6574eca64c)

## Limitations

The dataset contains only 20 examples. The results represent an initial evaluation baseline rather than a statistically robust assessment.

LLM-as-a-Judge ratings may contain errors, and keyword overlap does not reliably measure factual correctness.