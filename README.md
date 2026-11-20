# LangSmith custom evaluation: EU AI Act consultant assistant

**Author:** Elif Yurdakul · Ironhack W7D4 · *LAB | Micromanage your agents*

**Reviewer entry point: [`lab_proof.md`](lab_proof.md)**

## Domain and dataset

An LLM assistant answers the EU AI Act questions that clients ask an AI consultant: Is this
use case banned? Is it high-risk? Who is the provider? When do the rules apply? Do we need a
FRIA? The dataset **`eu-ai-act-consultant-qa-v1`** has 18 hand-written question/answer pairs
across 10 categories. The reference answers come from the Ironhack W7 lesson decks and follow
the AI Act as amended by the **Digital Omnibus** (Regulation (EU) 2026/1744, July 2026).
Three of the questions depend on Omnibus dates, which are newer than most models' training
data. Details: [`docs/dataset_documentation.md`](docs/dataset_documentation.md).

## Approach

1. Hand-built JSON dataset → quality checks → uploaded to LangSmith (with metadata).
2. Target function: a traced consultant-style assistant (gpt-4o-mini, temperature 0, ≤120 words).
3. Evaluators:
   - `correctness`: OpenEvals `CORRECTNESS_PROMPT` as LLM-as-judge (gpt-5.4-mini).
   - `keyword_match`: rule-based check that the decisive terms (dates, risk level…) are present.
   - `advisory_quality` (optional part): custom LLM-as-judge on over-claiming, under-engaging and escalation.
4. Baseline experiment, then analysis by category, difficulty and post-cutoff facts.
5. A/B test on cost and performance:
   - gpt-4o-mini
   - gpt-5.4-mini
   - gpt-4o-mini with a six-line regulatory briefing

## How to run

```bash
pip install -r requirements.txt
cp .env.example .env        # add OPENAI_API_KEY and LANGSMITH_API_KEY (skip if you have a .env in a parent folder)
jupyter notebook lab_langsmith_eu_ai_act.ipynb
```

Run the cells top to bottom. In the setup cell, `LANGSMITH_ENDPOINT` is set to the EU region;
change it to `https://api.smith.langchain.com` for a US account. The dataset is created on the first run and reused after that. A full run
(5 experiments in total, about 200 API calls) costs well under $1.

**Headline result:** closed-book gpt-4o-mini got 11% right, answering from the 2021 draft of the Act. gpt-5.4-mini reached 50%. A six-line briefing fixed every post-Omnibus date question. See [`evaluation_summary.md`](evaluation_summary.md) and [`optimization_summary.md`](optimization_summary.md).

## LangSmith links

All experiments are in the dataset view (EU region):
[eu-ai-act-consultant-qa-v1](https://eu.smith.langchain.com/o/56d75618-ab53-46aa-9126-4d9ac8a5f936/datasets/f30b2b21-efd9-4000-ab2d-80447d226548)

| Experiment | Purpose | Result |
|---|---|---|
| `gpt-4o-mini-consultant-promptv1-1e89f2d3` | Main run: correctness + keyword | 11% / 6% |
| `gpt-4o-mini-consultant-promptv1-advisory-a4a820a4` | Custom evaluator: correctness + advisory quality | 18% / 0.60 |
| `config-a-gpt-4o-mini-34d795d9` | A/B, baseline | 17% |
| `config-b-gpt-5.4-mini-…` | A/B, model changed | 50% |
| `config-c-gpt-4o-mini-briefing-…` | A/B, system prompt + regulatory briefing | 28% (Omnibus questions 3 of 3) |

## File map

| File / folder | Purpose |
|---|---|
| `lab_proof.md` | Reviewer entry point: workflow, one traced run, evidence, output, limitation |
| `lab_langsmith_eu_ai_act.ipynb` | The instructor's lab notebook with every TODO completed (Parts 1–5 + both optional parts) |
| `data/eu_ai_act_qa_dataset.json` | The 18 examples: question, reference answer, key terms, metadata |
| `docs/dataset_documentation.md` | Domain, sources, data structure, field definitions, category list |
| `evaluation_summary.md` | Evaluation paragraph and key metrics (Step 10, written by the notebook) |
| `optimization_summary.md` | Cost/performance recommendation (Step 16, written by the notebook) |
| `outputs/` | Results CSVs, charts and LangSmith screenshots |
| `requirements.txt` / `.env.example` | Dependencies and environment template (`.env` is git-ignored) |
