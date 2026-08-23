# W7D5_LAB_Micromanage_your_agents
- Week 7 / Day 5
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-23
---

# EU ETS and FuelEU Maritime LangSmith Evaluation

This project evaluates an LLM question-answering system for EU ETS and FuelEU Maritime rules. The system answers questions using supplied regulatory context, and LangSmith records traces, experiment results, and correctness scores.

## Project Goal

The goal was to create a custom LangSmith dataset from official EU regulatory information, run an LLM evaluation, and analyze model performance.

## Dataset

- **Domain:** EU ETS maritime and FuelEU Maritime regulation
- **Initial LangSmith dataset:** 12 examples
- **Expanded evaluation set:** 20 examples
- **Inputs:** A question and a supporting context passage
- **Expected output:** A concise, factually correct answer grounded only in the supplied context
- **Sources:** Official European Commission transport and climate-policy pages

## Model and Evaluation

- **Target model:** `gpt-4o-mini`
- **Evaluation platform:** LangSmith
- **Evaluator:** LLM-as-a-judge correctness evaluator
- **Evaluation criterion:** Whether the model answer correctly matches the reference answer and is supported by the provided context

## Results

See [`evaluation_summary.md`](evaluation_summary.md) for the complete short evaluation report.

## How to Run

1. Clone this repository.
2. Create a `.env` file in the project root.
3. Add the required API keys:

   ```env
   LANGSMITH_API_KEY=your_langsmith_key
   OPENAI_API_KEY=your_openai_key
   ```

4. Install the required libraries:

   ```bash
   pip install langsmith openai openevals pandas python-dotenv matplotlib
   ```

5. Open and run `eu_ets_fueleu_evaluation.ipynb` from top to bottom.

Do not commit the `.env` file because it contains private API keys.

## File Map

| File or folder | Purpose |
|---|---|
| `eu_ets_fueleu_evaluation.ipynb` | Main notebook: dataset upload, target function, evaluator, experiment, pandas analysis, and visualizations |
| `eu_ets_fueleu_examples.json` | Structured EU ETS and FuelEU Maritime question-answer examples |
| `dataset_documentation.md` | Description of the domain, data structure, and dataset design |
| `source_notes.md` | Source links and notes from the official EU materials |
| `evaluation_summary.md` | Short report with methodology, results, failure pattern, limitations, and recommendation |
| `screenshots/` | LangSmith dataset, experiment, pandas-analysis, and failed-example screenshots |
| `instructions.md` | Original lab instructions |
| `rubric.md` | Lab assessment rubric |
| `.gitignore` | Prevents private files such as `.env` from being committed |

## Key Learning

This project demonstrates a complete evaluation workflow: create domain-specific examples, upload them as a LangSmith dataset, run a traced model experiment, measure correctness, inspect failures, and use the results to propose a specific prompt improvement.
