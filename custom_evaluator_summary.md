# Custom Evaluator Deliverable: Plausibility LLM Judge

## 1. Evaluator Design & Specification

- **Metric Measured:** Category Plausibility & Defensibility.
- **Core Rationale:** Deterministic exact-match evaluators penalize label mismatches binarily (`0` or `1`) against historical reference outputs. The `plausibility_evaluator` measures whether a predicted label is a defensible interpretation of the article content—separating acceptable taxonomy boundary calls from genuine model hallucinations.
- **Scoring Taxonomy (1–5 Scale):**
  - **5:** Clearly correct and unambiguous fit.
  - **4:** Solid, well-supported fit.
  - **3:** Defensible, but not the single best fit.
  - **2:** Weak or strained connection.
  - **1:** Complete category irrelevance.
  - **0:** Out-of-taxonomy label (short-circuited without an API call).

## 2. Local Unit Test Verification

Executing `python src/custom_evaluator.py` validated the LLM judge's standalone reasoning logic:

- **Test 1 (Clear Sports text → Predicted `Sports`):** Score **5/5**. *Reasoning:* Discusses Olympic swimming competition.
- **Test 2 (Madden NFL release → Predicted `Sports`, Reference `Sci/Tech`):** Score **5/5**. *Reasoning:* Discusses a football video game and fan impact, which strongly aligns with Sports.
- **Test 3 (Out-of-taxonomy `Politics`):** Score **0/5**. *Reasoning:* Invalid category short-circuit.

## 3. Full-Run LangSmith Analysis (`gpt-4o-mini-20260823-180009`)

Executing `run_evaluation.py` tracked both metrics side-by-side across all 16 dataset examples:

- **Aggregate Results:** `exact_match` AVG = **0.88** (87.5%), `plausibility` AVG = **4.75 / 5.0**.
- **Divergence on Hard Edge Cases:**
  - **Row 8 (Madden NFL 2005 Article):** `exact_match` = `0.00` vs. `plausibility` = `5.00`. The reference label is `Sci/Tech`, but the judge confirmed `Sports` is a 5/5 plausible read.
  - **Row 13 (AOL PC Sales Article):** `exact_match` = `0.00` vs. `plausibility` = `4.00`. The reference label is `Sci/Tech`, but the judge recognized that corporate discount pricing is a 4/5 solid fit for `Business`.

## 4. Strategic Insight

Pairing `exact_match` with `plausibility` reveals that `gpt-4o-mini` suffered zero severe hallucinations or format breakages across the entire run. The 12.5% error rate flagged by exact-match scoring consists entirely of highly defensible boundary interpretations (average plausibility of 4.5/5 on failed rows).


## 5. Full Comparison Table & Detailed Divergence Analysis (Step 12)

**Full comparison table (16/16 examples):**

| # | Reference | Predicted | exact_match | plausibility |
|---|---|---|---|---|
| 1 | Sports | Sports | 1.00 | 5.00 |
| 2 | Sci/Tech | Sci/Tech | 1.00 | 5.00 |
| 3 | Business | Business | 1.00 | 5.00 |
| 4 | Sci/Tech | Sci/Tech | 1.00 | 5.00 |
| 5 | World | World | 1.00 | 4.00 |
| 6 | Sports | Sports | 1.00 | 5.00 |
| 7 | Business | Business | 1.00 | 5.00 |
| **8** | **Sci/Tech** | **Sports** | **0.00** | **5.00** |
| 9 | Business | Business | 1.00 | 4.00 |
| 10 | World | World | 1.00 | 5.00 |
| 11 | Sports | Sports | 1.00 | 5.00 |
| 12 | Business | Business | 1.00 | 4.00 |
| **13** | **Sci/Tech** | **Business** | **0.00** | **4.00** |
| 14–16 | *(various)* | *(various)* | 1.00 each | 5.00 each |
| **Avg** | | | **0.88** | **4.75** |

**Where the two evaluators diverge:**
Exactly 2 of 16 examples — rows 8 and 13, both true Sci/Tech articles the model mislabeled — show a real split: `exact_match = 0`, `plausibility = 4–5`. Every other example agrees in direction (both high). This is the entire story of the comparison: the divergence is concentrated precisely on the same 2 examples flagged in Step 8/9's error analysis, not spread randomly across the dataset.

**What plausibility is capturing that correctness can't:**
`exact_match` only asks "did it match AG News's label?" — a binary, reference-bound question. `plausibility` asks "is this a defensible read of the article on its own terms?" — independent of any reference. The fact that both failing predictions score 4–5 on plausibility (not 1–2) tells you these are not reasoning errors or hallucinations; they're legitimate alternate categorizations that happen to disagree with one specific labeling convention from a 2004-era news dataset.

**Correlation vs. discrepancy:**
Across the other 14 examples, the two metrics move together (high correctness, high plausibility) — so they're not independent or contradictory measures in general. The discrepancy is narrow and specific: it appears only at the correctness boundary, which is exactly where a second evaluation dimension is most useful. If plausibility had also cratered on rows 8 and 13, that would suggest the model was genuinely confused; instead it suggests the dataset's category boundary is the ambiguous element, not the model's reasoning.

**Bottom-line insight:**
Correctness and plausibility agree on 14/16 examples, but diverge sharply on the 2 failures — both scoring near-maximal plausibility despite being marked wrong. This shows the model's errors stem from a genuinely ambiguous category boundary (Sci/Tech vs. Sports/Business) in the AG News taxonomy, not from flawed reasoning, and demonstrates why measuring only exact-match correctness can understate a classifier's actual judgment quality on edge cases.


## 6. Reflection on the Value of Custom Evaluation Dimensions

This exercise demonstrates a limitation of relying on a single reference-based metric for evaluation. Taken alone, `exact_match` reports a flat 12.5% failure rate with no indication of *why* those failures occurred or how severe they are — a stakeholder reading only that number might reasonably conclude the model has a meaningful classification weakness worth significant prompt-engineering investment.

Adding `plausibility` as a second, reference-free dimension changes that conclusion. Because both failing examples scored 4-5 out of 5 on plausibility, the evidence points to the errors being defensible boundary calls on a genuinely ambiguous 2004-era news taxonomy, not gaps in the model's reasoning. This reframes the finding from "the model is unreliable at classification" to "the model reasons soundly, but disagrees with one specific labeling convention on ambiguous cases" — a much more actionable and less alarming conclusion.

More generally, this suggests that any evaluation relying solely on exact-match or reference-based scoring risks conflating two very different failure types: genuine model errors versus disagreements with an imperfect or ambiguous ground truth. A second, reference-free dimension — even a simple one like plausibility — is a cheap way to distinguish between them before deciding whether a low score calls for model improvement or dataset re-examination.