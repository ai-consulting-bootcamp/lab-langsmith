# Dataset documentation

## Domain and purpose

This lab evaluates whether an LLM can recommend an appropriate evaluation strategy for an AI-consulting scenario. Each scenario must be classified as **HUMAN**, **AUTOMATED**, or **HYBRID**, with a concise rationale. The task is useful for planning quality assurance because the right evaluation method depends on whether the desired judgment is deterministic, subjective, high-stakes, or a combination of these.

## Dataset identity

- **LangSmith dataset name:** `llm-evaluation-strategy-selection-v1`
- **Size:** 12 examples
- **Description:** Fictional AI-consulting scenarios for selecting human, automated, or hybrid LLM evaluation strategies.
- **Version:** v1, prepared 24 August 2026
- **Data classification:** Fictional; no personal, customer, or production data

## Sources

The examples were designed from the evaluation concepts in the course lab brief *Micromanage your agents* and the companion human-evaluation material. The implementation pattern follows the current LangSmith evaluation documentation and the OpenAI Responses API documentation. No third-party dataset was copied.

## Data structure

| Section | Field | Meaning |
|---|---|---|
| Input | `case_id` | Stable identifier used for analysis |
| Input | `scenario` | The evaluation-planning situation presented to the model |
| Input | `constraints` | Facts that affect the appropriate evaluation method |
| Reference output | `strategy` | One of `HUMAN`, `AUTOMATED`, or `HYBRID` |
| Reference output | `rationale` | Gold-standard explanation of the choice |
| Metadata | `category` | Primary evaluation problem represented by the case |
| Metadata | `difficulty` | `easy`, `medium`, or `hard` |
| Metadata | `source` | Provenance statement for the fictional case |

## Coverage

The reference labels are balanced: four HUMAN, four AUTOMATED, and four HYBRID examples. The cases cover deterministic accuracy, subjective quality, regulated communications, structured format compliance, safety, cultural sensitivity, code execution, ground-truth creation, judge validation, tool use, and fairness.

## What makes a good answer

A good answer selects exactly one allowed strategy, uses the scenario's stated constraints rather than inventing new facts, and explains the choice in one sentence of no more than 45 words. A HYBRID answer must identify a material role for both automated coverage and human judgment; it should not use “hybrid” merely as a cautious default.

## Quality checks

- Twelve unique case IDs and complete inputs/reference outputs
- Balanced gold labels
- No real personal or regulated data
- Explicit edge cases where scale and nuance conflict
- Credential-free tests in `tests/test_dataset.py`

