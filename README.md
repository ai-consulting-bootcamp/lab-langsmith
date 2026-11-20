# ShopCo — LangSmith Evaluation Lab

Start with [lab_proof.md](lab_proof.md) for the observed run,
evidence, results, and limitation.

## Domain and approach

This lab evaluates customer-support answers for ShopCo, a fictional
online store. The dataset contains 15 English examples covering
shipping, returns, and missing information.

Each input contains a question and the full policy.
Reference answers were prepared with AI assistance and manually reviewed.
The target uses gpt-4o-mini. Evaluation combines an OpenEvals correctness
judge using gpt-5.4-mini and a deterministic response-length check.

## How to run

1. Use Python 3.11 and open `02_langsmith.ipynb` in VS Code or Jupyter.
2. Create a local `.env` file using `.env.example`.
3. Add your OpenAI and LangSmith API keys.
4. Select the correct Python kernel.
5. Run the required notebook cells in order, from Part 1 to Part 5.
   The first cell installs dependencies.
6. The notebook uses the LangSmith EU endpoint.
   Use credentials from the same region.

Running the target and judge consumes API tokens.
Running the experiment again creates another experiment.
An existing dataset with the same name is not uploaded again.
If you change the dataset, use a new version name.

Optional Parts 1 and 2 were not completed.
Optional code cells were replaced with Markdown notes marking
these sections as not completed.

## LangSmith links

- [Dataset](https://eu.smith.langchain.com/o/17e08f1d-f35a-4236-b995-58ab83d3b83b/datasets/d2e58858-c5c6-4212-a8f5-1b48516a1f99)
- [Experiment](https://eu.smith.langchain.com/o/17e08f1d-f35a-4236-b995-58ab83d3b83b/datasets/d2e58858-c5c6-4212-a8f5-1b48516a1f99/compare?selectedSessions=fe23cce8-fa82-47c2-bcfe-171917718478)

Account access may be required. Local evidence is included below.

## File map

| File or folder | Purpose |
|---|---|
| `lab_proof.md` | Reviewer entry point with an observed run and evidence |
| `02_langsmith.ipynb` | Implementation, execution outputs, and analysis |
| `evaluation_summary.md` | Short evaluation report |
| `data/shopco_policy.md` | Fictional source policy |
| `data/shopco_examples_v1.json` | Full evaluation dataset |
| `outputs/` | Result CSVs, metrics, chart, and screenshots |
| `.env.example` | Environment variable template without secrets |
| `.gitignore` | Excludes local credentials and temporary files |
| `instructions.md` | Original lab instructions, if included |
| `rubric.md` | Original grading rubric, if included |