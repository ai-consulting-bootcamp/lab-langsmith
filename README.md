# Micromanage your agents

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 4 · **Status:** Required

Custom LangSmith evaluation of gpt-4o-mini as a SaaS customer support agent, built against 20 tickets from the Bitext customer support dataset.

## Domain and dataset

Domain: customer support tickets for a SaaS/automation product. Categories: account, subscription, payment, refund, invoice.

Source: `bitext/Bitext-customer-support-llm-chatbot-training-dataset` on Hugging Face, filtered from 11 categories down to the 6 SaaS-relevant ones, then sampled to 20 examples (seed 42).

LangSmith dataset: `saas-support-tickets`

## Approach

1. Loaded and filtered the Bitext dataset, uploaded 20 examples to a LangSmith dataset.
2. Built a target function: gpt-4o-mini answering as a support agent.
3. Built a correctness evaluator using openevals' `CORRECTNESS_PROMPT` with a Claude Haiku judge.
4. Ran the evaluation, reviewed results in the LangSmith UI, analyzed by category.
5. Built a custom evaluator, actionability, scoring whether responses give concrete next steps versus vague pointers.
6. Ran both evaluators together, compared agreement.
7. A/B compared gpt-4o-mini against gpt-4o on cost, correctness, and latency.

## How to run

1. Activate the conda env: `conda activate My_class_repo_conda`
2. Install packages: `pip install langsmith openai openevals datasets python-dotenv langchain-anthropic -U`
3. Set `.env` with `LANGSMITH_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
4. Open `langsmith_support_eval.ipynb`, run cells top to bottom
5. LangSmith is on the US endpoint (`api.smith.langchain.com`), not EU

## LangSmith links

- Dataset: `saas-support-tickets`
- Main experiment (correctness only): `gpt-4o-mini-support-ebd06ada`
- Dual-evaluator experiment (correctness + actionability): `gpt-4o-mini-support-dual-606c9af0`
- A/B experiment (gpt-4o): `gpt-4o-support-e5a88e33`

## File map

| File | Purpose |
|---|---|
| `instructions.md` | Original lab instructions |
| `rubric.md` | Grading rubric |
| `README.md` | This file |
| `langsmith_support_eval.ipynb` | All code: dataset creation, target function, evaluators, experiments |
| `data/support_tickets.json` | Local copy of the 20 filtered examples |
| `evaluation_summary.md` | Required deliverable: methodology, results, custom evaluator findings |
| `optimization_summary.md` | Optional deliverable: cost/performance comparison, gpt-4o-mini vs gpt-4o |

## Key finding

Correctness averaged 0.35 for gpt-4o-mini. Biggest failure pattern: account-category tickets (0/6), where the model gives short general answers but the reference expects scripted step-by-step instructions. The custom actionability evaluator only agreed with correctness 50% of the time, showing the two catch different failure modes. gpt-4o scored higher on correctness (0.57) but cost roughly 12x more per correct answer.