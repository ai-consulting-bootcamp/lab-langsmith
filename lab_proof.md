# Lab proof: custom LangSmith evaluation (EU AML compliance Q&A)

Entry point for the reviewer. Background, how to run and the file map are in [README.md](README.md); the summary is in [evaluation_summary.md](evaluation_summary.md).

## Code / workflow

`check_connection.py` → `create_dataset.py` → `aml_eval.py` (target + evaluator) → `run_evaluation.py` → `analyze_results.py`

- Dataset: `aml-compliance-qa-v1`, 18 examples, from [data/examples.json](data/examples.json)
- Target: gpt-4o-mini, temperature 0, `@traceable` + `wrappers.wrap_openai` (tracing on, project `aml-qa-eval`)
- Evaluator: openevals LLM-as-judge correctness (`CORRECTNESS_PROMPT`, judge gpt-4o-mini)
- Experiment: [gpt-4o-mini-t0-baseline](https://eu.smith.langchain.com/o/448288b8-6568-4b16-965c-8f10ad23e35e/datasets/1664c068-5137-4318-acdf-78987ee98887/compare?selectedSessions=1bdd3d95-f411-4895-b01d-9ab5e8f813f7)

## One run: input → evidence → output

**Input** (category `ubo`, difficulty `hard`):
> If no natural person can be identified as beneficial owner of a company after exhausting all means, who should be recorded under the EU AML Directive?

**Final output** (gpt-4o-mini):
> Under the EU AML framework, specifically Article 3(6) of the 4th Anti-Money Laundering Directive (AMLD IV), if no natural person can be identified as the beneficial owner after exhausting all means, the company itself should be recorded as the beneficial owner. …

**Reference answer:**
> The natural person(s) holding the position of senior managing official, provided there are no grounds for suspicion; the obliged entity must keep records of the actions taken to identify the beneficial owner.

**Evidence:** correctness = **False**. The judge's reasoning and the full trace are in [results/failed_example_ubo.png](results/failed_example_ubo.png). The model cites the right article but gives the wrong rule; in practice, recording the company as its own UBO would be a compliance failure.

## Results

- Pass rate **72% (13/18)**: easy 100%, medium 57%, hard 60%; regulatory 0/2
- Screenshots: [dataset_uploaded.png](results/dataset_uploaded.png) · [experiment_overview.png](results/experiment_overview.png) · [pass_rate_by_category.png](results/pass_rate_by_category.png)
- Data: [baseline_results.csv](results/baseline_results.csv) · [baseline_results_with_metadata.csv](results/baseline_results_with_metadata.csv)

## UI review notes (Step 8)

- All 6 easy questions passed; failures cluster in exact thresholds, article numbers and the 2024 AML package.
- Failures: occasional-transaction threshold (said €10,000, correct €15,000), UBO fallback (above), AMLA (no Frankfurt, called it a "proposal"), former PEP and AMLR cash limit (core figure right but wrong article and missing detail; the judge is arguably strict here).
- Pattern: confident but wrong citations. The model states article numbers with no hedging.

## Failure / limitation hit

1. **Judge model:** my OpenAI project has no access to `gpt-4o` (403 `model_not_found`), so gpt-4o-mini judges its own answers. That is not an independent judge and may bias scores.
2. **Small, single-author dataset:** 18 examples with reference answers written by one person; per-category results rest on 1–3 examples.

## Rubric map

| Rubric item | Evidence |
| --- | --- |
| Steps 1 & 3: domain, documents, examples | README "Domain and dataset", `data/examples.json` |
| Step 2: environment | `check_connection.py`, `.env` template in README |
| Step 4: dataset (≥10 examples) | `create_dataset.py`, `results/dataset_uploaded.png` |
| Step 5: target function with tracing | `aml_eval.py` → `target()` |
| Step 6: evaluator | `aml_eval.py` → `correctness_evaluator()` |
| Step 7: evaluation run | `run_evaluation.py`, experiment link above |
| Step 8: UI review | screenshots + notes above |
| Steps 9 & 10: analysis + report | `analyze_results.py`, `evaluation_summary.md` |