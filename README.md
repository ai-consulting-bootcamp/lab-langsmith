# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

This repository contains everything you need for this lab.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against
- [`langsmith_custom_dataset_evaluation.ipynb`](./langsmith_custom_dataset_evaluation.ipynb) — setup, FRAMES example extraction, LangSmith dataset creation, and evaluation workflow
- [`lab_proof.md`](./lab_proof.md) — documentation of the selected dataset and lab progress
- [`evaluation_summary.md`](./evaluation_summary.md) — measured evaluation results and limitations
- [`frames_evaluation_scores.csv`](./frames_evaluation_scores.csv) — per-example score, reasoning category, latency, and error status
- [`frames_evaluation_metrics.json`](./frames_evaluation_metrics.json) — aggregate metrics and experiment link

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, using the [Google FRAMES benchmark](https://huggingface.co/datasets/google/frames-benchmark) for the evaluation examples.
3. Run the notebook from top to bottom. It loads the FRAMES `test` split, selects 20 question-answer examples, verifies the LangSmith dataset `FRAMES-Multi-Hop-QA-Evaluation`, runs the evaluator, and writes the result artifacts listed above.
4. Open a **pull request** back into this repository.
5. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
- The recorded experiment evaluates direct, parametric answering without retrieving the Wikipedia pages linked in FRAMES; see the report for the measured results and limitations.
