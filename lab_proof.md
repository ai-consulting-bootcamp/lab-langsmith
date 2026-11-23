# LangSmith Lab Proof

## Submission Summary

- **Chosen domain:** Multi-hop factual question answering using Google's FRAMES benchmark.
- **Dataset name:** `FRAMES-Multi-Hop-QA-Evaluation`
- **Dataset ID:** `dc312e9b-cd59-4b89-9214-3e1ccd0d80d7`
- **Dataset description:** A 20-example subset of the FRAMES test split for evaluating answers to multi-hop factual questions against reference answers.
- **Target model:** `gpt-4o-mini`, temperature 0, maximum 512 tokens.
- **Experiment:** `frames-gpt-4o-mini-20261123-2123-197c6eca`
- **Experiment link:** [View the LangSmith experiment](https://eu.smith.langchain.com/o/edab2a5d-9667-472c-96d6-b273cacdf453/datasets/dc312e9b-cd59-4b89-9214-3e1ccd0d80d7/compare?selectedSessions=cb28b7ef-282e-40cf-9659-509a81d7ce74)

## Part 1: Setup & Document Selection

### Step 1: Choose Your Domain and Documents

**Domain description**

This lab evaluates whether an AI assistant can answer multi-hop factual questions using a subset of the FRAMES benchmark. Each prompt is an independent evaluation case; the dataset's `Answer` is used as the reference answer.

**Document sources**

- [Google FRAMES benchmark on Hugging Face](https://huggingface.co/datasets/google/frames-benchmark)

The benchmark has 824 rows in its `test` split. The notebook selects 20 examples and maps its `Prompt` and `Answer` fields to LangSmith input and output fields.

**Good-example criteria**

- **Input:** A FRAMES `Prompt` containing a multi-hop factual question.
- **Expected output:** The reference answer supplied in the FRAMES `Answer` field.
- **Metadata:** Reasoning type, supporting Wikipedia links, source dataset, and split.
- **Good example:** A non-empty prompt with a reference answer and reasoning metadata.
- **Excluded example:** A record with a missing prompt or answer.

### Step 2: Set Up LangSmith Environment

- **LangSmith endpoint:** EU (`https://eu.api.smith.langchain.com`)
- **Project name:** `langsmith-custom-dataset-evaluation`
- **Tracing status:** Working
- **Environment configuration:** A repository-root `.env` file is loaded by the setup notebook and `.gitignore` excludes it so credentials are not committed. The configuration uses `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, `LANGSMITH_TRACING=true`, `LANGSMITH_PROJECT=langsmith-custom-dataset-evaluation`, and `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com` (the notebook overrides the endpoint to the EU value).
- **Connection verification:** The setup notebook successfully loaded both API keys and initialized `langsmith.Client` and the LangSmith-wrapped OpenAI client. It completed a traced OpenAI greeting request and a `@traceable` test function, so tracing and client connectivity were working.

## Part 2: Dataset Creation

### Step 3: Extract and Structure Your Examples

**Data structure**

| Field | Type | Description |
|---|---|---|
| input | object | Contains `question`, mapped from the FRAMES `Prompt` field. |
| output | object | Contains `answer`, mapped from the FRAMES `Answer` field. |
| metadata | object | Contains `reasoning_types`, `wiki_links`, `source`, and `split` for analysis and provenance. |

**Configured example count:** 20 selected from the 824-row `test` split. The notebook ran and verified 20 uploaded examples.

**Example quality checks**

- [x] At least 10 examples are included (20 selected).
- [x] Inputs and reference outputs are non-empty.
- [x] Duplicate prompts are rejected.
- [x] Reasoning metadata is present on uploaded examples.
- [ ] No separate manual review/filtering of all source examples was performed.

**Example data**

The examples are extracted from FRAMES when the notebook runs. Raw benchmark records are not checked into this repository.

Representative example:

```json
{
  "input": {"question": "<FRAMES Prompt>"},
  "output": {"answer": "<FRAMES Answer>"},
  "metadata": {
    "reasoning_types": "<FRAMES reasoning types>",
    "wiki_links": "<supporting Wikipedia links>",
    "source": "google/frames-benchmark",
    "split": "test"
  }
}
```

### Step 4: Create LangSmith Dataset

- **Dataset name:** `FRAMES-Multi-Hop-QA-Evaluation`
- **Dataset ID:** `dc312e9b-cd59-4b89-9214-3e1ccd0d80d7`
- **Dataset description:** A 20-example subset of FRAMES for evaluating multi-hop question answering against reference answers.
- **Upload method:** The notebook loads the FRAMES `test` split, creates a LangSmith dataset, and uploads each prompt, reference answer, reasoning type, and source link metadata.
- **Verification:** The notebook confirmed all 20 uploaded examples have non-empty question and answer fields and reasoning metadata. The experiment is linked above; no UI screenshot is included.
- **Example count verified:** 20

**Previous dataset note:** The earlier HLE run created a separate `hle-mc-benchmark` dataset. It is not the FRAMES dataset; use `FRAMES-Multi-Hop-QA-Evaluation` for subsequent evaluation.

## Part 3: Evaluation Setup

### Step 5: Implement Target Function

**Target purpose**

The traced `target_function` receives an input dictionary with a non-empty `question` string and returns an `answer` generated by the OpenAI chat API. It is decorated with `@traceable(name="frames_target")`.

**Implementation details**

- **Code file:** [langsmith_custom_dataset_evaluation.ipynb](./langsmith_custom_dataset_evaluation.ipynb)
- **Model:** `gpt-4o-mini`
- **Temperature:** 0
- **Maximum tokens:** 512
- **Tracing:** Enabled with `@traceable` and LangSmith client configuration.
- **Error handling:** Invalid/empty inputs and empty model responses raise explicit errors; API failures are allowed to surface without fallback.

**Smoke test:** Three FRAMES questions ran through the target successfully. The calls returned non-empty answers; this verifies execution, not answer correctness.

### Step 6: Set Up Evaluators

**Built-in correctness evaluator**

- **Type:** LLM-as-judge via `create_llm_as_judge`.
- **Judge model:** `openai:gpt-4o-mini`.
- **Criteria:** Factual accuracy, completeness, and whether the answer addresses the question; wording differences alone are not errors.
- **Output format:** Boolean correctness feedback, normalized to 1.0/0.0 for score analysis, with judge comments where available.

**Additional evaluators**

None. The optional custom evaluator and cost/performance comparison were not implemented.

## Part 4: Run Evaluation

### Step 7: Execute Evaluation Experiment

- **Experiment:** `frames-gpt-4o-mini-20261123-2123-197c6eca`
- **Dataset:** `FRAMES-Multi-Hop-QA-Evaluation` (20 examples)
- **Target:** `target_function` (`frames_target`)
- **Evaluator(s):** `correctness_evaluator`
- **Concurrency:** 2
- **Result link or export:** [LangSmith experiment](https://eu.smith.langchain.com/o/edab2a5d-9667-472c-96d6-b273cacdf453/datasets/dc312e9b-cd59-4b89-9214-3e1ccd0d80d7/compare?selectedSessions=cb28b7ef-282e-40cf-9659-509a81d7ce74); see [score export](./frames_evaluation_scores.csv) and [metrics](./frames_evaluation_metrics.json).

### Step 8: Review Results in LangSmith UI

The notebook printed and reviewed all 20 per-example results, including generated answer, reference answer, judge score, latency, and error status. No UI screenshot is included. There were no failed target runs.

**Initial observations**

- The target answered the record-label parent-company question correctly (example `06554c83-ab08-450b-ae54-30752b70451b`, score 1.0).
- Several answers failed on multi-hop entity identification or exact requested outputs. For example, the Bronte Tower answer discussed its height but did not give the requested ranking; judge score 0.0.
- Some answers confidently supplied unsupported intermediate facts, such as the "future wife" example; the judge marked it incorrect.
- These are observations from this 20-example sample, not conclusions about all FRAMES questions.

## Part 5: Analysis & Reporting

### Step 9: Analyze Results

**Aggregate metrics**

| Metric | Value |
|---|---:|
| Example count | 20 |
| Scored examples | 20 |
| Mean score | 0.150 |
| Median score | 0.000 |
| Pass rate (score >= 0.5) | 15.0% (3/20) |
| Failed target runs | 0 |

**Performance by category**

| Category | Example count | Mean score | Pass rate | Observation |
|---|---:|---:|---:|---|
| Multiple constraints | 5 | 0.200 | 20.0% | Low performance in this small group. |
| Multiple constraints; temporal reasoning | 2 | 0.000 | 0.0% | No examples passed. |
| Numerical reasoning; multiple constraints; temporal reasoning | 2 | 0.000 | 0.0% | No examples passed. |
| Numerical reasoning; tabular reasoning; multiple constraints | 3 | 0.000 | 0.0% | No examples passed. |
| Numerical reasoning; tabular reasoning; multiple constraints; temporal reasoning | 1 | 0.000 | 0.0% | Single example; not generalizable. |
| Numerical reasoning; tabular reasoning; post processing; temporal reasoning | 1 | 0.000 | 0.0% | Single example; not generalizable. |
| Tabular reasoning; multiple constraints | 3 | 0.333 | 33.3% | One of three examples passed. |
| Tabular reasoning; multiple constraints; temporal reasoning | 2 | 0.500 | 50.0% | One of two examples passed. |
| Temporal reasoning | 1 | 0.000 | 0.0% | Single example; not generalizable. |

**Error analysis**

- **Observed failure modes:** Incorrect entity/fact selection, incomplete answers, and unsupported intermediate claims. The target receives no retrieved Wikipedia text despite the dataset containing supporting `wiki_links`.
- **Best-performing example:** `06554c83-ab08-450b-ae54-30752b70451b`, score 1.0.
- **Lowest-scoring example:** `042f3d1a-5dc0-41ac-a1d7-9bfacbb307bb`, score 0.0; it did not provide the requested ranking.
- **Root-cause hypotheses:** Multi-hop questions require precise intermediate facts, and a parametric-only target can hallucinate or miss time-sensitive details. These hypotheses require testing with retrieval-augmented context.
- **Limitations:** This is a 20-example subset of the 824-row test split. Scores are LLM-judge outputs and results should not be generalized to the full benchmark.

### Step 10: Create Evaluation Report

**Evaluation summary**

See [evaluation_summary.md](./evaluation_summary.md), [frames_evaluation_scores.csv](./frames_evaluation_scores.csv), and [frames_evaluation_metrics.json](./frames_evaluation_metrics.json).
