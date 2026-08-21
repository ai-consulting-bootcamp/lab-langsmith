# LAB | Micromanage your agents

Week 7 of the Ironhack AI Consulting Bootcamp — building a custom LangSmith
dataset, running evaluation experiments, and designing evaluators that measure
what correctness cannot.
**Author:** Nnanyelugo Ahukannah

Fork of [`ai-consulting-bootcamp/lab-langsmith`](https://github.com/ai-consulting-bootcamp/lab-langsmith).
`instructions.md` and `rubric.md` are unchanged; the original lab README is
preserved in full below this section.

## Start here

- **[`evaluation_summary.md`](evaluation_summary.md)** — the evaluation write-up (Step 10)
- **[`optimization_summary.md`](optimization_summary.md)** — the cost/performance write-up (Step 16)
- **[`lab_langsmith_ugo_ahukannah/`](lab_langsmith_ugo_ahukannah/)** — dataset, code, results, figures, screenshots

## Domain and dataset

**Consumer-credit compliance question answering** for Cardinal Trust Bank, a
fictional US regional lender. A three-document corpus of 27 numbered clauses
(Regulation B adverse-action duties, FCRA §615 disclosures, and the bank's own
notice policy); 22 questions a compliance officer would actually ask, each with a
reference answer and the clause IDs it rests on.

The ground truth is the **corpus**, not the law: the documents were authored for
this exercise, so the evaluation measures faithfulness to a supplied source rather
than real-world legal correctness. A model can give a real-world-plausible answer
that contradicts the document it was handed, and in a grounded-QA system that is
still a failure.

LangSmith dataset **`cardinal-trust-adverse-action-qa`**
(`9f32b481-0b9d-4199-8cc9-25a4bb7a35c0`), EU region, project
`cardinal-trust-compliance-qa` — 22 examples, 6 experiments.

## Approach

Three configurations over one dataset, each isolating a single variable:

| target | model | prompt | isolates |
|---|---|---|---|
| `mini` | gpt-4o-mini | full grounded | baseline |
| `gpt4o` | gpt-4o | full grounded | the **model** |
| `terse` | gpt-4o-mini | stripped | the **prompt** |

Five evaluators: openevals' stock correctness judge, a custom `groundedness`
judge, and three deterministic citation checks that use no model at all.

## Headline result

**Correctness was blind to the biggest failure in the run.** Stripping the
grounding discipline out of the prompt — same model — *raised* correctness
0.818 → 0.909 while collapsing citation validity 0.909 → 0.318 and groundedness
0.955 → 0.318. The answers stayed right and stopped being checkable.

| target | correctness | citation validity | citation wellformed | fabricated-free | groundedness | $/1k queries |
|---|---|---|---|---|---|---|
| mini | 0.818 | 0.909 | 1.000 | 1.000 | 0.955 | **0.34** |
| gpt4o | **0.955** | **0.955** | 1.000 | 1.000 | 0.955 | 5.61 |
| terse | 0.909 | **0.318** | **0.364** | 1.000 | **0.318** | 0.32 |

Nothing was ever fabricated — zero invented clause references across all three
runs. An earlier version of the citation evaluator reported 77% hallucination on
`terse`; that was the evaluator's fault, not the model's, and correcting it is
written up in [`custom_evaluator.md`](lab_langsmith_ugo_ahukannah/custom_evaluator.md).

## File map

| Path | What it is |
|---|---|
| [`evaluation_summary.md`](evaluation_summary.md) | Step 10 — methodology, results, limitations, recommendation |
| [`optimization_summary.md`](optimization_summary.md) | Step 16 — cost/performance trade-off and when to pick each config |
| [`lab_langsmith_ugo_ahukannah/dataset_documentation.md`](lab_langsmith_ugo_ahukannah/dataset_documentation.md) | Steps 1, 3, 4 — domain, sources, data structure, LangSmith dataset |
| [`lab_langsmith_ugo_ahukannah/custom_evaluator.md`](lab_langsmith_ugo_ahukannah/custom_evaluator.md) | Steps 11–13 — custom evaluator design, the rewrite, what it revealed |
| [`lab_langsmith_ugo_ahukannah/corpus/`](lab_langsmith_ugo_ahukannah/corpus/) | The three source documents, 27 clauses |
| `lab_langsmith_ugo_ahukannah/questions.json` | 22-question bank with reference answers and clause citations |
| `lab_langsmith_ugo_ahukannah/corpus_index.py` | Parses the corpus into addressable clauses |
| `lab_langsmith_ugo_ahukannah/build_dataset.py` | Joins questions to clauses, validates, emits the dataset |
| `lab_langsmith_ugo_ahukannah/target_function.py` | The three traced target functions |
| `lab_langsmith_ugo_ahukannah/evaluators.py` | All five evaluators, with their controls |
| `lab_langsmith_ugo_ahukannah/run_evaluation.py` | Dataset upload and experiment execution |
| `lab_langsmith_ugo_ahukannah/analyze_results.py` | Analysis, judge audit, figures |
| `lab_langsmith_ugo_ahukannah/llm_evaluation_walkthrough.ipynb` | The whole pipeline as an executed notebook |
| `lab_langsmith_ugo_ahukannah/dataset_examples.json` | Generated dataset |
| `lab_langsmith_ugo_ahukannah/experiment_results.json` | Raw per-example results for all three experiments |
| `lab_langsmith_ugo_ahukannah/analysis_summary.json` | Aggregated metrics, breakdowns, judge audit |
| `lab_langsmith_ugo_ahukannah/figures/` | Comparison and difficulty charts |
| `lab_langsmith_ugo_ahukannah/screenshots/` | LangSmith UI: dataset overview and 3-experiment comparison |
| `lab_langsmith_ugo_ahukannah/run_*.command` / `.bat` | Double-clickable launchers, macOS and Windows |

## Rubric coverage

| Rubric rows | Where |
|---|---|
| 1, 14 — choose and prepare documents | `dataset_documentation.md`, `corpus/` |
| 2, 8, 16, 17 — custom LangSmith dataset, ≥10 examples | `build_dataset.py`, `questions.json`, `dataset_examples.json` (22 examples) |
| 3, 9, 18 — target function with tracing | `target_function.py` (`@traceable` + `wrap_openai`) |
| 4, 10, 15, 19, 20 — set up and run evaluations | `run_evaluation.py`, `evaluators.py` |
| 5, 11, 21, 22, 23 — analyse results, report, LangSmith UI | `analyze_results.py`, `evaluation_summary.md`, `screenshots/` |
| 6, 12, 24, 25, 26 — *(optional)* custom evaluators | `custom_evaluator.md`, `evaluators.py` — four custom evaluators |
| 7, 13, 27, 28, 29 — *(optional)* cost/performance | `optimization_summary.md`, three-way A/B in `analysis_summary.json` |

Both optional blocks are complete.

## Running it

```bash
cd lab_langsmith_ugo_ahukannah
pip install -r requirements.txt

python corpus_index.py             # parse the corpus            (free)
python build_dataset.py            # build + validate dataset    (free)
python evaluators.py               # evaluator controls          (~$0.001)
python target_function.py          # smoke-test on 3 examples    (~$0.001)

python run_evaluation.py --upload                    # create the LangSmith dataset
python run_evaluation.py --targets mini,gpt4o,terse  # the three experiments (~$0.14)
python analyze_results.py                            # analysis + figures (free)
```

Double-clickable launchers are provided for each: `run_*.command` (macOS) and
`run_*.bat` (Windows).

## API keys

Keys load at runtime from `~/.config/ironhack/.env.local` (mode `600`), outside
every git repo. **No key is stored in this repository**, and the notebook verifies
key presence by length and hash fingerprint rather than printing it. Required:
`OPENAI_API_KEY`, `LANGSMITH_API_KEY`, and — for an EU workspace, as here —
`LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com`. Against the default US
endpoint an EU key authenticates and then returns 403 on every call, which reads
as a bad key.

## Caveat

The corpus is modelled on the public structure of Regulation B and FCRA §615(a)
and on a plausible internal policy, but it was authored for this exercise and is
not legal advice. The evaluation measures faithfulness to that supplied corpus,
not real-world legal correctness.

---
---

# Original lab README

*Everything below is unmodified from the upstream lab repository.*

# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

This repository contains everything you need for this lab.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
