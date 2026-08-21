# Corpus

Three source documents. Every expected answer in the dataset is grounded in a
clause here, and `build_dataset.py` refuses to emit an example whose cited clause
does not exist.

| File | Clause prefix | What it covers |
|---|---|---|
| `reg_b_adverse_action.md` | `RB-` | ECOA / Regulation B notification duties |
| `fcra_615a_notices.md` | `FC-` | FCRA §615 adverse-action disclosures |
| `cardinal_trust_credit_policy.md` | `CT-` | The bank's own internal policy |

**These documents are the ground truth for this evaluation.** They are modelled on
the public structure of Regulation B and the FCRA, and on a plausible internal
policy, but they were authored for this exercise and are not legal advice. The
evaluation therefore measures *faithfulness to the supplied corpus*, not
real-world legal correctness — a distinction that matters, because a model can
give a real-world-plausible answer that contradicts the document it was given, and
in a grounded-QA system that is still a failure.
