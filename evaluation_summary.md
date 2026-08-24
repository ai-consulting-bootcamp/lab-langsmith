# Evaluation Summary

We evaluated gpt-4o-mini's ability to extract structured school book orders (school, class, title, qty) from 13 raw WhatsApp-style order messages, using a custom LangSmith dataset built from real school book-order and catalogue data (Sai Vidyanikethan, NJR EM School, Bramharshi Vidya Mandir). Correctness was judged with an LLM-as-judge evaluator (semantic match against reference, ignoring formatting differences like capitalization); the model scored **0.54 average correctness (7/13 passed)**. Every one of the 6 failures traced back to a single root cause: the model could not resolve informal or abbreviated school names ("njr", "bvm", typo'd variants) to their canonical form, either nulling the school field or, in one case, merging the abbreviation into an adjacent field — it was **not** a general extraction weakness, since all failures still extracted the correct items, classes, and quantities. The main limitation of this evaluation is its small size (13 examples, single model, mixed real/synthetic quantities) and some run-to-run score variance (0.54–0.62 across repeated runs of the same model at temperature 0), so exact percentages should be read directionally rather than precisely. **Recommendation:** add a lightweight school-name normalization step (a known-abbreviations lookup or fuzzy match against the catalogue's school list) either in the prompt or as a post-processing step before the extraction result is used, rather than trying to solve this with a stronger/more expensive model.

**Metrics**
| Metric | Value |
|---|---|
| Examples | 13 |
| Passed / Failed | 7 / 6 |
| Avg correctness | 0.54 |
| P50 latency | 1.28s |
| Total cost (13 examples) | <$0.01 |
| Pass rate — real-quantity examples (Sai Vidyanikethan) | 4/4 (100%) |
| Pass rate — synthetic-quantity examples | 3/9 |

**Failure pattern**
| Row | Message (excerpt) | Cause |
|---|---|---|
| 1 | "bvm class 9 — ..." | "bvm" not resolved to Bramharshi Vidya Mandir |
| 2 | "njr class 1 — ..." | "njr" not resolved to NJR EM School |
| 4 | "njr class 6 — ..." | "njr" not resolved to NJR EM School |
| 9 | "class 10 njr - ..." | "njr" not resolved to NJR EM School |
| 13 | "njr nursery — ..." | "njr nursery" merged into school field; class left null |
| 5 | "bramharshi vidya mandr clas 6 — ..." | typo'd/informal school name not normalized |

Custom evaluator (completeness — item-level coverage, ignoring field accuracy) scored **1.00 average across all 13 examples**, including all 6 correctness failures. This confirms the model never drops or hallucinates items; 100% of observed errors are attribute-normalization failures, 0% are coverage failures.

**Evaluator methodology note**

Both the correctness and completeness judges were updated to receive the original raw order message as context, alongside the reference and extracted outputs, so the judge can resolve ambiguous cases (e.g. abbreviations, informal phrasing) against the actual source text rather than the reference/output pair alone. The completeness evaluator was also hardened: it now validates that the judge response contains `total_reference_items`, `missing_count`, and `extra_count` before scoring, and explicitly distinguishes a genuine 0.0 (nothing covered) from a malformed/unparseable judge response — the latter is flagged via a `judge_parse_failed` metadata field instead of being silently scored as a real 0. These are robustness/methodology improvements to the judge itself; they did not change the underlying extraction failures described above.
