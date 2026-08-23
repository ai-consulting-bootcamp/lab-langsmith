| Metric                          | `gpt-4o-mini` |     `gpt-4.1` |
| ------------------------------- | ------------: | ------------: |
| Mean label accuracy             |         0.473 |     **0.867** |
| Fully correct / judge pass rate |           40% |       **80%** |
| Total target cost, 15 cases     |      $0.00234 |  **$0.03451** |
| Mean cost/example               |     $0.000156 | **$0.002300** |
| Cost/correct case               |     $0.000390 | **$0.002875** |
| Mean latency                    |        1.80 s |    **1.23 s** |



---

terminal output:

=== Model Summary ===
      model  mean_label_accuracy  correctness_rate  total_cost_usd  mean_cost_per_example_usd  cost_per_correct_case_usd  mean_latency_seconds
    gpt-4.1             0.866667               0.8        0.034506                   0.002300                   0.002875              1.229766
gpt-4o-mini             0.473333               0.4        0.002338                   0.000156                   0.000390              1.795181

=== Performance Difference ===
Mean label accuracy gain (gpt-4.1 - mini): +0.393
Correctness-rate gain: +40.0%
Cost multiplier: 14.8x
Mean latency difference: -0.565 seconds

=== Case-Level Wins ===
gpt-4.1 better: 7
gpt-4o-mini better: 0
Ties: 8

=== Case Comparison ===
                    case_id  gpt-4.1  gpt-4o-mini  difference_gpt4.1_minus_mini  winner
    case_01_clear_inclusion      1.0          1.0                           0.0     tie
    case_02_clear_inclusion      1.0          1.0                           0.0     tie
    case_03_clear_exclusion      1.0          0.0                           1.0 gpt-4.1
    case_04_clear_exclusion      1.0          0.0                           1.0 gpt-4.1
case_05_missing_information      1.0          0.0                           1.0 gpt-4.1
case_06_missing_information      1.0          1.0                           0.0     tie
 case_07_ambiguous_evidence      0.0          0.0                           0.0     tie
 case_08_ambiguous_evidence      1.0          1.0                           0.0     tie
  case_09_multiple_criteria      1.0          0.5                           0.5 gpt-4.1
  case_10_multiple_criteria      1.0          0.6                           0.4 gpt-4.1
 case_11_temporal_reasoning      1.0          0.0                           1.0 gpt-4.1
     case_12_boundary_value      1.0          0.0                           1.0 gpt-4.1
case_13_medical_terminology      1.0          1.0                           0.0     tie
     case_14_mixed_evidence      1.0          1.0                           0.0     tie
     case_15_not_applicable      0.0          0.0                           0.0     tie

Analysis complete.
Summary saved to: /Users/nevena/Ironhack_Labs/week7/lab-langsmith/results/optimization_summary.csv
Case comparison saved to: /Users/nevena/Ironhack_Labs/week7/lab-langsmith/results/optimization_case_comparison.csv


