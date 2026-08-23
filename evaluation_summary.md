# Evaluation summary

The evaluation used 15 synthetic social-impact consulting briefs across monitoring, finance, safeguarding, privacy, inclusion, governance, grant compliance, and sustainability, with three difficulty levels. The traced target returns a structured `decision`, `answer`, and `next_action`; LangSmith applies exact decision scoring, a custom consulting-quality evaluator, and an OpenEvals reference-aware semantic judge. Both prompt variants completed successfully on all 15 examples in LangSmith on 23 August 2026.

The evidence-first prompt produced the strongest grounded explanation quality: semantic correctness rose from **0.92 to 1.00** and consulting quality from **0.80 to 0.86**. The concise prompt retained the best exact decision score (**1.00 vs 0.92**) and was more efficient. The evidence-first miss therefore appears to be a routing/label-calibration issue rather than a semantic grounding issue and should be inspected at row level before production use. The dataset is synthetic and small, and the LLM judge can still encode rubric bias; human review remains necessary for high-risk consulting decisions.

| Live LangSmith variant | Examples | Consulting quality | Decision correctness | Semantic correctness | P50 latency | Total tokens | Total cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Concise | 15 | 0.80 | **1.00** | 0.92 | **0.896 s** | **3,746** | **$0.0073** |
| Evidence-first | 15 | **0.86** | 0.92 | **1.00** | 1.01 s | 4,592 | $0.0107 |

[Open the live two-experiment comparison in LangSmith](https://smith.langchain.com/o/63cd6e13-a3e6-4f18-8155-2537acb86cf8/datasets/f1c3e65b-e2af-4315-ad3b-1806c07a49a6/compare?selectedSessions=0162e5ea-6355-4711-bf7e-9237b964b076%2C1673e114-003b-4723-a298-411ddadf7d45).

The credential-free local A/B baseline remains useful for reproducibility. It produced 30 outputs: the simple keyword configuration achieved **80.0% decision accuracy (12/15)** and the risk-aware configuration achieved **100.0% (15/15)**. Its three failures were hard cases involving an incomplete theory of change, a four-of-80 feedback sample, and an unsigned international-transfer agreement.

| Local deterministic configuration | Examples | Decision accuracy | Pass rate |
| --- | ---: | ---: | ---: |
| Keyword baseline | 15 | 80.0% | 80.0% |
| Risk-aware rules | 15 | 100.0% | 100.0% |
