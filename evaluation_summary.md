# Evaluation Summary

I evaluated gpt-4o-mini as a retail customer support chatbot against an 18-example LangSmith dataset (`retail-chatbot-support-eval`) spanning 5 failure modes (policy accuracy, honesty about missing data, tone, hallucination, safety/policy bypass), scored with a custom LLM-as-judge correctness evaluator (also gpt-4o-mini) that compares each response against a written expected-behavior reference rather than an exact match. Overall correctness was 16/18 (89%). The model was perfect on hallucination, honesty about missing data, and safety/policy-bypass attempts (all 3/3 or 4/4), but weaker on policy accuracy and tone (3/4 each, 75%). By difficulty, easy and hard cases both scored 100%, while medium cases scored 80%, a mildly surprising pattern worth noting rather than assuming difficulty always predicts failure. The 2 failures were not hallucination or rudeness: one case acknowledged a damaged delivery but suggested investigating instead of offering a direct refund or replacement, and the other incorrectly assumed a packaging requirement did not apply instead of flagging the uncertainty. Limitations: only 18 hand-written examples and a single run, the judge is itself an LLM sharing the target model's blind spots, and using gpt-4o-mini for both generation and judging risks self-consistency bias. Recommendation: tighten the system prompt's language around concrete resolution offers for property-damage complaints and packaging-requirement edge cases, the two categories that underperformed, before expanding the dataset further.

| Category | Score |
|---|---|
| hallucination | 3/3 (100%) |
| honesty_missing_data | 4/4 (100%) |
| safety | 3/3 (100%) |
| policy_accuracy | 3/4 (75%) |
| tone | 3/4 (75%) |

| Difficulty | Score |
|---|---|
| easy | 3/3 (100%) |
| hard | 5/5 (100%) |
| medium | 8/10 (80%) |

## Optional: custom evaluator (tone)

I built a second evaluator, `tone_evaluator`, that scores empathy and warmth on a 1-5 scale, independent of whether the response was procedurally correct. It uses the same judge anatomy as `correctness_evaluator` (task description, criteria, output format) but with explicit score anchors (1 = dismissive/robotic, 3 = polite but generic, 5 = warm and specific), since the reflection in `lab-llm-judges` flagged undefined score scales as a calibration risk. A quick sanity check confirmed it works as intended: a warm, specific response scored 5, and a curt one-line response to the same situation scored 1.

Running both evaluators together on all 18 examples, average tone was 2.78/5, well below the 89% correctness rate. There were 0 "wrong but warm" cases, but 7 "correct but cold" cases (tone score of 2), clustered almost entirely in `hallucination`, `honesty_missing_data`, and `safety`, the categories where the right behavior is to refuse or redirect rather than help directly. This shows something correctness alone could not: the chatbot is factually and procedurally sound in these categories, but its refusals and redirects read as robotic rather than empathetic, a real customer-experience risk that a correctness-only evaluation would completely miss.
