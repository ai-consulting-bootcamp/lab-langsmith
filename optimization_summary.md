# Optimization summary

I compared three configurations on the same 18 questions with the same evaluators (gpt-4o-mini; gpt-5.4-mini;
gpt-4o-mini plus a six-line regulatory briefing on the July 2026 Digital Omnibus). The highest pass rate was
**config-b-gpt-5.4-mini** (56% at $0.812 per 1,000 questions).
[fill: best trade-off and when to pick each config. Remember: a gap of 1-2 examples (about 6-11 points) may be luck.]

| Config | Model | Pass rate | Pass rate (Omnibus Qs) | Cost / correct answer | Cost / 1k questions | Avg latency |
|---|---|---|---|---|---|---|
| config-a-gpt-4o-mini | gpt-4o-mini | 17% | 0% | $0.00044 | $0.074 | 1.71s |
| config-b-gpt-5.4-mini | gpt-5.4-mini | 56% | 0% | $0.00146 | $0.812 | 1.99s |
| config-c-gpt-4o-mini-briefing | gpt-4o-mini | 28% | 100% | $0.00036 | $0.101 | 1.54s |

Prices: gpt-4o-mini $0.15/$0.60, gpt-5.4-mini $0.75/$4.50 per 1M input/output tokens (OpenAI pricing, checked 20 Nov 2026).
Costs cover the model under test only; judge calls cost the same for every config.
