# LangSmith Lab Proof

## Submission Summary

- **Chosen domain:** Questions from the text-only, multiple-choice portion of Humanity's Last Exam (HLE), a broad academic benchmark.
- **Dataset name:** `HLE-Multiple-Choice-Evaluation`
- **Dataset ID:** Record the ID printed by the notebook after creating/verifying this dataset.
- **Dataset description:** A 20-example text-only, multiple-choice subset of HLE for testing answer generation against the dataset's reference answers across subject categories.
- **Target model:** [Model name and configuration]
- **Experiment:** [LangSmith experiment name]
- **Experiment link or screenshot:** [Add a public or private-accessible link, or reference a screenshot in this repository.]

## Part 1: Setup & Document Selection

### Step 1: Choose Your Domain and Documents

**Domain description**

This lab evaluates whether an AI assistant can answer multiple-choice questions from a small, text-only HLE subset. Each question is one independent evaluation case; the HLE answer is used as the reference answer.

**Document sources**

- [HLE dataset on Hugging Face](https://huggingface.co/datasets/cais/hle)
- [Hugging Face dataset viewer API](https://datasets-server.huggingface.co/rows?dataset=cais%2Fhle&config=default&split=test&offset=0&length=100)

The HLE dataset is gated. A Hugging Face account must be granted access, and a read token must be available locally as `HF_TOKEN` before the notebook can load it. The notebook filters for multiple-choice examples without images and takes the first 20 matching rows.

**Good-example criteria**

- **Input:** An HLE multiple-choice question with its answer options.
- **Expected output:** The reference answer supplied by HLE.
- **Metadata:** HLE subject category, source dataset, split, and answer type.
- **Good example:** A text-only multiple-choice question with a non-empty reference answer and a valid category.
- **Excluded example:** An image-based item, a non-multiple-choice item, or a record with missing question, answer, or category.

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
| input | object | Contains `question`, the HLE question sent to the model. |
| output | object | Contains `answer`, the HLE reference answer. |
| metadata | object | Contains `category`, `source`, `split`, and `answer_type` for filtering and analysis. |

**Example count:** 20 (the notebook previously loaded and uploaded 20; rerun the updated upload/verification cell for the correctly named dataset).

**Example quality checks**

- [x] At least 10 examples are included.
- [x] Inputs are clear and independent.
- [x] Outputs contain appropriate ground truth where available.
- [x] Metadata is consistent.
- [x] Unclear or incomplete examples were removed.

**Example data**

The examples are extracted from HLE when the notebook runs; the dataset is gated, so raw records are not checked into this repository.

Representative example:

```json
{
  "input": {"question": "<text-only HLE multiple-choice question>"},
  "output": {"answer": "<HLE reference answer>"},
  "metadata": {
    "category": "<HLE subject category>",
    "source": "cais/hle",
    "split": "test",
    "answer_type": "multipleChoice"
  }
}
```

### Step 4: Create LangSmith Dataset

- **Dataset name:** `HLE-Multiple-Choice-Evaluation`
- **Dataset ID:** Record after rerunning the updated notebook cell.
- **Dataset description:** A 20-example text-only, multiple-choice subset of HLE for evaluation across academic subject categories.
- **Upload method:** The notebook loads HLE, creates a LangSmith dataset, and uploads each question, reference answer, and metadata.
- **Verification:** The notebook verifies the uploaded count and that examples contain inputs and outputs. Add a LangSmith UI screenshot or dataset URL after rerunning the updated upload cell.
- **Example count verified:** Pending rerun of the updated upload and verification cell.

**Previous dataset note:** An earlier run created a dataset named `Re-Twin-benchmark` using HLE questions. Its name and description do not match its contents; use the correctly named HLE dataset for subsequent evaluation.

## Part 3: Evaluation Setup

### Step 5: Implement Target Function

**Target purpose**

[Describe what the function receives and returns.]

**Implementation details**

- **Code file:** [Link to the target function code.]
- **Model:** [Model name]
- **Temperature:** [Value]
- **Maximum tokens:** [Value]
- **Tracing:** [Yes, with `@traceable` / LangSmith wrapping]
- **Error handling:** [Describe retries or fallback behavior.]

**Smoke test**

| Example | Result | Notes |
|---|---|---|
| [Example 1] | [Pass / fail] | [Notes] |
| [Example 2] | [Pass / fail] | [Notes] |
| [Example 3] | [Pass / fail] | [Notes] |

### Step 6: Set Up Evaluators

**Built-in correctness evaluator**

- **Type:** [LLM-as-judge or other]
- **Judge model:** [Model name]
- **Criteria:** [Define what correct means.]
- **Output format:** [Score and reasoning fields.]

**Additional evaluators**

[Document any evaluators used beyond correctness.]

## Part 4: Run Evaluation

### Step 7: Execute Evaluation Experiment

- **Experiment prefix:** [Name]
- **Dataset:** [Dataset name]
- **Target:** [Target function name]
- **Evaluator(s):** [Names]
- **Concurrency:** [Value]
- **Result link or export:** [Link or file path]

### Step 8: Review Results in LangSmith UI

[Add the LangSmith UI screenshot or summarize the aggregate metrics and individual-example review.]

**Initial observations**

- [High-performing pattern]
- [Low-performing pattern]
- [Interesting or surprising example]

## Part 5: Analysis & Reporting

### Step 9: Analyze Results

**Aggregate metrics**

| Metric | Value |
|---|---:|
| Example count | [N] |
| Mean score | [Value] |
| Median score | [Value] |
| Pass rate | [Percentage] |
| [Additional metric] | [Value] |

**Performance by category**

| Category | Example count | Mean score | Pass rate | Observation |
|---|---:|---:|---:|---|
| [Category] | [N] | [Value] | [Percentage] | [Observation] |

**Error analysis**

- **Most common failure mode:** [Description]
- **Best-performing example:** [Describe and give a score.]
- **Worst-performing example:** [Describe and give a score.]
- **Root-cause hypotheses:** [List possible causes.]

### Step 10: Create Evaluation Report

**Evaluation summary**

See [`evaluation_summary.md`](./evaluation_summary.md).
