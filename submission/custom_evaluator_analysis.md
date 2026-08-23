# Custom Evaluator: Format & Type Compliance

## What it measures
Whether the target function's output honors correct data types and honest
missing-data signaling, independent of whether the extracted value is
semantically correct. Checks: vendor_name is a string, award_amount is
numeric or None, award_id is a string or None, no currency symbols leaked
into the amount field, and -- the most consequential check -- whether
missing reference data (None) is honestly reported as None rather than
backfilled with a placeholder (0, empty string).

## Why it's a different dimension than correctness
On the edge-case dataset, the multi-vendor notice scored 0.6667 on
correctness (vendor_name wrong, since the model concatenated both vendors)
but a full 1.00 on format compliance (still a well-typed, valid string) --
proving the two evaluators catch different failure classes. Conversely, the
missing-data notice scored 0.6667 on correctness but only 0.80 on format
compliance, because the model returned 0 and "" instead of null for
genuinely absent fields -- a failure correctness alone tags simply as
"wrong," while format-compliance specifically identifies it as "silently
dishonest," which is the more actionable framing for a production system
deciding whether it can trust a null-shaped signal from this model.

## Results (edge-case dataset, 5 examples)
| Case | Correctness | Format Compliance | Note |
|---|---|---|---|
| Missing amount + ID | 0.6667 | 0.80 | Model returned 0/"" instead of null |
| Multi-vendor | 0.6667 | 1.00 | Model concatenated both vendors into one string |
| Abbreviated currency ($2.3M) | 1.00 | 1.00 | Correctly expanded |
| Multiple dollar figures | 1.00 | 1.00 | Correctly picked base value |
| Contract modification | 1.00 | 1.00 | Correctly resolved to original vendor/ID |

Average correctness: 0.87. Average format compliance: 0.96.

## Implementation Bug Caught Mid-Development
The first version of `correctness_evaluator` called `.strip()` directly on
`reference.get("field", "")` -- which only supplies the "" default when the
key is missing entirely. Since the edge-case dataset has these keys present
with an explicit `None` value (representing genuinely absent data), `.get()`
returned `None`, and `.strip()` on `None` raised an `AttributeError`,
crashing the evaluator on exactly the cases it was built to test. Fixed
with a `normalize()` helper that treats `None` as empty string before
calling `.strip()`, and an explicit branch for the amount comparison so
that a `None` reference requires a `None` prediction to count as correct,
rather than being silently coerced into a numeric comparison. This mirrors
a finding from the LLM-as-judge lab: an evaluator's logic needs to be
tested against the edge of its own dataset, not just the happy path.
