# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

## Domain and dataset

B2B SaaS marketing operations, lead qualification and conversion prediction. Given a lead's 30-day engagement snapshot (firmographics, lead source/channel, touch and session activity, estimated deal value), the task is to predict whether the lead converts to a paying customer within 90 days.

Dataset: [LeadForge Lead Scoring: Intro (v1)](https://www.kaggle.com/datasets/derelictpanda/leadforge-lead-scoring-intro-v1) on Kaggle, 18 examples sampled and stratified across lead source and outcome. Full description in [`dataset_documentation.md`](./dataset_documentation.md).

## Approach

1. Set up a LangSmith client with EU tracing, wrapped OpenAI client for automatic call logging.
2. Sampled 18 leads from the source CSV, stratified across `lead_source` and `converted_within_90_days`, uploaded as a LangSmith dataset.
3. Built a target function (`predict_conversion`) that asks gpt-4o-mini to predict conversion from a lead's snapshot, `@traceable` for tracing.
4. Built a correctness evaluator with `create_llm_as_judge`, starting with openevals' generic prompt then tightening it to a binary-match rubric after the generic one appeared to under-score correct answers.
5. Ran the evaluation, reviewed results in the LangSmith UI, and analyzed aggregate and per-category metrics.
6. Ran an optional A/B comparison against gpt-4o on the same dataset and evaluator.

## How to run

1. Create a `.env` file with `OPENAI_API_KEY` and `LANGSMITH_API_KEY`.
2. Open `lead_scoring_evaluation.ipynb` and run cells top to bottom.
3. Running the evaluation cells calls the OpenAI API and will incur cost.

## LangSmith links

- Dataset: `ironhack-lab-micromanage-your-agents-lead-scoring` (see notebook Step 4 for creation code)
- gpt-4o-mini experiment (corrected evaluator): [`gpt-4o-mini-lead-scoring-d70eabbf`](https://eu.smith.langchain.com/o/30e98d46-c47a-47c0-ad74-25a7832452c5/datasets/b294578b-5f9a-427c-83b9-542b448a3780/compare?selectedSessions=9c9defca-c69a-41b1-89ff-3fc2f620f30b)
- gpt-4o A/B experiment: [`gpt-4o-lead-scoring-62598ef8`](https://eu.smith.langchain.com/o/30e98d46-c47a-47c0-ad74-25a7832452c5/datasets/b294578b-5f9a-427c-83b9-542b448a3780/compare?selectedSessions=e7c533b2-ceb5-47d1-9860-c86574d142e2)

## File map

| File | Purpose |
|---|---|
| `lead_scoring_evaluation.ipynb` | All implementation code: setup, dataset creation, target function, evaluators, evaluation runs, A/B comparison |
| `dataset_documentation.md` | Step 1 deliverable: domain, source, data structure |
| `evaluation_results.md` | Steps 7-9, 11-15 deliverables: experiment links, UI review notes, analysis, A/B results, custom evaluator (not attempted) |
| `evaluation_summary.md` | Step 10 deliverable: one-paragraph evaluation summary (required) |
| `optimization_summary.md` | Step 16 deliverable: one-paragraph cost/performance recommendation (optional) |
| `Data/lead_scoring.csv` | Source data: 5,000-row LeadForge dataset, used to build the 18-example sample |
| `Outputs/` | Raw CSV exports of each LangSmith experiment run |
| `instructions.md` | Lab instructions (provided) |
| `rubric.md` | Grading rubric (provided) |

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
