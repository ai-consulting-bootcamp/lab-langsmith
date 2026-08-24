# Step 8 — Reviewing Results in the LangSmith UI

Reviewed the `gpt-4o-mini-final-69b227b3` experiment in the LangSmith comparison view (screenshot in `screenshots/`).

**Aggregate metrics observed:**
- correctness avg: 0.62 (0.54 on the earlier baseline run)
- completeness avg: 1.00
- P50 latency: 1.12s

**Observations from clicking into individual examples:**
- All 6 failing rows (correctness = 0.00) share the same pattern: an abbreviated or typo'd school name in the raw message ("njr", "bvm", "bramharshi vidya mandr") that the model did not resolve to the canonical school name used in the reference output.
- Every failing row still scored completeness = 1.00 — the model extracted the right number of items with correct titles/quantities in every case; only the `school` field (and once, `class`, when the two got merged) was wrong.
- Passing rows were concentrated in messages that either used the full school name or came from Sai Vidyanikethan (whose name wasn't abbreviated in any test message).

**Interesting examples to investigate further:**
- Row 13 (`"njr nursery — ..."`): worth a closer look, since the model didn't just null the school field here — it merged "njr nursery" into the `school` string and left `class` null, a slightly different failure shape than the other abbreviation misses.
- Row 5 (`"bramharshi vidya mandr clas 6 — ..."`, typo'd): worth checking whether this is really the same root cause as the njr/bvm cases, or a separate typo-tolerance issue.

Full quantitative breakdown and root-cause analysis in `evaluation_summary.md`.