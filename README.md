# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

This repository contains everything you need for this lab.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against
- [`langsmith_custom_dataset_evaluation.ipynb`](./langsmith_custom_dataset_evaluation.ipynb) — setup, HLE example extraction, LangSmith dataset creation, and evaluation workflow
- [`lab_proof.md`](./lab_proof.md) — documentation of the selected dataset and lab progress

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, using the text-only, multiple-choice subset of the gated [HLE dataset](https://huggingface.co/datasets/cais/hle) for the evaluation examples.
3. Before running the notebook's HLE cells, request/accept access to the dataset on Hugging Face and add a read token as `HF_TOKEN` in the local, git-ignored `.env` file. Never commit or share the token.
4. Run the notebook from top to bottom. It loads 20 HLE examples, creates the LangSmith dataset `HLE-Multiple-Choice-Evaluation`, and checks the uploaded examples.
5. Open a **pull request** back into this repository.
6. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
