# LAB | Micromanage your agents - custom LangSmith dataset + evaluation

**Domain:** question answering over internal operational-risk policies (fictional Northwind Payments GmbH: incident management and vendor/outsourcing). **Dataset:** `northwind-policy-qa-v1`, 14 question/answer pairs with policy section references, including 2 out-of-scope questions that the assistant should refuse.

**Approach:** the examples are uploaded as a LangSmith dataset. A traced target function (`@traceable` plus a wrapped OpenAI client) answers from the policy text. `client.evaluate()` then scores each answer with two evaluators: an LLM-as-judge **correctness** check against the reference answer, and a code-based **grounded_citation** check (correct section cited, or "Not covered" for out-of-scope questions).

Start with **[lab_proof.md](lab_proof.md)**. LangSmith dataset and experiment links are in lab_proof.md and evaluation_summary.md.

## How to run
```
pip install -r requirements.txt
cp .env.example .env        # add your OPENAI_API_KEY and LANGSMITH_API_KEY
python langsmith_eval.py
```
The script creates the dataset (or reuses it), tests the target on 2 examples, runs the experiment, and writes the results and reports.

## File map
| File | Purpose |
|---|---|
| `lab_proof.md` | Reviewer entry point: workflow, one run with evidence, failure/limitation |
| `evaluation_summary.md` | Short evaluation report (paragraph + metric tables) |
| `langsmith_eval.py` | Dataset creation, target function, evaluators, experiment, analysis |
| `dataset_examples.json` | The 14 examples (inputs, reference outputs, metadata) |
| `docs/` | Source documents the dataset was built from |
| `results/eval_results.csv` | Per-example outputs, scores and judge reasoning |
| `.env.example` | Environment variables needed (no secrets) |
