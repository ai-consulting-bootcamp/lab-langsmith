# TenderAI Model Evaluation

## Overview

This project evaluates the TenderAI tender-requirement classification workflow using LangSmith.

The evaluation measures how accurately `gpt-4.1-mini` classifies tender requirements against the expected classification using a custom evaluation dataset.

## Evaluation Setup

* **Dataset:** `TenderAI-Requirement-Evaluation-v1`
* **Examples:** 15
* **Model:** `gpt-4.1-mini`
* **Evaluator:** Exact-match correctness
* **Experiment:** `TenderAI-gpt-4.1-mini-10852ed7`
* **Framework:** LangSmith

## Results

The evaluation processed all 15 examples.

* **Correct:** 6/15
* **Incorrect:** 9/15
* **Accuracy:** 40%
* **Median latency:** approximately 0.745 seconds

The main observed failure pattern was a tendency to classify requirements as `INSUFFICIENT`, including several requirements that were expected to be `SUPPORTED`.

## Key Finding

The evaluated configuration is not reliable enough for production tender classification without further improvement.

Potential improvements include:

* Better prompting
* Stronger evidence grounding
* Retrieval of relevant company knowledge before classification
* Additional evaluation examples
* Testing alternative model configurations

## Repository Structure

```text
.
├── data/
│   └── tender_evaluation_dataset.json
├── results/
├── src/
│   ├── run_langsmith_evaluation.py
│   └── ...
├── evaluation_summary.md
├── evaluation_design.md
├── evaluation_memo.md
├── implementation_summary.md
├── benchmark_audit.md
├── llm_judge.md
├── evaluation_results.json
└── README.md
```

## Evaluation Limitation

The target function evaluated the requirement text without providing the underlying TenderAI knowledge-base evidence. Therefore, this experiment measures classification behavior rather than a complete evidence-grounded tender assessment.
