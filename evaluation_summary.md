# Evaluation summary

I evaluated a **gpt-4o-mini** "EU AI Act consultant assistant" (temperature 0, consultant system prompt,
closed-book) on **eu-ai-act-consultant-qa-v1**: 18 client questions built from the Ironhack W7 lesson decks,
covering 10 categories, with 6 hard examples and 3 that depend on the
July 2026 Digital Omnibus. An OpenEvals LLM-as-a-judge (`CORRECTNESS_PROMPT`, gpt-5.4-mini) passed
**11%** of answers, and a rule-based key-term check passed **11%**. Accuracy was **0%** on
Omnibus-dependent questions against **13%** on the rest; the weakest category was **consultant_role**.
Biggest failure pattern: [fill after error analysis]. Limitations: 18 examples (one example is about
5.6 points), a single judge model with no human calibration, and ground truth from a teaching deck rather
than the legal text. Recommendation: [fill].

| Metric | Score |
|---|---|
| Correctness (LLM judge) | 11% |
| Keyword match (rule) | 11% |
| Correctness, Omnibus questions / others | 0% / 13% |
| Avg latency | 1.78s |

LangSmith experiment: [link]
