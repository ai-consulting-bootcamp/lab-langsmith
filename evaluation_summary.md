# Evaluation Summary — Coaching Assistant (coach-gpt4o-mini-00928780)

We evaluated a `gpt-4o-mini`-based AI coaching assistant against a custom 15-example LangSmith
dataset (`coaching-eval-dataset`) covering single-turn and multi-turn (2-3 turn) employee-coach
exchanges across five categories (goal-setting, clarity, motivation, feedback-resistance,
perspective), using an LLM-as-judge correctness evaluator that checks whether each generated
response is a single, open-ended, advice-free reflective question. The model scored **12/15
(80%) correctness**, and all three failures occurred on multi-turn examples (turn 2 or 3 of a
thread) — none on turn-1 — indicating the model holds the "pure reflection, no advice" rule
reliably on a fresh message but drifts toward subtly solution-oriented phrasing (e.g. "ways you
could gain insight," "benefits of exploring") once it has more conversational context to react
to; two of the three failures were flagged by the judge for containing an embedded suggestion,
and one for being arguably yes/no-answerable, though that last call is debatable and may reflect
judge imprecision rather than a genuine flaw in the response. The main limitation of this
evaluation is its small size (15 examples, single model, no repeated runs to check variance) and
a judge that is itself an LLM prone to occasional misjudgment, as seen in the ambiguous
yes/no-flagged case. **Recommendation:** tighten the system prompt specifically for multi-turn
turns — e.g. explicitly reminding the model, when conversation history is present, to reflect the
employee's own words back rather than proposing directions ("ways to," "benefits of") — and
re-run the evaluation to see if the multi-turn failure rate drops.

## Metrics

| Metric | Value |
|---|---|
| Examples evaluated | 15 |
| Correctness (avg) | 0.80 |
| Passed | 12 |
| Failed | 3 |
| Turn-1 failure rate | 0/9 (0%) |
| Multi-turn (turn 2-3) failure rate | 3/6 (50%) |
| Model | gpt-4o-mini |
| Avg latency | ~0.7s |
| Cost per example | <$0.01 |

## Failure detail

| Row | Employee message | Generated response | Judge reasoning |
|---|---|---|---|
| 8 | "I guess I just assume it because they never complain." | "What might be some ways you could gain more insight into your teammates' experiences?" | Contains a suggestion, not a single open-ended question |
| 10 | "I don't know, I've always talked like this, I don't think I can change." | "What might be some benefits of exploring a different communication style?" | Contains a suggestion, not a single open-ended question |
| 15 | "I got the same feedback again this cycle and nothing's changed." | "What do you think might be holding you back from making the changes you want to see?" | Not open-ended, answerable with yes/no (debatable — reads as open-ended) |

LangSmith experiment: `coach-gpt4o-mini-00928780`
