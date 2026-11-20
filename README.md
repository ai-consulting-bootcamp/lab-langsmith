# LangSmith custom evaluation: EU AML compliance Q&A

Custom LangSmith evaluation of **gpt-4o-mini** answering EU anti-money-laundering (AML) compliance questions.

## Domain and dataset

- **Domain:** EU AML compliance: AMLD4/5, the 2024 AML package (AMLR, AMLA) and FATF standards. Inputs are practical compliance questions; expected outputs are short, article-referenced answers.
- **Sources:** EU AML Directive (2015/849 as amended), Regulation (EU) 2024/1624 (AMLR), Regulation (EU) 2024/1620 (AMLA), FATF Recommendations; reference answers written by me from a compliance background.
- **LangSmith dataset:** `aml-compliance-qa-v1`, 18 examples (6 easy, 7 medium, 5 hard) across 10 categories. [Dataset link](<DATASET URL>)
- **Structure** (`data/examples.json`):
  - `inputs.question`: the compliance question given to the model
  - `outputs.answer`: the reference (ground-truth) answer
  - `metadata.category`: topic (cdd, ubo, pep, edd, reporting, record_keeping, regulatory, fundamentals, typologies, scenario)
  - `metadata.difficulty`: easy / medium / hard
  - `metadata.source`: the legal provision the answer is based on

## Approach

1. Wrote 18 AML Q&A examples and uploaded them as a LangSmith dataset.
2. Target function: gpt-4o-mini, temperature 0, AML-assistant system prompt, traced with `@traceable` and the wrapped OpenAI client.
3. Evaluator: LLM-as-judge correctness (openevals `CORRECTNESS_PROMPT`), judged by gpt-4o-mini, comparing each answer to the reference.
4. Ran the evaluation with `client.evaluate()` and analysed the results by difficulty and category.

**Result:** 72% pass rate (13/18). See [evaluation_summary.md](evaluation_summary.md).
**Experiment:** [gpt-4o-mini-t0-baseline](https://eu.smith.langchain.com/o/448288b8-6568-4b16-965c-8f10ad23e35e/datasets/1664c068-5137-4318-acdf-78987ee98887/compare?selectedSessions=1bdd3d95-f411-4895-b01d-9ab5e8f813f7)

## How to run

```bash
pip install langsmith openai openevals langchain langchain-openai pandas matplotlib python-dotenv
```

Create a `.env` file in the root with `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com`, `LANGSMITH_PROJECT=aml-qa-eval` and `OPENAI_API_KEY`, then run:

```bash
python check_connection.py
python create_dataset.py
python aml_eval.py
python run_evaluation.py
python analyze_results.py
```

## File map

| File / folder | Purpose |
| --- | --- |
| `lab_proof.md` | **Reviewer entry point**: one run with input, evidence, output and a limitation |
| `evaluation_summary.md` | One-paragraph evaluation summary with key metrics |
| `instructions.md` / `rubric.md` | Original lab instructions and grading rubric |
| `data/examples.json` | The 18 AML Q&A examples (source of the dataset) |
| `check_connection.py` | Verifies the LangSmith and OpenAI connections |
| `create_dataset.py` | Creates the LangSmith dataset and uploads the examples |
| `aml_eval.py` | Target function and correctness evaluator (plus a 3-example test) |
| `run_evaluation.py` | Runs the full evaluation and exports results to CSV |
| `analyze_results.py` | Metrics by difficulty and category, failed examples, chart |
| `setup_structure.sh` | Creates the folder structure |
| `results/` | CSV exports, chart and LangSmith screenshots |
| `notebooks/` | Notebook workspace |