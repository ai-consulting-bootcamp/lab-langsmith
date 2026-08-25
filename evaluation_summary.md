# Evaluation Summary

## Executive readout

The Intellectus Operations/CX evaluator was tested against a **12-case custom LangSmith dataset** designed around the behavioural rules of Workflow 53, including strict domain filtering, evidence-ID integrity, uncertainty handling, contradiction management, validation requirements, and rejection of unsupported internal-process claims. Using **GPT-5.4 mini** as the target model, the evaluation achieved **97.9% correctness**, **100% groundedness**, and **100% contract compliance** across all cases. The strongest result was not simply the aggregate score, but the model’s ability to remain evidence-bound: even in the hardest case, where the reference expected rejection of an unsupported claim about automatic volunteer assignment, the model did not hallucinate or break the workflow contract; the deviation was one of response calibration and over-elaboration rather than factual grounding. This makes the current setup suitable as a regression baseline for future prompt, workflow, or model changes. The next practical improvement is to tighten handling of unsupported internal-process claims so the target returns the minimum defensible finding instead of adding unnecessary `unknown` findings, while keeping the existing groundedness and contract safeguards unchanged.

## Evaluation design

| Layer | Purpose |
|---|---|
| **Correctness** | Measures semantic alignment with the expected reference behaviour. |
| **Groundedness** | Checks that findings remain supported by the supplied Operations/CX evidence. |
| **Contract compliance** | Enforces deterministic rules such as valid evidence IDs, domain boundaries, and validation requirements. |

> **Key interpretation:** the main observed failure pattern was calibration, not hallucination. The model remained grounded and contract-compliant even when it did not match the reference answer perfectly.

## Current baseline

| Metric | Result |
|---|---:|
| Dataset size | 12 cases |
| Target model | GPT-5.4 mini |
| Correctness | **97.9%** |
| Groundedness | **100%** |
| Contract compliance | **100%** |
