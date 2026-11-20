# LangSmith Evaluation Lab: Living in Germany Q&A

**Lab:** Micromanage your agents (LangSmith evaluation) · **Author:** Barsha Mishra

## Domain and dataset

An assistant for **newcomers living in Germany** answers practical questions (Anmeldung, tax ID, minimum wage, Deutschlandticket, Rundfunkbeitrag, Kindergeld, Pfand, Sunday shopping, health insurance, emergency numbers) **using only a short context paragraph**.

- **LangSmith dataset:** `living-in-germany-qa-v1` (EU region), **19 examples** in 6 categories, 8 easy / 7 medium / 4 hard
- **Fields:** inputs = `question`, `context` · outputs = `answer` (reference) · metadata = `category`, `difficulty`, `source`
- **Custom dataset:** written for this lab (by me, with help from Claude). Each context summarises official information in my own words (bundesregierung.de, service.berlin.de, deutschlandticket.de / bahn.de, rundfunkbeitrag.de, arbeitsagentur.de, make-it-in-germany.com). Changing figures were checked in November 2026: Deutschlandticket 63 €, minimum wage 13.90 €, Rundfunkbeitrag 18.36 €, Kindergeld 259 €.
- **Includes:** 3 trap questions that the context does not answer, and 2 calculation questions

## Approach

1. **Target:** `gpt-4o-mini`, temperature 0, system prompt "answer only from the context; if the answer is missing, say so", traced with `@traceable` and a wrapped OpenAI client.
2. **Evaluators:**
   - **correctness:** LLM-as-a-judge, OpenEvals `CORRECTNESS_PROMPT` with `gpt-5.4-mini`
   - **key_facts_match:** free rule-based check (trap phrase present, key numbers present)
3. **Experiment:** `client.evaluate(...)` with prefix `gpt-4o-mini-promptv1`, `max_concurrency=2`.
4. **Analysis:** pass rates overall, by category and by difficulty; error analysis using the judge's comments.

**Result:** 79 % correctness (15/19). Main failure pattern: **wrong refusals** (4/4 failures), with **no hallucinations**. See `evaluation_summary.md`.

## LangSmith links

- **Experiment:** https://eu.smith.langchain.com/o/3a0834ef-79bf-4dc2-80d3-2f65dcd44277/a/-/datasets/96bc0a98-d200-4547-94ab-9c46ad9d7d0f/compare?selectedSessions=a26327ee-9f7d-4e1b-8b69-2c839490c92e
- **Dataset:** `living-in-germany-qa-v1` in the EU workspace (LangSmith links need access to my workspace; screenshots are in `outputs/`)

## How to run

1. Create a `.env` file (never commit it):
   ```
   LANGSMITH_API_KEY=your-key
   OPENAI_API_KEY=your-key
   ```
2. Install the packages: `pip install langsmith openai openevals python-dotenv pandas matplotlib`
3. Open `living_in_germany_langsmith_evaluation.ipynb` and run all cells top to bottom. The dataset cell skips the upload if the dataset already exists. Each run of `client.evaluate` creates a new experiment.

The notebook uses the **EU** endpoint (`https://eu.api.smith.langchain.com`).

## File map

| File / folder | What it is |
|---|---|
| `lab_proof.md` | **Entry point:** workflow, one run with input, evidence, output, and one failure |
| `evaluation_summary.md` | One-paragraph evaluation summary with a metrics table |
| `living_in_germany_langsmith_evaluation.ipynb` | The full lab notebook: setup, dataset, target, evaluators, experiment, analysis |
| `outputs/results_main.csv` | Results for all 19 examples (inputs, answers, references, scores) |
| `outputs/metrics_overall.csv` | Pass rate per evaluator |
| `outputs/error_analysis.csv` | Failed examples with judge comments and failure types |
| `outputs/pass_rate_by_category.png` | Bar chart: correctness by category |
| `outputs/screenshot_dataset.png` | LangSmith dataset view |
| `outputs/screenshot_experiment.png` | LangSmith experiment table |
| `outputs/screenshot_trace.png` | One trace: the minimum wage question (wrong refusal) |
| `.gitignore` | Keeps `.env` and API keys out of the repo |

Optional parts (custom evaluator, A/B cost test) were not completed.
