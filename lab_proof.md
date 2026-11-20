# LangSmith Lab Proof

## Submission Summary

- **Chosen domain:** Re-Twin and its ArTee product. ArTee is the primary subject because it has a clear product description and supports several testable capabilities. The evaluation dataset will test whether an AI assistant can explain Re-Twin's purpose, ArTee's features, and how the product fits within the wider battery energy storage system (BESS) platform.
- **Dataset name:** `Ironhack-LABLangSmith`
- **Dataset ID:** `3e9257b1-1b43-4f1b-b617-692664f76bc0`
- **Dataset description:** Evaluates whether an AI assistant can accurately explain Re-Twin and its ArTee digital energy analyst, including ArTee capabilities, Re-Twin platform context, battery storage analysis, and supporting Investment Analysis and Live Benchmarking modules.
- **Target model:** [Model name and configuration]
- **Experiment:** [LangSmith experiment name]
- **Experiment link or screenshot:** [Add a public or private-accessible link, or reference a screenshot in this repository.]

## Part 1: Setup & Document Selection

### Step 1: Choose Your Domain and Documents

**Domain description**

This lab evaluates whether an AI assistant can explain Re-Twin's project and product in simple, accurate words. The main focus is ArTee's purpose, capabilities, and role in helping users understand energy data, evaluate project scenarios, receive reports, and make decisions for battery energy storage systems.

**Document sources**

- [Re-Twin ArTee product page](https://www.re-twin.energy/de/artee)
- [Re-Twin platform overview](https://www.re-twin.energy/de/plattform-ubersicht)
- [Re-Twin Investment Analysis](https://www.re-twin.energy/de/investitionsanalyse)
- [Re-Twin Live Benchmarking](https://www.re-twin.energy/de/live-benchmarking)

**Re-Twin product scope for the dataset**

- **ArTee (primary subject):** Integrated digital energy analyst for project setup, scenario evaluation, result interpretation, 24/7 support, and automated reporting.
- **Re-Twin Platform (context):** Overall platform for evaluating, benchmarking, and maximizing the profitability of BESS assets throughout the project lifecycle.
- **Investment Analysis:** Models project-specific BESS data, compares scenarios, calculates operations and cash flow, and creates structured or bankable reports.
- **Live Benchmarking:** Places a digital twin under live market conditions to test strategies and compare simulated performance with actual or alternative assets.
- **Digital Twin:** Virtual representation of a BESS asset that combines project-specific technical data with live market data.
- **Automated Reporting:** Configurable performance reports delivered on a schedule to email or connected dashboards.
- **API Access:** Integration of live benchmark data into external dashboards.
- **Multi-Market Simulation:** Trading analysis across Day-Ahead, Intraday, FCR, aFRR, mFRR, and balancing markets.

ArTee is the clearest main product for this lab. Investment Analysis and Live Benchmarking should be included as context questions that test whether the assistant understands how ArTee fits into the Re-Twin platform, rather than replacing ArTee as the primary subject.

**Good-example criteria**

- **Input:** A user question about ArTee or Re-Twin, such as what ArTee does, how it supports project setup, or how it differs from the Investment Analysis and Live Benchmarking modules.
- **Expected output:** An accurate, concise product explanation based on Re-Twin's published product information.
- **Metadata:** Category (for example, `identity`, `capability`, `reporting`, `analysis`, or `platform-context`), difficulty, source page, and whether the answer requires external context.
- **Good example:** The answer names ArTee as Re-Twin's digital energy analyst and accurately explains the relevant feature or workflow.
- **Poor example:** The answer invents unsupported features, confuses ArTee with the whole platform, or misses the distinction between planning and live performance analysis.

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
| input | object | [Describe the input fields.] |
| output | object | [Describe the expected output fields.] |
| metadata | object | [Describe optional analysis fields.] |

**Example count:** [Number of examples]

**Example quality checks**

- [ ] At least 10 examples are included.
- [ ] Inputs are clear and independent.
- [ ] Outputs contain appropriate ground truth where available.
- [ ] Metadata is consistent.
- [ ] Unclear or incomplete examples were removed.

**Example data**

[Link to or embed a representative JSON/CSV example and the full dataset file.]

### Step 4: Create LangSmith Dataset

- **Dataset name:** `Ironhack-LABLangSmith`
- **Dataset ID:** `3e9257b1-1b43-4f1b-b617-692664f76bc0`
- **Dataset description:** Evaluates whether an AI assistant can accurately explain Re-Twin and ArTee, with supporting context for the Re-Twin platform, Investment Analysis, Live Benchmarking, and digital twin capabilities.
- **Upload method:** [Script or code used]
- **Verification:** [Describe or screenshot the dataset in the LangSmith UI.]
- **Example count verified:** [Number]

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
