# Evaluation summary

I evaluated a **gpt-4o-mini** "EU AI Act consultant assistant" on **`eu-ai-act-consultant-qa-v1`**. The setup was temperature 0, a consultant system prompt and no retrieval. The dataset has 18 client questions built from the Ironhack W7 lesson decks: 10 categories, 6 hard questions, and 3 that depend on the July 2026 Digital Omnibus. An OpenEvals LLM-as-a-judge (`CORRECTNESS_PROMPT`, gpt-5.4-mini) passed only **3 of 18 answers (17%)**, and a rule-based key-term check passed **1 of 18 (6%)**. **The biggest failure pattern is confident answers built on the wrong version of the law.** gpt-4o-mini answers from the 2021 Commission *proposal*, not the final Act. It quotes the proposal's fines (€30M / 6% instead of €35M / 7%) and its article numbers (Art. 52 for transparency, Art. 62 for incident reporting, Art. 71 for fines). It misses all 3 Article 5 bans in the dataset, calling emotion recognition at work and social scoring "high-risk". It invents dates for the Omnibus questions; at temperature 0, the same question got "1 January 2025" in one run and "6 April 2025" in the next. Almost every answer ends with "consult a lawyer", which sounds careful but hides the errors. Limitations: 18 examples, so one example is about 5.6 points; the same configuration scored 11% to 17% across runs. There is one judge model with no human calibration; I found one judge mistake in the A/B run (see below). The ground truth is a teaching deck, not the legal text. **Recommendation:** do not use a closed-book small model for EU AI Act advice. Ground it in the final text: a six-line briefing fixed 3 of 3 Omnibus questions (see `optimization_summary.md`). Then re-test on this dataset before any client use.

| Metric | Score |
|---|---|
| Correctness (LLM judge) | 17% (3 of 18) |
| Keyword match (rule) | 6% (1 of 18) |
| Correctness on Omnibus questions vs the rest | 0% (0 of 3) vs 20% (3 of 15) |
| Advisory quality (custom judge, separate run) | 0.61 mean; correctness 11% in that run |
| Agreement between the judge and the keyword rule | 16 of 18 rows |
| Average latency | 1.40 s |

**Failure types** (15 failed answers, each tagged by hand from the judge comment):

| Type | n | Example |
|---|---|---|
| Wrong or invented fact | 4 | "Logs must be kept for a minimum of five years (Article 61)"; the right answer is at least 6 months |
| Missed Article 5 ban | 3 | Emotion recognition at work classified as "high-risk" instead of prohibited |
| Stale knowledge (Omnibus) | 3 | High-risk Annex III date given as "6 April 2025"; the right answer is 2 December 2027 |
| Incomplete | 3 | Chatbot: correctly "not high-risk", but misses the Article 50 duty to say it's an AI |
| Over-generalisation | 2 | "Both need a FRIA because they use high-risk AI"; the right answer is neither |

**Judge check:** in the main run I found no judge mistakes. In the A/B run, the judge marked gpt-5.4-mini's face-scraping answer **correct**. That answer called the practice "high-risk", but face scraping is banned under Article 5(1)(e). The keyword rule passed it too: it only checks that the words are present, not the classification. **Both evaluators are lenient when the bottom line (don't do it) is right but the legal category is wrong.**

Data: `outputs/results_main.csv`, `outputs/failures_main.csv`, `outputs/metrics_main.csv`, `outputs/pass_rate_by_category.png`.
