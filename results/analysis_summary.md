# Evaluation Analysis

The baseline model achieved a mean criterion-level label accuracy of 0.473, with fully correct labels on 6 of 15 examples. Performance was strongest for clear inclusion criteria and weakest for exclusion, temporal, boundary-value, and not-applicable cases. Error analysis revealed a pronounced tendency to over-predict NOT MET, particularly for exclusion criteria where the model appeared to interpret the literal criterion rather than the project-specific eligibility-label semantics. Missing-information cases also showed occasional over-inference. Because several categories contain only one or two examples, category and difficulty results should be treated as exploratory rather than generalizable.

## Aggregate Metrics

- Mean label accuracy: **0.473**
- Median label accuracy: **0.500**
- Perfect-label cases: **6/15 (40.0%)**
- LLM-judge correctness pass rate: **6/15 (40.0%)**
- Label accuracy range: **0.0–1.0**

## Performance by Category

| category            |   examples |   mean_label_accuracy |   correctness_rate |
|:--------------------|-----------:|----------------------:|-------------------:|
| clear_inclusion     |          2 |                  1    |                1   |
| medical_terminology |          1 |                  1    |                1   |
| mixed_evidence      |          1 |                  1    |                1   |
| multiple_criteria   |          2 |                  0.55 |                0   |
| ambiguous_evidence  |          2 |                  0.5  |                0.5 |
| missing_information |          2 |                  0.5  |                0.5 |
| boundary_value      |          1 |                  0    |                0   |
| clear_exclusion     |          2 |                  0    |                0   |
| not_applicable      |          1 |                  0    |                0   |
| temporal_reasoning  |          1 |                  0    |                0   |

## Performance by Difficulty

| difficulty   |   examples |   mean_label_accuracy |   correctness_rate |
|:-------------|-----------:|----------------------:|-------------------:|
| easy         |          4 |                   0.5 |                0.5 |
| hard         |          6 |                   0.6 |                0.5 |
| medium       |          5 |                   0.3 |                0.2 |

## Label Confusions

| expected_label   | predicted_label   |   count |
|:-----------------|:------------------|--------:|
| MET              | NOT MET           |       5 |
| UNKNOWN          | NOT MET           |       3 |
| NOT APPLICABLE   | NOT MET           |       1 |
| UNKNOWN          | MET               |       1 |
| UNKNOWN          | NOT APPLICABLE    |       1 |

## Error Analysis

- Cases with at least one evaluation failure: **9/15**.
- Cases with perfect labels but failed LLM-judge correctness: **0**.
- Detailed evaluator comments are stored in `failures.csv` for qualitative review.
