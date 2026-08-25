# Intellectus Operations/CX — LangSmith Evaluation

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![LangSmith](https://img.shields.io/badge/LangSmith-Evaluation-111111)
![OpenAI](https://img.shields.io/badge/OpenAI-Responses_API-412991?logo=openai&logoColor=white)
![Evaluation](https://img.shields.io/badge/Evaluation-12_cases-0B6E4F)
![Groundedness](https://img.shields.io/badge/Groundedness-100%25-2E7D32)
![Contract](https://img.shields.io/badge/Contract_Compliance-100%25-2E7D32)

A focused evaluation harness for the **Intellectus Operations/CX capability**, built to test whether an LLM can reproduce the evidence discipline and decision rules of Workflow 53 without inventing process facts, crossing domain boundaries, or weakening validation requirements.

---

## Why this repo exists

Intellectus does not need a model that simply sounds plausible. It needs one that can:

- separate observed facts from inference and unknowns;
- stay inside the Operations/CX evidence domain;
- preserve evidence traceability;
- surface validation questions when the evidence is incomplete;
- reject unsupported internal-process claims;
- avoid premature technology recommendations.

This repo turns those expectations into a repeatable evaluation system.

---

## Evaluation at a glance

| Layer | What it tests |
|---|---|
| **Correctness** | Whether the output matches the expected reference behaviour semantically |
| **Groundedness** | Whether findings remain supported by the supplied evidence |
| **Contract compliance** | Whether hard workflow rules are respected deterministically |

The benchmark uses **12 custom cases** designed around the actual behavioural constraints of the Intellectus Operations/CX workflow.

---

## Benchmark coverage

The dataset includes cases for:

- supported facts;
- inferred evidence;
- hypotheses;
- unknown / insufficient evidence;
- contradictions;
- strict domain filtering;
- evidence-ID integrity;
- donor journey signals;
- validation-question requirements;
- unsupported internal-process claims;
- recommendation boundaries;
- mixed evidence across domains.

The goal is not to maximise score on generic QA. It is to test whether the model behaves like the consulting workflow expects.

---

## Model comparison

Three target models were tested under the same dataset, prompt, references, evaluators and execution settings.

| Model | Correctness | Groundedness | Contract | Avg. latency | Target cost |
|---|---:|---:|---:|---:|---:|
| GPT-4o mini | 95.8% | 100% | 100% | 2.06 s | $0.0015 |
| **GPT-5.4 mini** | **97.9%** | **100%** | **100%** | 1.89 s | $0.0094 |
| GPT-5.4 | 95.8% | 100% | 100% | **1.82 s** | $0.0311 |

**Recommended default:** `gpt-5.4-mini`

It delivered the best quality-cost balance for this capability. `gpt-4o-mini` remains a useful low-cost fallback for higher-volume or lower-risk workloads.

For the full model decision, see [`optimization_summary.md`](optimization_summary.md).

---

## Repository structure

```text
langsmith-intellectus-agent-evaluation/
├── README.md
├── lab_proof.md
├── evaluation_summary.md
├── optimization_summary.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── evaluation_examples.json
│
├── src/
│   ├── create_dataset.py
│   ├── target.py
│   ├── evaluators.py
│   ├── run_evaluation.py
│   ├── compare_models.py
│   └── run_gpt4o_mini.py
│
├── results/
│   ├── model_comparison.csv
│   └── model_comparison.xlsx
│
└── evidence/
    ├── langsmith_model_comparison.png
    ├── langsmith_three_model_comparison.csv
    ├── model_quality_comparison.png
    ├── model_cost_comparison.png
    └── model_latency_comparison.png
```

---

## How it works

### 1. Dataset

`data/evaluation_examples.json` contains the 12 benchmark cases and their reference expectations.

The examples are uploaded to LangSmith as:

```text
intellectus-operations-cx-evaluation-v1
```

### 2. Target

`src/target.py` uses the OpenAI Responses API with structured output and LangSmith tracing.

The target returns:

- `finding`
- `finding_type`
- `evidence_ids`
- `requires_validation`
- `validation_question`

### 3. Evaluators

`src/evaluators.py` contains three complementary checks:

**Correctness evaluator**  
LLM-as-judge comparison against the reference behaviour.

**Groundedness evaluator**  
Custom evaluator focused on evidence support, unsupported claims, domain leakage and overstatement.

**Contract compliance evaluator**  
Deterministic checks for rules that should not depend on model judgement.

---

## Run locally

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create `.env` from `.env.example` and add your own credentials.

```env
OPENAI_API_KEY=
LANGSMITH_API_KEY=
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=intellectus-operations-cx-evaluation
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
TARGET_MODEL=gpt-5.4-mini
JUDGE_MODEL=gpt-5.4
```

Do not commit `.env`.

### Create or refresh the dataset

```bash
python src/create_dataset.py
```

### Run the baseline evaluation

```bash
python src/run_evaluation.py
```

### Run the low-cost GPT-4o mini baseline

```bash
python src/run_gpt4o_mini.py
```

### Run the model comparison workflow

```bash
python src/compare_models.py
```

---

## What the evaluation found

The main issue was not hallucination or contract failure.

The hardest case exposed a **calibration problem**: unsupported internal-process claims were handled safely, but the model sometimes added more uncertainty handling than the reference required.

That distinction matters. A grounded but over-elaborate answer is a different problem from an unsupported answer.

The next improvement is therefore narrow:

> tighten unsupported internal-process handling so the target returns the minimum defensible finding while preserving the existing grounding and validation safeguards.

See [`evaluation_summary.md`](evaluation_summary.md) for the baseline analysis.

---

## Evidence

The README stays intentionally concise. The full visual proof is in [`lab_proof.md`](lab_proof.md), including the three-model LangSmith comparison and the Python-generated quality, cost, and latency charts.

The consolidated metrics are available in [`evidence/model_comparison.csv`](evidence/model_comparison.csv), with the executive workbook in [`results/model_comparison.xlsx`](results/model_comparison.xlsx).

---

## Design principle

The evaluation is intentionally layered:

```text
Reference behaviour
        ↓
LLM target
        ↓
Semantic correctness
        +
Evidence grounding
        +
Deterministic contract checks
```

This makes the benchmark useful beyond a one-off lab. It can be reused as a regression suite when prompts, models or workflow rules change.
