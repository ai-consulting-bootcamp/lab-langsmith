# LangSmith evaluation lab: EU AI Act Q&A

Ironhack AI bootcamp, Week 7 Day 4: "Micromanage your agents".

I built my own evaluation dataset for one use case, uploaded it to LangSmith, ran an experiment on `gpt-4o-mini` and reported the results.

## Domain and dataset
- **Use case:** a Q&A assistant that answers business questions about the EU AI Act (Regulation (EU) 2024/1689), e.g. "Can we use AI to detect employees' emotions during video calls?"
- **Source:** official text on EUR-Lex: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- **Dataset:** `eu-ai-act-qa-v1` in LangSmith, with 19 examples
  - **Inputs:** `question` plus `context` (a short plain-English summary of the relevant article)
  - **Reference output:** `answer` (verdict plus article)
  - **Metadata:** `category`, `difficulty`, `source`
- **Categories:** prohibited practices (5), scope/timeline (4), high-risk (3), penalties/obligations (3), transparency (2), unanswerable (2)
- **Difficulty:** 7 easy, 6 medium, 6 hard. The hard examples are traps: exceptions to a rule, the SME fine rule, a "not automatically high-risk" case, and questions the context cannot answer.

## Approach
1. **Target:** `gpt-4o-mini`, temperature 0. The system prompt tells it to answer only from the context, start with a verdict, cite the article, and say "The context does not say." when the answer isn't there.
2. **Evaluators:**
   - `correctness`: LLM-as-a-judge (OpenEvals `CORRECTNESS_PROMPT`, judge model `gpt-5.4-mini`)
   - `cites_correct_article`: a rule-based check that the answer cites the same article(s) as the reference, or says "does not say" for unanswerable questions
3. **Experiment:** `client.evaluate()` on the full dataset, then analysis by category and difficulty, plus error analysis.

## Results
| Metric | Final run | Range over 3 runs |
|---|---|---|
| Correctness (LLM judge) | 100% (19/19) | 95–100% |
| Cites correct article (rule-based) | 100% (19/19) | 100% |

Full write-up: [`evaluation_summary.md`](evaluation_summary.md). Walkthrough of one run: [`lab_proof.md`](lab_proof.md).

## LangSmith links
- Final experiment (`gpt-4o-mini-promptv1-rulefix-9edb81ae`): https://eu.smith.langchain.com/o/6a443e3e-a646-46d2-8426-409f0215ab77/datasets/516fe224-9104-44fa-99fd-fd6dfd3bf85a/compare?selectedSessions=eefea85a-9afb-4420-b164-c0021d1d4f89
- Dataset `eu-ai-act-qa-v1`: in the same workspace, under Datasets & Experiments (EU region)

## How to run
1. Install the packages:
   ```
   pip install langsmith openai openevals python-dotenv pandas matplotlib
   ```
2. Create a `.env` file next to the notebook:
   ```
   OPENAI_API_KEY=sk-...
   LANGSMITH_API_KEY=lsv2_...
   ```
3. Open `lab_langsmith_eu_ai_act.ipynb` and run the cells top to bottom.
   - The notebook uses the **EU** LangSmith endpoint. If your account is on `smith.langchain.com` (US), change `LANGSMITH_ENDPOINT` to `https://api.smith.langchain.com`.
   - The dataset upload is skipped if `eu-ai-act-qa-v1` already exists.
   - Each run of Step 7 creates a new experiment, and scores can vary slightly between runs.

## File map
| File | What it is |
|---|---|
| `lab_proof.md` | Entry point: one run from input to output, evidence, and the limitations I hit |
| `lab_langsmith_eu_ai_act.ipynb` | The full lab notebook (dataset, target, evaluators, experiment, analysis) |
| `evaluation_summary.md` | One-paragraph evaluation summary with metrics |
| `outputs/results_main.csv` | Raw experiment results (one row per example) |
| `outputs/results_analysed.csv` | Results joined with metadata, judge comments and failure types |
| `outputs/pass_rate_by_category.png` | Correctness pass rate by category |
| `outputs/screenshot_*.png` | LangSmith screenshots: dataset, experiment table, one trace |
| `.gitignore` | Keeps `.env` (API keys) out of the repo |
