# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

This repository contains everything you need for this lab.

## Step 1: Domain and Documents

- **Domain:** Retail customer support, the same scenario used in the companion `lab-llm-judges` lab: a chatbot that handles returns, product questions, and complaints for an online retailer.
- **Sources:** Examples are written by hand, based on realistic support intents from two benchmarks researched in `lab-llm-judges/benchmark_audit.md`: the [ABCD dataset](https://github.com/asappresearch/abcd) (policy-bound refund and order-change dialogues) and the [Bitext Customer Support dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset) (intent categories such as ORDER, REFUND, DELIVERY, COMPLAINT). The 5 evaluation prompts from `lab-llm-judges/evaluation_design.md` are expanded into the fuller example set here.
- **What makes a good example:** Each example has an input (a realistic customer message: a policy question, an order status request, a complaint, a product question, or a policy-bypass attempt) and an expected output (what a correct, on-policy chatbot response should contain, not exact wording, since phrasing can vary). Examples are tagged with a category (matching the failure modes from `evaluation_design.md`: policy accuracy, honesty about missing data, tone, hallucination, safety) so results can be analyzed by category later.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against
- `01_openevals.ipynb`, `02_langsmith.ipynb`: reference notebooks with implementation patterns
- `langsmith_evaluation.ipynb`: dataset creation, target function, evaluators (correctness and tone), the evaluation run, the model A/B comparison, and results analysis
- `langsmith_ui_review.md`: notes from reviewing datasets and experiment traces directly in the LangSmith UI
- `evaluation_summary.md`: methodology, results, and the custom tone evaluator's findings
- `optimization_summary.md`: cost-performance comparison across `gpt-4o-mini`, `gpt-4o`, and `gpt-5.6-luna`
- `troubleshooting_notes.md`: real issues hit while building the notebook, and how they were fixed

## Dataset and experiments

- LangSmith dataset: `retail-chatbot-support-eval` (18 examples, 5 categories: policy_accuracy, honesty_missing_data, tone, hallucination, safety)
- LangSmith project: `retail-chatbot-eval` (EU region)
- Experiments are visible in the LangSmith UI under this project; each run in the notebook prints a direct link to its results.

## How to run the code

1. Create a `.env` file in this folder with `OPENAI_API_KEY` and `LANGSMITH_API_KEY`.
2. Install dependencies: `pip install langsmith openai python-dotenv`.
3. Open `langsmith_evaluation.ipynb` and run all cells in order.

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
