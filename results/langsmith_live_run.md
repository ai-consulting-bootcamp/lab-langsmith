# LangSmith live-run evidence

- Run date: 2026-08-23
- Dataset: `paola-social-impact-consulting-eval-v1`
- Examples: 15 per experiment
- GitHub Actions result: success in 54 seconds
- Model: `gpt-5.4-mini`

| Variant | Experiment | Consulting quality | Decision correctness | Semantic correctness | P50 latency | Tokens | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Concise | `concise-gpt-5.4-mini-3a90cba0` | 0.80 | 1.00 | 0.92 | 0.896 s | 3,746 | $0.0073 |
| Evidence-first | `evidence_first-gpt-5.4-mini-036a2b3d` | 0.86 | 0.92 | 1.00 | 1.01 s | 4,592 | $0.0107 |

Evidence links:

- [Two-experiment comparison](https://smith.langchain.com/o/63cd6e13-a3e6-4f18-8155-2537acb86cf8/datasets/f1c3e65b-e2af-4315-ad3b-1806c07a49a6/compare?selectedSessions=0162e5ea-6355-4711-bf7e-9237b964b076%2C1673e114-003b-4723-a298-411ddadf7d45)
- [Concise experiment](https://smith.langchain.com/o/63cd6e13-a3e6-4f18-8155-2537acb86cf8/datasets/f1c3e65b-e2af-4315-ad3b-1806c07a49a6/compare?selectedSessions=0162e5ea-6355-4711-bf7e-9237b964b076)
- [Evidence-first experiment](https://smith.langchain.com/o/63cd6e13-a3e6-4f18-8155-2537acb86cf8/datasets/f1c3e65b-e2af-4315-ad3b-1806c07a49a6/compare?selectedSessions=1673e114-003b-4723-a298-411ddadf7d45)
- [Successful workflow run](https://github.com/paolahsp/lab-langsmith-social-impact/actions/runs/32667348222)
