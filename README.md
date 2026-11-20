# MNM AG — Vendor Management Evaluation with LangSmith

**Track:** Module 5 — Evaluation & Strategy  
**When:** Week 7, Day 4  
**Status:** Required Lab — Core Evaluation Completed

## 1. Project Overview

This project evaluates an AI assistant designed to answer vendor management questions in Microsoft Dynamics 365 Finance & Operations (F&O).

The evaluation uses **MNM AG**, a fictional wholesale and distribution company with two legal entities, MNM-DE and MNM-NL.

The objective is to assess whether the assistant provides accurate answers based on the supplied company policies, follows vendor management rules, and avoids inventing information when the context is insufficient.

## 2. Dataset

**LangSmith Dataset:** `MNM-FNO-Vendor-Management-v1`

A custom dataset containing 15 question-and-answer examples was created and uploaded to LangSmith.

The dataset covers seven categories:

- Vendor creation
- Vendor configuration
- Payment configuration
- Multi-company vendor management
- Vendor controls
- Troubleshooting
- Unknown information

**Difficulty distribution:** 5 easy, 5 medium, and 5 hard examples.

Each example contains:

- `question` — the question submitted to the AI assistant
- `context` — fictional company policies and relevant information
- `answer` — the expected reference answer
- `category` — vendor management topic
- `difficulty` — easy, medium, or hard
- `source` — origin of the reference information

## 3. Implementation and Evaluation

The evaluation was implemented in Python using LangSmith and OpenAI.

**Target model:** `gpt-4o-mini`  
**Tracing:** LangSmith enabled  
**Dataset size:** 15 examples

Three evaluation dimensions were implemented:

1. **Correctness:** An LLM-as-a-judge evaluator checks whether the generated answer is consistent with the reference answer.
2. **Uncertainty handling:** A rule-based evaluator checks whether the assistant appropriately handles information that is unavailable in the provided context.
3. **Groundedness (custom evaluator):** An LLM-as-a-judge evaluator checks whether the generated answer is supported by the supplied company context without introducing unsupported claims.

The custom groundedness evaluator was also tested with correct, incorrect, and borderline answers before being used in a separate experiment.

## 4. Evaluation Results

| Metric | Result |
|---|---|
| Total examples | 15 |
| Correctness | 100% (15/15) |
| Uncertainty handling | 100% (15/15) |
| Groundedness (custom experiment) | 100% (15/15) |
| Evaluation errors | 0 |
| Correctness vs. groundedness disagreements | 0 |

All 15 examples passed the evaluators. The assistant also correctly declined to invent a vendor's bank account number when the information was unavailable.

These results demonstrate successful performance on the fictional test dataset, but do not establish reliability in real-world production scenarios.

**Detailed findings and recommendations:** See [`evaluation_summary.md`](./evaluation_summary.md).

## 5. LangSmith Experiments

**Dataset:** `MNM-FNO-Vendor-Management-v1`

**Main experiment:** `MNM-FNO-gpt4o-mini-v1-92e5bc11`

**Custom groundedness experiment:** `MNM-FNO-groundedness-v1-4d1abece`

The experiments can be reviewed in the LangSmith EU workspace under **Datasets & Experiments**.

Screenshots of the dataset, tracing, experiment results, and evaluator feedback are included in the `Screenshot/` folder.

## 6. Repository File Map

| File / Folder | Description |
|---|---|
| `MNM-F&O-Vendor-Evaluation_EU.ipynb` | Main Python notebook containing dataset creation, target function, evaluators, experiment execution, and analysis |
| `mnm_vendor_examples.json` | Structured dataset containing 15 examples |
| `evaluation_summary.md` | Evaluation methodology, findings, limitations, and recommendation |
| `outputs/results_main.csv` | Results from the main evaluation |
| `outputs/results_custom.csv` | Results from the custom groundedness evaluation |
| `outputs/pass_rate_by_category.png` | Correctness performance by category |
| `Screenshot/langsmith_dataset.png` | LangSmith dataset evidence |
| `Screenshot/langsmith_tracing.png` | Tracing evidence |
| `Screenshot/langsmith_experiment_results.png` | Main experiment results |
| `Screenshot/bank_account_trace.png` | Bank account uncertainty-handling example |
| `Screenshot/langsmith_bank_account_feedback.png` | Evaluator feedback for the bank account example |
| `instructions.md` | Original lab instructions |
| `rubric.md` | Submission grading criteria |
| `README.md` | Project overview and file documentation |

## 7. How to Run

1. Clone or download the repository.
2. Create a Python environment and install the required packages, including `langsmith`, `langchain`, `langchain-openai`, `openai`, `pandas`, and `matplotlib`.
3. Configure your OpenAI API key and LangSmith credentials locally using environment variables. Use the LangSmith EU endpoint for this project.
4. Open `MNM-F&O-Vendor-Evaluation_EU.ipynb` in VS Code or Jupyter.
5. Execute the notebook cells in sequence to create or verify the dataset, test the target function, run evaluations, and generate results.
6. Open LangSmith to inspect the traces, evaluator feedback, and experiments.

**Security:** API keys and `.env` files must not be committed to GitHub.

Running the evaluation again may create a new experiment and incur API usage costs.

## 8. Limitations and Recommendations

The evaluation used only 15 examples from a fictional company policy. Although all examples passed, the small dataset limits how confidently the results can be generalized.

The recommended next step is to expand the dataset with more challenging and ambiguous vendor management scenarios and independently review reference answers and evaluator decisions before testing with real company data.

## 9. Optional Extensions

The custom groundedness evaluator was implemented and tested successfully.

Cost and performance optimization, including A/B model comparisons, remains optional and has been deferred for future learning.

## 10. Original Lab Submission Instructions

This repository follows the Ironhack lab submission workflow:

1. Fork the original repository.
2. Complete the lab and commit the implementation and evidence to the fork.
3. Open a pull request to the original repository.
4. Review the automated feedback against `rubric.md` and address any blocking findings.

### Submission Hygiene

- Keep the repository limited to this lab.
- Use clear, descriptive filenames.
- Exclude secrets, API keys, tokens, and local environment files.
- Submit the GitHub repository URL, not a standalone cloud document.
- Keep evaluation findings in `evaluation_summary.md`, not in this README.