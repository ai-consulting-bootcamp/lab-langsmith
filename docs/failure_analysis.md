# Failure analysis

## What failed

| Case | Configuration | Failure type | Evidence and expected result |
|---|---|---|---|
| S03 | Policy-aware | Misinterpreted condition | Treats the five-seat billing minimum as a ban on three members. The annual bill is 5 x USD 120 = USD 600. |
| S04 | Baseline | Wrong calculation / ignored condition | Bills six Business members at USD 150, ignoring the ten-seat minimum. The next bill is USD 250; removing members does not refund the current period. It also omits PLAN-01. |
| S04 | Policy-aware | Invented requirement / incomplete answer | Says a downgrade to Team is required, although the policy only specifies a billing minimum. It never gives the USD 250 bill and omits PLAN-01. |
| S07 | Both | Wrong refund eligibility | Treats a one-day-old renewal as eligible, although the window applies only to the first subscription charge. |
| S19 | Both | Business-hour arithmetic | Adds four clock hours to Friday 16:00. Only one business hour remains Friday, so three roll over to Monday: target Monday 12:00 UTC. |
| S15 | Policy-aware | Missing citation | Correctly declines to invent backup retention, but omits DATA-02. Correctness and groundedness still pass. |

The baseline has three correctness failures, all in hard cases; the policy-aware prompt has four. Access and data have 100% correctness in both configurations. API/support and billing are at 75% in both. Plans fall from 75% to 50% with the longer prompt. These category estimates each have only four cases. All easy and medium questions pass correctness in both variants, while hard-case correctness is 8/11 (72.7%) for baseline and 7/11 (63.6%) for policy-aware.

## Evaluator disagreements and reliability

The groundedness judge passes S19 for both configurations even though the proposed Friday 20:00 deadline contradicts the 17:00 close. Its comments repeat the same incorrect clock-hour calculation. This is a false positive in the custom judge, not evidence that the reference is wrong. The correctness judge rejects both answers and supplies the correct Monday deadline. The original scores remain unchanged in all exports, charts and headline metrics.

The groundedness rationale for policy-aware S04 is also flawed: it correctly rejects the invented downgrade, but incorrectly suggests USD 150 as a possible Business bill. The binary result is right for the wrong partial explanation. On S03, its rationale conflates unsupported eligibility with incompleteness despite the intended metric distinction. These cases show why a plausible explanation and a passing five-fixture calibration do not establish judge reliability.

The deterministic citation check passes wrong factual answers such as S07 because the relevant marker is present. It detects the uncited but factually correct S15 answer. This is useful complementary evidence, not an accuracy metric. Correctness and groundedness disagree on S19; correctness and citation coverage disagree on baseline S07/S19 and policy-aware S03/S07/S15/S19.

## Successful cases and scope

Both configurations compute the seven-member Team monthly charge correctly (S02), handle the inclusive refund boundary (S06), reject the 337-hour refund request (S08), and acknowledge unspecified backup retention (S15). Both distinguish MFA recovery routes and refuse to claim that they opened a ticket or verified an outage (S20). The longer prompt is not uniformly worse, but adds no correctness wins in this run.

The source policy and derivations were checked against the flagged outputs. No reference correction was identified. This is a policy-based audit of the saved outputs, not an independent blinded human evaluation. The audit is preserved in `outputs/policy_audit.csv` alongside unmodified judge scores.

## Implications

Billing minima and business-hour arithmetic are candidates for deterministic functions with explicit inputs and tested boundaries. A second dataset version would add multiple examples for seat minima, renewals, elapsed-time boundaries, weekend rollover, conflicting policy versions and unavailable facts. The judge calibration would include arithmetic and eligibility traps, and a separate held-out set plus repeated runs would assess whether changes generalize. The baseline is a reasonable supervised prototype starting point, but 85% on this small set is insufficient evidence for unattended billing or account decisions.
