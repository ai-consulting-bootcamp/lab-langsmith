# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

This repository contains the completed LangSmith custom dataset & evaluation lab.

## Project: Blog Title Generation Evaluation

### Domain & Dataset

**Domain:** Content Creation — blog title generation. Given a real Medium article excerpt,
generate an engaging, accurate title.

**Dataset:** 18 examples extracted from [`fabiochiu/medium-articles`](https://huggingface.co/datasets/fabiochiu/medium-articles)
on Hugging Face, spanning 14 distinct topics (writing, marketing, productivity, health,
personal essays, etc.). Each example pairs a ~400-word article excerpt (input) with the
article's actual, published title (ground truth output) — real human-authored titles rather
than synthetic labels. See [`domain_and_dataset.md`](domain_and_dataset.md) for the full
rationale.

**LangSmith dataset:** `blog-title-generation-medium-articles`
(`https://eu.smith.langchain.com/datasets/c55c213c-5c11-48e2-9bbd-04c91b31ba7d`)

### Approach Overview

1. Extracted and quality-filtered 18 examples from the source dataset — including a
   title-leakage guard, since ~40% of raw excerpts otherwise repeated the headline verbatim
   as the first line of the body (see "Data Structure" below).
2. Uploaded the examples to a LangSmith dataset.
3. Built a `@traceable` target function (`gpt-4o-mini`) that generates a title from an
   article excerpt.
4. Built a custom correctness evaluator (LLM-as-judge, `gpt-4o-mini`) scoring topical/factual
   alignment with the reference title — explicitly designed to ignore stylistic wording
   differences, since there's rarely one single "correct" title.
5. Ran the evaluation experiment, reviewed results in the LangSmith UI, then did a deeper
   quantitative + qualitative analysis (categorical breakdown, error analysis).
6. **(Optional)** Built a second, independent custom evaluator for *editorial style fit*
   (does the title read like something a human editor would actually publish, vs. an
   SEO-style meta-description) and ran both evaluators together for comparison.
7. **(Optional)** Ran an A/B cost-performance comparison between `gpt-4o-mini` and `gpt-4o`
   on the same task, dataset, and evaluator, pulling real cost/token/latency data from
   LangSmith to determine which model is actually worth its price for this task.

### Data Structure (Step 3)

`data/blog_title_examples.json` contains 18 examples, each a JSON object with three
top-level fields matching the shape LangSmith expects for
`client.create_examples(inputs=..., outputs=..., metadata=...)`:

```json
{
  "inputs": {
    "article_text": "<~400-word excerpt of the article body>"
  },
  "outputs": {
    "title": "<the article's real, published title>"
  },
  "metadata": {
    "tags": ["<all of the article's original tags>"],
    "primary_tag": "<tags[0], used for categorical analysis in Step 9>",
    "url": "<source Medium URL>",
    "full_text_word_count": 862,
    "excerpt_word_count": 400
  }
}
```

- **`inputs.article_text`** — sent to the target function (Step 5) along with an
  instruction to write a title.
- **`outputs.title`** — the ground truth for the correctness evaluator (Step 6).
- **`metadata`** — not sent to the model; used for categorical/error analysis (Step 9).

**Data quality steps taken** (see [`scripts/extract_examples.py`](scripts/extract_examples.py)):

- **Deduplication** by title.
- **Length filtering** — articles under 250 words (before excerpting) dropped.
- **Title leakage guard** — Medium's scraped `text` field frequently repeats the headline
  as the first line of the body. Left unhandled, ~40% of excerpts started with the title
  itself, letting the model "cheat" by copying it instead of generating one. The script
  detects and strips this before building the excerpt.
- **Malformed-title filtering** — titles that are empty, too short/long (outside 15–100
  characters), contain a raw URL, or are literally "Untitled" are excluded.
- **Diversity cap** — max 2 examples per `primary_tag` (14 distinct tags across 18
  examples), since the raw dataset skewed heavily toward mental-health/neuroscience content.

Regenerate with `python3 scripts/extract_examples.py` (streams directly from Hugging Face,
no local download needed, overwrites `data/blog_title_examples.json`).

### Key Findings

- **Correctness:** mean 0.878 (18 examples, 0 errors) — the model reliably identifies the
  correct topic of an article from its excerpt.
- **Real failure mode:** not style, but an *excerpt-scope mismatch* — when a human title
  encodes the author's stance/rhetorical framing rather than just the topic, that framing
  often isn't established in the first 400 words, so the model titles the visible setup
  instead. See `data/step9_analysis.md`.
- **Custom evaluator finding:** correctness (mean 0.87) and editorial style fit (mean 0.33)
  are essentially uncorrelated (r = 0.025) — the model is topically accurate on nearly every
  example while almost never producing a title that would pass an editor's bar for
  conciseness. See `data/custom_evaluator_summary.md`.
- **Cost/performance finding:** `gpt-4o` scored slightly *lower* than `gpt-4o-mini` (0.892
  vs. 0.906) while costing **16.5x more per example** ($0.0016 vs. $0.0001) — no measurable
  quality benefit justifies the extra cost on this task. See `optimization_summary.md`.

Full narrative: [`evaluation_summary.md`](evaluation_summary.md) and [`optimization_summary.md`](optimization_summary.md).

### How to Run

```bash
pip install langsmith openai openevals datasets python-dotenv

cp .env.example .env   # fill in OPENAI_API_KEY and LANGSMITH_API_KEY

python3 scripts/extract_examples.py            # Step 3: build data/blog_title_examples.json
python3 scripts/create_dataset.py              # Step 4: upload to LangSmith
python3 scripts/target_function.py             # Step 5: smoke-test the target function
python3 scripts/evaluator.py                   # Step 6: smoke-test the correctness evaluator
python3 scripts/run_evaluation.py              # Step 7: run the full evaluation
python3 scripts/analyze_results.py             # Step 9: aggregate/categorical analysis

# Optional: custom evaluator (Steps 11-13)
python3 scripts/custom_evaluator.py            # smoke-test the style-fit evaluator
python3 scripts/run_evaluation_with_custom.py  # run both evaluators together

# Optional: cost/performance A/B comparison (Steps 14-15)
python3 scripts/run_ab_comparison.py           # run gpt-4o-mini vs gpt-4o
python3 scripts/analyze_cost_performance.py    # compare cost, score, latency
```

All scripts read credentials from `.env` (see `.env.example` for the required variables,
including the LangSmith EU endpoint).

### File Map

| File | Purpose |
|---|---|
| `instructions.md` | The lab instructions |
| `rubric.md` | How this submission is graded — what the AI reviewer checks the PR against |
| `domain_and_dataset.md` | Step 1 deliverable: domain choice, data source, example structure |
| `02_langsmith.ipynb` | Reference lesson notebook, adapted to this project's actual dataset/pipeline |
| `.env.example` | Required environment variables (no real secrets) |
| `data/blog_title_examples.json` | The 18 structured examples (Step 3) — see "Data Structure" above |
| `data/step8_ui_review_notes.md` | LangSmith UI review notes (Step 8) |
| `data/step9_analysis.md` | Full quantitative + categorical + error analysis (Step 9) |
| `data/eval_results_gpt-4o-mini.json` | Per-example correctness results (Step 7) |
| `data/eval_results_multi_evaluator.json` | Per-example correctness + style-fit results (Step 12) |
| `data/custom_evaluator_summary.md` | Custom evaluator design + results (Steps 11-13) |
| `scripts/extract_examples.py` | Builds the dataset from `fabiochiu/medium-articles` (Step 3) |
| `scripts/create_dataset.py` | Uploads examples to LangSmith (Step 4) |
| `scripts/target_function.py` | The `@traceable` title-generation target function (Step 5) |
| `scripts/evaluator.py` | Correctness evaluator (Step 6) |
| `scripts/run_evaluation.py` | Runs the evaluation experiment (Step 7) |
| `scripts/analyze_results.py` | Aggregate/categorical analysis script (Step 9) |
| `scripts/custom_evaluator.py` | Custom style-fit evaluator (Step 11) |
| `scripts/run_evaluation_with_custom.py` | Runs both evaluators together (Step 12) |
| `scripts/run_ab_comparison.py` | Runs gpt-4o-mini vs. gpt-4o with cost/token/latency tracking (Step 14) |
| `scripts/analyze_cost_performance.py` | Cost-performance comparison + recommendation (Step 15) |
| `data/ab_comparison_results.json` | Per-example results for both models (Step 14) |
| `evaluation_summary.md` | Required top-level evaluation report (Step 10) |
| `optimization_summary.md` | Cost-performance recommendation (Step 16) |
| `lab_proof.md` | Screenshot evidence write-up — see "Screenshots" below |
| `screenshots/` | Screenshot image files |

### Screenshots

Full write-up with captions in [`lab_proof.md`](lab_proof.md). Direct index for evaluation:

| Screenshot | Step | Shows |
|---|---|---|
| [`screenshots/dataset_examples.png`](screenshots/dataset_examples.png) | Step 4 | LangSmith dataset "Examples" tab — all 18 examples with inputs/reference outputs/metadata correctly attached |
| [`screenshots/experiments_comparison.png`](screenshots/experiments_comparison.png) | Step 7 / 12 | LangSmith "Experiments" tab — correctness-only vs. correctness+style-fit runs side by side, with feedback/latency/cost charts |
| [`screenshots/target_function_smoke_test.png`](screenshots/target_function_smoke_test.png) | Step 5 | Terminal output of `scripts/target_function.py` — reference vs. generated titles |
| [`screenshots/analysis_output.png`](screenshots/analysis_output.png) | Step 9 | Terminal output of `scripts/analyze_results.py` — aggregate metrics, categorical breakdown, length-gap check |

### LangSmith Links

- Dataset: `https://eu.smith.langchain.com/datasets/c55c213c-5c11-48e2-9bbd-04c91b31ba7d`
- Correctness-only experiment (current, matches `data/eval_results_gpt-4o-mini.json`):
  `gpt-4o-mini-blog-title-55fcee73`
- Correctness + style-fit experiment: `gpt-4o-mini-blog-title-multi-eval-993d4c7e`
- A/B comparison experiments: `ab-gpt-4o-mini-92d3085a` and `ab-gpt-4o-fce27e55`

`scripts/run_evaluation.py` was run more than once while testing the pipeline
(`temperature=0.3` means each rerun regenerates slightly different titles/scores); all
narrative docs and metrics in this repo reflect the experiment listed above as current.

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
