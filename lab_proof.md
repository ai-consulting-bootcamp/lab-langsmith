# Lab proof: custom LangSmith evaluation for EU AI Act consulting

**Author:** Elif Yurdakul · Ironhack W7D4 · *LAB | Micromanage your agents*

## 1. Workflow (code)

| Step | Where (in [`lab_langsmith_eu_ai_act.ipynb`](lab_langsmith_eu_ai_act.ipynb)) |
|---|---|
| Dataset: 18 Q&A pairs, key terms, metadata | Step 3 · [`data/eu_ai_act_qa_dataset.json`](data/eu_ai_act_qa_dataset.json) · [`docs/dataset_documentation.md`](docs/dataset_documentation.md) |
| Upload to LangSmith (no duplicates, with metadata) | Step 4 |
| Target function (`@traceable` + `wrap_openai`, try/except) | Step 5 |
| Evaluators: `correctness` (OpenEvals), `keyword_match` (rule) | Step 6 |
| Experiment, analysis, error analysis | Steps 7–9 |
| Custom evaluator `advisory_quality` | Optional Part 1 (Steps 11–13) |
| A/B test of cost vs performance (3 configurations) | Optional Part 2 (Steps 14–16) |

```
JSON examples ──► LangSmith dataset ──► target(question) ──► answer + tokens + latency
                                              │
                    correctness judge ◄───────┤  (OpenEvals, vs reference answer)
                    keyword check ◄───────────┤  (rule, key terms)
                    advisory-quality judge ◄──┘  (custom, optional part)
                                              ▼
                        experiment in LangSmith ──► pandas analysis ──► outputs/
```

## 2. One run: input → evidence → output

**Input** (`timeline`, hard, `post_cutoff_fact = true`):
> From what date do the high-risk obligations apply to stand-alone Annex III AI systems such as
> CV-screening or credit-scoring tools?

**Reference:** 2 December 2027 (postponed from 2 August 2026 by the Digital Omnibus, Regulation (EU) 2026/1744).

**Final output** (gpt-4o-mini, main experiment `gpt-4o-mini-consultant-promptv1-1e89f2d3`):
> "The high-risk obligations for stand-alone Annex III AI systems … apply from **1 January 2025**.
> This is outlined in **Article 69** of the EU AI Act … please consult a legal expert …"

**Evidence:**

| Evaluator | Score | Reasoning (shortened) |
|---|---|---|
| `correctness` (judge) | **False** | "Factually incorrect … according to the reference, they apply from 2 December 2027 after postponement from the original 2 August 2026 date." |
| `keyword_match` (rule) | **False** | `missing: ['2 december 2027']` |
| `advisory_quality` (custom, separate run) | **0.25** | Lowest score in the run. It states a wrong date as settled fact, then adds a generic "consult a legal expert". |

The same question across the A/B configurations: the Omnibus questions scored **0 of 3** with gpt-4o-mini, **0 of 3** with gpt-5.4-mini, and **3 of 3** with gpt-4o-mini plus the regulatory briefing.

Screenshots: `outputs/screenshot_dataset.png`, `outputs/screenshot_experiment.png`, `outputs/screenshot_trace.png`.
Data: [`outputs/results_main.csv`](outputs/results_main.csv) · [`outputs/failures_main.csv`](outputs/failures_main.csv).
Results: [`evaluation_summary.md`](evaluation_summary.md) · [`optimization_summary.md`](optimization_summary.md).

**Headline numbers:**
- Main run: correctness **11%**, keyword match **6%**.
- Advisory quality: **0.60**.
- A/B pass rates:
  - gpt-4o-mini: **17%**
  - gpt-5.4-mini: **50%**
  - gpt-4o-mini + briefing: **28%**

## 3. Failure / limitation I hit

**The model answers from a draft of the law, and the "consult a lawyer" disclaimer hides it.**
gpt-4o-mini quoted the 2021 Commission *proposal*:
- its fines (€30M / 6% instead of €35M / 7%)
- its article numbers (Art. 52, 62, 71 instead of 50, 73, 99)

It treated 3 of 3 banned practices as merely "high-risk" or "not covered". Every one of these answers ended with "consult a lawyer", so they read as careful while giving a client the wrong legal picture. Correctness and the keyword check catch the wrong facts. Only the custom advisory judge shows the second problem: a disclaimer is not the same as good escalation.

**Technical limitations I hit along the way:**
- **Run-to-run noise.** The same configuration scored 11% in the main run and 17% in the A/B run. With 18 examples, one answer moves the score by about 5.6 points.
- **Packages in the wrong Python.** `pip` in Terminal installed into a different Python than the notebook kernel. I fixed it with `%pip` inside the notebook.
- **Bad API key.** A pasted LangSmith key with an extra character returned **403 Forbidden**. The error looked like a region problem, but the key was the cause.


![alt text](image-5.png)

![alt text](image-6.png)

![alt text](image-7.png)