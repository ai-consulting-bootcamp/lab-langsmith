# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

This repository contains the completed LangSmith evaluation lab for a fictional Northstar Outfitters customer-support policy.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against
- [`policy.md`](./policy.md) — the versioned source document used to create the dataset
- [`lab_langsmith.ipynb`](./lab_langsmith.ipynb) — completed setup, dataset, target, evaluators, experiments, analysis, and optional A/B comparison
- [`lab_proof.md`](./lab_proof.md) — run evidence, links, outputs, and limitations
- [`evaluation_summary.md`](./evaluation_summary.md) — compact findings report
- [`optimization_summary.md`](./optimization_summary.md) — optional cost/performance comparison
- [`outputs/`](./outputs/) — CSV results and generated charts

## How to complete this lab

1. Put valid `OPENAI_API_KEY` and `LANGSMITH_API_KEY` values in a local `.env` file.
2. Open `lab_langsmith.ipynb` and run cells top to bottom. The dataset cell is rerun-safe and skips an existing version.
3. Review the generated CSVs/charts in `outputs/` and the LangSmith experiment links printed by the experiment cells.

The lab uses the EU LangSmith endpoint, `gpt-4o-mini` as the target, and `gpt-5.4-mini` as the stronger judge. The dataset is intentionally small and fictional; its purpose is to demonstrate the evaluation workflow rather than establish a production quality claim.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
