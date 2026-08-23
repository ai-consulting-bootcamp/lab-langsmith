# Optimization summary

The live LangSmith comparison shows a real quality/efficiency trade-off. **Evidence-first is the recommended default for nuanced or higher-risk consulting briefs** because it achieved perfect semantic correctness (1.00) and higher consulting quality (0.86), versus 0.92 and 0.80 for concise. It used 22.6% more latency at P50 (1.01 s vs 0.896 s), 22.6% more tokens (4,592 vs 3,746), and about 46.6% more total model cost ($0.0107 vs $0.0073) across 15 cases. Concise nevertheless achieved perfect exact decision correctness (1.00), while evidence-first scored 0.92, so the evidence-first decision-label miss should be reviewed and the prompt tightened before production.

For immediate deployment, use concise for low-risk, high-volume triage and evidence-first when explanation quality and explicit evidence constraints matter more than the small absolute cost increase. Keep deterministic risk-aware routing as a zero-token guardrail for known safeguarding, privacy, and evidence-quality patterns. The next optimization cycle should (1) inspect the evidence-first label mismatch, (2) add it as a regression example, (3) tighten the decision-label instruction without weakening explanation quality, and (4) rerun the same fixed dataset.

| Configuration | Decision score | Semantic score | Tokens | Total cost | Suitable use |
| --- | ---: | ---: | ---: | ---: | --- |
| Keyword baseline | 0.80 | n/a | 0 | $0 | Smoke testing only |
| Risk-aware rules | 1.00 | n/a | 0 | $0 | Known-pattern guardrail |
| Concise LLM | **1.00** | 0.92 | **3,746** | **$0.0073** | Lower-risk, high-volume briefs |
| Evidence-first LLM | 0.92 | **1.00** | 4,592 | $0.0107 | Nuanced or higher-risk briefs |

[Open the live comparison in LangSmith](https://smith.langchain.com/o/63cd6e13-a3e6-4f18-8155-2537acb86cf8/datasets/f1c3e65b-e2af-4315-ad3b-1806c07a49a6/compare?selectedSessions=0162e5ea-6355-4711-bf7e-9237b964b076%2C1673e114-003b-4723-a298-411ddadf7d45).
