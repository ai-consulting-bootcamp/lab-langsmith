# Optimization Summary

## Model decision

Three target models were evaluated under the **same 12-case dataset, prompt, reference outputs, evaluators, and execution settings** so that only model choice changed. **GPT-5.4 mini is the recommended default for Intellectus Operations/CX**: it delivered the highest correctness (**97.9%**) while maintaining **100% groundedness** and **100% contract compliance**, at a total target-model cost of approximately **$0.0094** for the full evaluation. **GPT-4o mini** remains a strong low-cost fallback, matching the larger model on groundedness and contract compliance while reducing total target cost to approximately **$0.0015**, making it suitable for higher-volume or lower-risk workloads. **GPT-5.4** did not improve quality on this benchmark: correctness remained at **95.8%** while cost increased to approximately **$0.0311**, so the additional spend is not justified for this capability today. The practical operating model is therefore to use GPT-5.4 mini as the standard, retain GPT-4o mini as a cost-optimised option, and only reconsider GPT-5.4 if future evaluation sets introduce materially harder reasoning tasks where it demonstrates a measurable quality gain.

## Cost / quality view

| Model | Correctness | Groundedness | Contract | Avg. latency | Target cost |
|---|---:|---:|---:|---:|---:|
| GPT-4o mini | 95.8% | 100% | 100% | 2.06 s | **$0.0015** |
| **GPT-5.4 mini** | **97.9%** | 100% | 100% | 1.89 s | **$0.0094** |
| GPT-5.4 | 95.8% | 100% | 100% | **1.82 s** | $0.0311 |

> **Decision:** choose the smallest model that preserves required quality. For the current Operations/CX workload, GPT-5.4 mini provides the strongest quality-cost balance.
