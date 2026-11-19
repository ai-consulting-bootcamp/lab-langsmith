# Evaluation design

## Target and controlled comparison

The target accepts `question` and `context` and returns an answer with provider model ID, token counts, elapsed time, finish reason, estimated token cost, and an error field. `@traceable` records the target span, and `wrap_openai` records model calls beneath it. Both configurations use `gpt-4o-mini`, temperature 0, a 350-token completion limit, and at most two concurrent evaluation cases. Temperature 0 reduces sampling variation but does not guarantee identical responses.

The baseline asks for concise, cited answers from the supplied context. The policy-aware configuration adds explicit checks for conditions, boundaries, archived policies, unknown facts, unavailable actions and secret handling. Only the system prompt changes. This is a paired offline prompt comparison, not a randomized production A/B test or a comparison of different target models. The exact prompts, package versions and requested settings are retained in each run manifest; each result also records the provider's resolved model name.

## Metrics

| Metric | Method | Pass criterion | Limitation |
|---|---|---|---|
| Correctness | OpenEvals `CORRECTNESS_PROMPT`, judged by `gpt-5.4-mini` | Semantically correct answer against the reference | LLM judgments can be inconsistent or too lenient about omissions |
| Citation coverage | Deterministic set inclusion | All required `[POLICY-ID]` markers appear and the target did not fail | A wrong answer can cite the right ID; this does not establish entailment |
| Groundedness | Custom OpenEvals Boolean judge | All factual claims and action claims stay within current policy and available capabilities | Can pass a true but incomplete answer; model-based judgment is imperfect |

The custom groundedness prompt separates task, supplied data, scoring criteria and a short evidence-based justification. It rejects invented facts and fabricated actions, but leaves completeness to correctness and citation syntax to the rule evaluator. A stronger, distinct model judges both target configurations; using the same provider still leaves correlated model-family biases. Judge calls use reasoning effort `none` and a 700-token output ceiling. Only the candidate answer is passed as judge output, so model names, latency and configuration labels do not influence grading.

## Calibration and error accounting

Five policy-derived fixtures cover a correct answer, wrong limits, an incomplete answer, a missing citation, and a fabricated completed action. They expose intended metric differences and retain expected labels, observed scores and judge comments. These fixtures are synthetic unit checks, not independent human ground truth. Disagreements are retained in the exported calibration record.

Target failures return an empty answer and the exception class, receive failing scores, and remain in the denominator. Truncation is also marked as a target failure. Evaluator failures are not silently dropped: a missing or non-Boolean score fails export validation. Results show coverage and errors separately. Smoke tests exercise three examples per target before the full experiments.

## Cost and timing

Token costs use successful API response usage, including cached input when reported. Prices are USD per million tokens, checked on 2026-11-19: GPT-4o mini input 0.15, cached input 0.075, output 0.60; GPT-5.4 mini input 0.75, cached input 0.075, output 4.50. Sources: [GPT-4o mini](https://developers.openai.com/api/docs/models/gpt-4o-mini) and [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini).

Comparison tables report target inference costs only. The API usage ledger separately records judge calls and target smoke checks, allowing the full successful-call suite cost to be calculated. Estimates exclude taxes, LangSmith charges, and provider charges for failed attempts without a returned usage record; they are not invoice totals. EU LangSmith storage does not imply OpenAI regional processing. Per-case latency is wall-clock time around the target API call, including any SDK retry delay, and excludes judge time. Sequential configuration runs are susceptible to time-of-run service load.
