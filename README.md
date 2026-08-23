# Clinical Trial Eligibility Evaluation with LangSmith

This project evaluates an LLM-based clinical trial eligibility screening assistant using **LangSmith**, deterministic evaluators, LLM-as-a-judge evaluation, cost/performance comparison, and a custom clinical decision-safety evaluator.

The screening task is based on curated examples from the **NCBI TrialGPT Criterion Annotations** dataset. For each patient note and trial criterion, the target model assigns one of four labels:

- `MET`
- `NOT MET`
- `UNKNOWN`
- `NOT APPLICABLE`

The assistant is designed as **screening support only**. It must stay grounded in the patient note, avoid inventing missing information, and leave final enrollment decisions to human review.

## Project Structure

```text
lab-langsmith/
├── data/
│   ├── curated_examples.json
│   └── trialgpt_criterion_annotations.parquet
├── results/
│   ├── evaluation_results.csv
│   ├── category_summary.csv
│   ├── difficulty_summary.csv
│   ├── failures.csv
│   ├── label_confusions.csv
│   ├── analysis_summary.md
│   ├── optimization_gpt-4o-mini.csv
│   ├── optimization_gpt-4.1.csv
│   ├── optimization_results.csv
│   ├── optimization_summary.csv
│   ├── optimization_case_comparison.csv
│   └── decision_safety_results.csv
├── notebooks/
│   └── data_exploration.ipynb
├── config.py
├── prepare_dataset.py
├── create_langsmith_dataset.py
├── target.py
├── evaluators.py
├── run_evaluation.py
├── analyze_results.py
├── optimization_targets.py
├── run_optimization.py
├── analyze_optimization.py
├── run_safety_evaluation.py
├── dataset_documentation.md
├── evaluation_summary.md
├── optimization_summary.md
├── custom_evaluator_summary.md
├── .env
├── .gitignore
└── README.md
```

## Dataset

The evaluation set contains **15 curated examples** derived from the public NCBI **TrialGPT Criterion Annotations** dataset.

The cases cover:

- clear inclusion criteria
- clear exclusion criteria
- missing information
- ambiguous evidence
- multiple criteria
- temporal reasoning
- boundary-value reasoning
- medical terminology
- mixed evidence
- not-applicable criteria

The curated examples are stored in:

```text
data/curated_examples.json
```

## Evaluation Approach

The baseline target model is `gpt-4o-mini`.

Two main evaluators are used:

1. **Label accuracy evaluator**  
   Deterministic comparison of predicted criterion labels against the expert-derived reference labels.

2. **Correctness evaluator**  
   An LLM-as-a-judge evaluator using `gpt-4.1-mini` with a task-specific rubric for the project label ontology.

The baseline evaluation achieved:

- Mean criterion-level label accuracy: **0.473**
- Fully correct cases: **6/15 (40%)**
- LLM-judge correctness rate: **6/15 (40%)**

The main baseline failure pattern was over-prediction of `NOT MET`, especially for exclusion criteria.

## Cost & Performance Optimization

The same 15 examples, prompt, dataset, and evaluators were used to compare:

- `gpt-4o-mini`
- `gpt-4.1`

| Metric | gpt-4o-mini | gpt-4.1 |
|---|---:|---:|
| Mean label accuracy | 0.473 | 0.867 |
| Correctness rate | 40% | 80% |
| Total target cost | $0.00234 | $0.03451 |
| Mean cost/example | $0.000156 | $0.002300 |
| Mean latency | 1.80 s | 1.23 s |

`gpt-4.1` improved 7 cases, performed worse on none, and tied on 8, but cost approximately **14.8× more**.

The comparison suggests that `gpt-4o-mini` is preferable for low-cost, high-volume screening with guaranteed human review, while `gpt-4.1` is the stronger choice when criterion-level accuracy is more important than marginal API cost.

## Custom Decision-Safety Evaluator

A custom `decision_safety` evaluator was added to measure behavior beyond correctness.

It checks whether the model:

- stays grounded in the supplied patient note
- preserves uncertainty when information is missing
- avoids unsupported clinical inference
- avoids deriving unreported clinical values
- does not make final enrollment decisions
- uses appropriately calibrated language

For `gpt-4.1`:

- Decision-safety pass rate: **14/15 (93.3%)**
- Correctness pass rate: **12/15 (80%)**

This showed that an answer can be incorrect without necessarily being unsafe.

The single safety failure occurred in an ambiguous-evidence case where the model inferred a confirmed lung-cancer diagnosis from a reported lung mass and classified the criterion as `MET` instead of preserving `UNKNOWN`.

## Setup

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=clinical-trial-eligibility-evaluation
```

Install the required packages in your environment:

```bash
python -m pip install "openai==2.45.0" langsmith openevals python-dotenv pandas pyarrow
```

## Running the Project

Prepare the curated local dataset:

```bash
python prepare_dataset.py
```

Create the LangSmith dataset:

```bash
python create_langsmith_dataset.py
```

Run the baseline evaluation:

```bash
python run_evaluation.py
```

Analyze baseline results:

```bash
python analyze_results.py
```

Run the model cost/performance comparison:

```bash
python run_optimization.py
```

Analyze optimization results:

```bash
python analyze_optimization.py
```

Run the custom decision-safety evaluation:

```bash
python run_safety_evaluation.py
```

## Main Findings

The evaluation showed that model quality depends strongly on both model capability and clear task-specific label semantics. A stronger target model substantially improved accuracy, but some failures remained even after model scaling. In particular, ambiguous clinical evidence and `NOT APPLICABLE` cases demonstrated that prompt design and ontology clarity remain important.

The project also showed that evaluation quality depends on the evaluators themselves. A generic correctness judge initially accepted an incorrect label interpretation, and the custom safety evaluator required structured output validation before its results could be trusted.

Overall, the lab demonstrates how LangSmith can be used not only to score model outputs, but also to compare models, inspect systematic failure modes, measure operational trade-offs, and introduce domain-specific evaluation criteria.
