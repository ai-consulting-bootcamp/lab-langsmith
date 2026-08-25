# LangSmith Experiment Evidence

## Current status

The local dataset and evaluation pipeline are complete, but no hosted dataset ID, experiment ID, URL, screenshot, or metric is recorded because `LANGSMITH_API_KEY` and `OPENAI_API_KEY` were not available in the execution environment. No hosted result has been invented.

## Expected hosted artifacts

Running `python ticket_priority_eval.py evaluate` with valid credentials will:

1. create or reuse `ironhack-support-ticket-priority-v1`;
2. verify that it contains exactly 12 examples;
3. trace the target under `ironhack-ticket-priority-evaluation`;
4. run an experiment prefixed `ticket-priority-baseline` (or the configured override);
5. print the real LangSmith experiment link.

After the run, add the printed dataset and experiment identifiers/links here and update `evaluation_summary.md` only with the observed metrics and failures.
