# LAB Proof – LangSmith Model Evaluation

## 1. Project Overview

**LAB:** Micromanage Your Agents  
**Domain:** OWASP GenAI LLM Top 10 (2026)  
**Evaluation platform:** LangSmith (EU region)  
**Target model:** GPT-4o-mini  
**Judge model:** GPT-5-mini

This project evaluates how accurately GPT-4o-mini answers questions about LLM application security based on the OWASP GenAI LLM Top 10 (2026).

The evaluation uses 20 custom question-answer pairs covering all ten OWASP risk categories.

## 2. Implementation and Workflow

The evaluation workflow follows these steps:

1. Create a LangSmith dataset containing questions, reference answers, and metadata.
2. Send each question to GPT-4o-mini through a Python target function.
3. Compare the generated answers against the reference answers.
4. Apply two evaluators:
   - LLM-as-a-Judge correctness evaluation using GPT-5-mini.
   - Rule-based keyword overlap with a 25% threshold.
5. Store evaluation scores, model outputs, and traces in LangSmith.
6. Export results and analyze model performance.

The experiment was executed using `client.evaluate()` with `max_concurrency=2`.

**Implementation:** [Evaluation Notebook](lab_langsmith.ipynb)

## 3. Evidence of a Successful Evaluation

**Dataset:** `owasp-llm-top10-2026-v1`

**Total examples:** 20

**Experiment:** `gpt-4o-mini-owasp2026-promptv1-79cc73e8`

**Execution time:** Approximately 80 seconds

**Result:** All 20 examples were processed, with no missing evaluator scores.

[Open the LangSmith Experiment](https://eu.smith.langchain.com/o/30676eb8-0d5d-42d8-aa84-ca8c16dce2c5/datasets/f36ce8bb-1f79-441f-9c59-b78ca1a6929d/compare?selectedSessions=68548a5f-d128-4510-859b-3b6574eca64c)

The repository includes the following evaluation artifacts:

- `outputs/results_main.csv` – Evaluation results
- `outputs/pass_rate_by_category.png` – Performance visualization
- `evaluation_summary.md` – Summary of findings

## 4. Example Run: Prompt Injection

**Input question:**

Which three deployment-time properties make prompt injection vulnerabilities worse according to OWASP?

**Expected reference answer:**

Context-window pooling, memory persistence, and agentic execution.

**Actual GPT-4o-mini output:**

The model identified three different properties:

1. Lack of Input Validation
2. Overly Permissive Contexts
3. Inadequate User Authentication and Authorization

**LLM Judge result:** `False`

**Judge explanation:**

The generated response contains generally relevant security considerations but fails to identify the three specific deployment-time properties described in the reference answer.

**Conclusion:**

The model produced a plausible but factually incorrect answer. This demonstrates the importance of comparing model outputs against domain-specific reference answers instead of relying on fluency or terminology alone.

## 5. Final Evaluation Results

| Metric | Result |
|---|---|
| Total evaluation examples | 20 |
| LLM Judge correctness | 55% (11/20) |
| Keyword overlap | 95% (19/20) |
| Factual errors | 6 |
| Incomplete answers | 2 |
| Hallucinations | 1 |
| Missing evaluator scores | 0 |

The largest failure pattern was incorrect OWASP terminology and classification.

## 6. Challenges and Limitations

**API model availability**

The Bootcamp API project did not provide access to GPT-4o. We checked the available models through the OpenAI API and successfully verified GPT-5-mini as an alternative Judge model.

**Evaluator disagreement**

The keyword-overlap evaluator achieved a 95% pass rate, compared with 55% for the LLM Judge. Manual inspection showed that lexical similarity could produce positive scores for answers containing incorrect security classifications.

**Small evaluation dataset**

The dataset contains only 20 examples. Results are useful as an initial baseline but cannot establish general model reliability.

**Reference-answer dependency**

Judge decisions were evaluated against the supplied OWASP-based reference answers. The underlying references were not independently audited in full.

## 7. Recommended Improvement

A future iteration should provide the target model with relevant official OWASP source material through retrieval-augmented generation (RAG).

The updated system should then be tested against a larger, more balanced dataset to determine whether source grounding improves correctness and reduces terminology errors.

## 8. Supporting Evidence

The submission includes screenshots documenting:

- The LangSmith dataset and its examples
- The evaluation experiment and scores
- An individual run with its trace or evaluation feedback

These screenshots should be stored in the `outputs/` directory alongside the exported results and chart.