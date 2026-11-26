# Custom dataset & evaluation with LangSmith — EU AI Act / GDPR Q&A for SMEs

**Domain:** questions a small EU business asks about the AI Act and the GDPR. **Dataset:** `ai-act-gdpr-sme-qa-v1`, 12 examples with reference answers written from the Week 7 course materials, tagged by topic and difficulty.

**Approach:** upload the dataset → traced target function (Gemini, free tier) → LLM-as-judge correctness evaluator (OpenEvals prompt) → `client.evaluate()` → scores by topic and difficulty.

**Status:** dataset and pipeline done; scored experiment pending because the free Gemini quota was exhausted on 26/11/2026. Details in [`lab_proof.md`](./lab_proof.md) (start here).

## File map

| File | What it is |
|---|---|
| `lab_proof.md` | Entry point: code, run, evidence, output, failures |
| `dataset_documentation.md` | Domain, documents, dataset name and description, data structure, the 12 examples |
| `langsmith_evaluation.py` | Dataset creation, target, evaluator, experiment and results export |
| `evaluation_summary.md` | Evaluation summary paragraph (status, method, recommendations) |
| `requirements.txt` | Python dependencies |

## How to run

```bash
pip install -r requirements.txt
# .env (never committed): GEMINI_API_KEY=..., LANGSMITH_API_KEY=lsv2_..., LANGSMITH_TRACING=true
# EU LangSmith accounts only: LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
python langsmith_evaluation.py
```

Optional: `TARGET_MODEL=gemini-2.5-flash-lite` (PowerShell: `$env:TARGET_MODEL="..."`) to start with another model.

## LangSmith links
Project: `ai-act-gdpr-qa-week7`. Dataset: `ai-act-gdpr-sme-qa-v1` (Datasets & Experiments in LangSmith). Experiment `gemini-flash-baseline-*`: pending.
