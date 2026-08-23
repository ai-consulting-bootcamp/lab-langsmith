# LangSmith Custom Evaluation Lab -- DoD Vehicle-Parts Contract Field Extraction

## Domain & Dataset
Real U.S. federal defense-vehicle procurement contract data pulled live from
the USAspending.gov public API (NAICS 336350/336330/336310/336399,
Department of Defense awards), reshaped into a structured field-extraction
task: given a natural-language contract notice, extract vendor name, award
amount, and award ID. See `dataset_documentation.md` for full details.

## Approach
1. Pulled 20 real contract awards via the USAspending.gov API
   (`fetch_contract_data.py`), reshaped 15 into LangSmith dataset examples
   (`structure_dataset.py`), uploaded to LangSmith (`create_langsmith_dataset.py`).
2. Built a traceable target function (`target_function.py`) using
   gpt-4o-mini to extract structured fields from each contract notice.
3. Built a rule-based correctness evaluator (`evaluator.py`) and ran the
   full evaluation (`run_evaluation.py`) -- scored a perfect 1.0, which
   `evaluation_summary.md` explains is a real but non-diagnostic result
   given how mechanical the base task is.
4. To stress-test further, hand-authored 5 hard edge cases (missing data,
   multi-vendor notices, ambiguous currency) (`create_edge_case_dataset.py`)
   and built a second custom evaluator measuring format/type compliance and
   honest null-handling (`custom_evaluator.py`), run via
   `run_edge_case_evaluation.py` -- see `custom_evaluator_analysis.md` for
   the comparison findings and a real bug caught and fixed mid-development.
5. Ran an A/B cost/performance comparison between gpt-4o-mini and gpt-4o
   (`run_ab_comparison.py`) -- see `optimization_summary.md`.

## LangSmith Links
- Main dataset: https://eu.smith.langchain.com/o/8cf5c25b-f325-47d9-9b55-55170ffd5e23/datasets/5ccaaafc-e5d3-4f86-8c29-f45dac39d45e
- Edge-case dataset: https://eu.smith.langchain.com/o/8cf5c25b-f325-47d9-9b55-55170ffd5e23/datasets/e46144a4-9676-4e00-ab99-e7df765e6d42
- Main evaluation experiment: gpt-4o-mini-extraction-5c712fe2
- Edge-case evaluation experiment: gpt-4o-mini-edge-cases-4875a303
- A/B comparison experiments: ab-compare-gpt-4o-mini-a1845321, ab-compare-gpt-4o-3374d4cb

## File Map
- `fetch_contract_data.py` -- pulls raw award data from USAspending.gov API
- `raw_contract_awards.json` -- raw API response (20 awards)
- `structure_dataset.py` -- reshapes raw awards into extraction examples
- `dataset_examples.json` -- 15 structured examples (input/output/metadata)
- `create_langsmith_dataset.py` -- uploads main dataset to LangSmith
- `create_edge_case_dataset.py` -- creates + uploads 5 hand-authored edge cases
- `target_function.py` -- traceable extraction function (gpt-4o-mini), plus
  a model-configurable factory used for the A/B comparison
- `evaluator.py` -- rule-based correctness evaluator
- `custom_evaluator.py` -- format/type-compliance evaluator (optional)
- `run_evaluation.py` -- runs the main evaluation experiment
- `run_edge_case_evaluation.py` -- runs both evaluators against edge cases
- `run_ab_comparison.py` -- gpt-4o-mini vs gpt-4o cost/performance comparison
- `dataset_documentation.md` -- domain, source, and data structure documentation
- `evaluation_summary.md` -- required evaluation summary (Step 10)
- `custom_evaluator_analysis.md` -- custom evaluator design + results (Steps 11-13)
- `optimization_summary.md` -- cost/performance recommendation (Step 16)

## How to Run
1. Activate the `bootcamp-env` conda environment.
2. Create a `.env` file with `OPENAI_API_KEY`, `LANGSMITH_API_KEY`,
   `LANGSMITH_TRACING=true`, `LANGSMITH_ENDPOINT` (region-specific --
   this account uses the EU endpoint), and `LANGSMITH_PROJECT`.
3. Run scripts in order: `fetch_contract_data.py` -> `structure_dataset.py`
   -> `create_langsmith_dataset.py` -> `create_edge_case_dataset.py` ->
   `run_evaluation.py` -> `run_edge_case_evaluation.py` -> `run_ab_comparison.py`
4. Results are visible in the LangSmith UI at the links above.
