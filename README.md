# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

This repository contains everything for this lab: a custom LangSmith dataset, evaluation
pipeline, custom evaluator, and cost-performance analysis for a news content classification
task.

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking
   feedback and push updates to the same PR.

## Domain & Dataset

**Domain:** Content Creation → News Content Classification. Rather than an open-ended
rewriting task (where "correct" is subjective), this lab classifies news articles into one
of four objective categories (`World`, `Sports`, `Business`, `Sci/Tech`), giving every
prediction an unambiguous, verifiable ground truth to score against.

**Dataset:** 16 examples curated from the [AG News dataset](https://huggingface.co/datasets/fancyzhx/ag_news)
(Hugging Face), spanning all 4 categories with `easy`/`medium`/`hard` difficulty tags based
on how much category-boundary ambiguity each article contains.

- **LangSmith dataset name:** `ag-news-content-classification`
- **Local source file:** [`data/content_creation_dataset.json`](data/content_creation_dataset.json)

See [`lab_walkthrough.md`](lab_walkthrough.md) for the full step-by-step documentation (domain selection, environment setup, dataset structuring, target function, evaluator design, and results analysis for every step of the lab).

## Approach (brief)

1. `create_dataset.py` — pulls curated AG News rows into a local JSON with reference
   labels, categories, and difficulty metadata.
2. `create_langsmith_dataset.py` — uploads the local JSON to LangSmith as a dataset.
3. `target_functions.py` — a `@traceable` `gpt-4o-mini` classifier (temperature 0.0)
   that predicts one of the 4 categories per article.
4. `evaluators.py` — `exact_match_evaluator`, a deterministic evaluator comparing the
   predicted category to the dataset's reference label.
5. `custom_evaluator.py` — `plausibility_evaluator`, an LLM-as-judge evaluator scoring
   (1-5) whether the predicted category is a *defensible* read of the article, independent
   of the reference label — this distinguishes genuine model errors from disagreements with
   an ambiguous ground truth.
6. `run_evaluation.py` — runs the full evaluation (`exact_match` + `plausibility`) via
   `client.evaluate()`.
7. `ab_comparison.py` — reruns the same dataset/prompt/evaluators against `gpt-4o` for a
   cost-performance comparison against the `gpt-4o-mini` baseline.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in your own LANGSMITH_API_KEY and OPENAI_API_KEY in .env

python src/create_dataset.py              # 1. build the local dataset JSON
python src/create_langsmith_dataset.py    # 2. upload it to LangSmith
python src/target_functions.py            # 3. smoke-test the target function
python src/custom_evaluator.py            # 4. smoke-test the custom evaluator
python src/run_evaluation.py              # 5. run the full evaluation
python src/ab_comparison.py               # 6. (optional) gpt-4o-mini vs gpt-4o comparison
```

## LangSmith Links

- **Dataset:** `ag-news-content-classification` — [view in LangSmith](https://eu.smith.langchain.com/o/16ee67e0-4be5-476b-ba9a-ddd0185bc293/datasets/72be7b1c-c88b-48f0-8a5e-42362ba4f1c9)
- **Baseline experiment** (exact_match only): [gpt-4o-mini-20260823-141007](https://eu.smith.langchain.com/o/16ee67e0-4be5-476b-ba9a-ddd0185bc293/datasets/72be7b1c-c88b-48f0-8a5e-42362ba4f1c9/compare?selectedSessions=b93db39c-384f-4f2b-8eb6-7e6e676f47c1)
- **With custom evaluator** (exact_match + plausibility): [gpt-4o-mini-20260823-180009](https://eu.smith.langchain.com/o/16ee67e0-4be5-476b-ba9a-ddd0185bc293/datasets/72be7b1c-c88b-48f0-8a5e-42362ba4f1c9/compare?selectedSessions=ce90eaee-7c9d-413c-9c89-656b99a0d041)
- **A/B comparison — gpt-4o-mini:** [ab-gpt-4o-mini](https://eu.smith.langchain.com/o/16ee67e0-4be5-476b-ba9a-ddd0185bc293/datasets/72be7b1c-c88b-48f0-8a5e-42362ba4f1c9/compare?selectedSessions=623f42db-1df0-4648-99b0-59c6fe610801)
- **A/B comparison — gpt-4o:** [ab-gpt-4o](https://eu.smith.langchain.com/o/16ee67e0-4be5-476b-ba9a-ddd0185bc293/datasets/72be7b1c-c88b-48f0-8a5e-42362ba4f1c9/compare?selectedSessions=35056420-49c8-4d12-ad96-4aae456b0fc8)

## File Map

| File / Folder | Purpose |
|---|---|
| `instructions.md` | The lab instructions (provided scaffold) |
| `rubric.md` | Grading rubric the AI reviewer checks this PR against (provided scaffold) |
| `lab_walkthrough.md` | Full step-by-step documentation for every step (1-16) of the lab |
| `evaluation_summary.md` | Required one-paragraph evaluation summary (Step 10) |
| `optimization_summary.md` | Optional one-paragraph cost/performance summary (Step 16) |
| `custom_evaluator_summary.md` | Optional custom evaluator design, results, and reflection (Steps 11-13) |
| `data/content_creation_dataset.json` | The 16 curated source examples before upload to LangSmith |
| `src/create_dataset.py` | Builds the local dataset JSON from AG News |
| `src/create_langsmith_dataset.py` | Uploads the local JSON to LangSmith as a dataset |
| `src/target_functions.py` | Traced `gpt-4o-mini` classification target function |
| `src/evaluators.py` | `exact_match_evaluator` — deterministic correctness scoring |
| `src/custom_evaluator.py` | `plausibility_evaluator` — LLM-as-judge, reference-free scoring |
| `src/run_evaluation.py` | Runs the full evaluation with both evaluators |
| `src/ab_comparison.py` | Cost-performance A/B comparison across models |
| `src/setup_env.py` | LangSmith/OpenAI client connection verification |
| `results/` | Raw CSV exports of evaluation runs from LangSmith |
| `screenshots/` | LangSmith UI screenshots documenting each step |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for required environment variables (no real secrets) |

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing (`.env` is git-ignored; verify it never appears in `git status` before pushing).
