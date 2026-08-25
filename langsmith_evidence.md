# LangSmith Experiment Evidence

## Hosted dataset

- **Name:** `ironhack-support-ticket-priority-v1`
- **Dataset ID:** `b8d3b2a8-e09a-430e-8bba-dec2aa346dd9`
- **Verified size:** 12 examples
- **Created:** 25 August 2026 at 09:46:27 UTC
- **Dataset link:** [Open dataset in LangSmith](https://smith.langchain.com/o/90426365-e410-4629-9c60-e0e6f05ccf5d/datasets/b8d3b2a8-e09a-430e-8bba-dec2aa346dd9)

The evaluation command called `list_examples` after creation and verified that the remote count exactly matched the 12 version-controlled examples.

## Hosted experiment

- **Name:** `ticket-priority-baseline-32443137`
- **Experiment ID:** `96da469f-89b8-4c39-b851-114b11a97813`
- **Model:** `gpt-5.6-luna`
- **Experiment link:** [Open experiment in LangSmith](https://smith.langchain.com/o/90426365-e410-4629-9c60-e0e6f05ccf5d/datasets/b8d3b2a8-e09a-430e-8bba-dec2aa346dd9/compare?selectedSessions=96da469f-89b8-4c39-b851-114b11a97813)

## Actual results

| Metric | Result |
| --- | ---: |
| Completed examples | 12 / 12 |
| Exact priority accuracy | 1.00 (12 / 12) |
| Run error rate | 0.00 |
| Median latency | 0.932345 seconds |
| p99 latency | 3.034319 seconds |
| Total tokens | 1,684 |
| Total cost | $0.0004088 |

All 12 evaluator feedback records had `priority_accuracy=1.0`. There were no failed or low-scoring cases: all four P1, four P2, and four P3 examples matched their references, including the three boundary examples. This strong result should be interpreted cautiously because the dataset is small, balanced, hand-written, and closely aligned with the system prompt; ambiguous multi-issue and noisier production-style tickets are not yet represented.
