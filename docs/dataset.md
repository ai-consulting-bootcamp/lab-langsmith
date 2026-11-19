# Dataset

I evaluated a support assistant for CloudDesk, a fictional workspace SaaS. The task is to answer customer questions accurately using a supplied policy excerpt, including cases where the assistant must acknowledge missing information or lack of authority. The corpus contains synthetic business policies and no real customer records.

## Source documents

| Document | Scope |
|---|---|
| [Plans](../data/plans.md) | Seats, pricing, annual billing, upgrades and downgrades |
| [Billing](../data/billing.md) | Cancellation, first-charge refund conditions, invoice access |
| [Access](../data/access.md) | MFA recovery, roles, SSO prerequisites |
| [Data](../data/data.md) | Exports, deletion, residency and unspecified details |
| [API and support](../data/api_support.md) | Rate limits, archived policy, business-hour response targets |

These five versioned documents are the complete source of truth for this experiment. They describe a fictional service and are not statements about any real SaaS provider. No customer information or external benchmark questions were imported.

## Dataset specification

- Name: `clouddesk-support-v1`
- Description: 20 synthetic CloudDesk support questions across plans, billing, access, data, and API/support, including boundary cases, unanswerable questions, and unauthorized action requests.
- Categories: five, with four examples each.
- Unit of evaluation: one independent question with its complete relevant policy document.
- Task boundary: supplied-context answer generation. Retrieval, tool execution, live account lookup and multi-turn dialogue are outside scope.
- Versioning: deterministic example IDs and exact input/reference checks make repeated uploads idempotent. Changed content requires a new dataset version. LangSmith's additional `dataset_split` metadata is treated as a service-managed field.

| Field | Purpose | Visible to target? |
|---|---|---|
| `inputs.question` | Customer request | Yes |
| `inputs.context` | Complete policy document for this question | Yes |
| `outputs.answer` | Expected facts, constraints, and citations | No |
| `outputs.required_citations` | Policy identifiers required by the citation check | No |
| `metadata.case_id` | Stable case identifier S01-S20 | No |
| `metadata.category`, `difficulty` | Analysis groups | No |
| `metadata.source`, `policy_ids` | Evidence location | No |
| `metadata.reference_rationale` | Lookup, arithmetic or boundary justification | No |
| `metadata.dataset_version` | Corpus version | No |

## Quality and answer criteria

A good response answers every material part of the question, preserves conditions and units, cites the relevant policy, and does not invent facts or completed actions. Wording can vary, so free-text exact match is inappropriate. Sources are included with each question, while references and scoring metadata are withheld from the target.

All 20 cases have nonempty inputs and references, unique IDs and questions, source-identical contexts, and valid policy references. Arithmetic cases include explicit derivations: S02 is 7 x 12 = USD 84, S03 is max(3, 5) x 120 = USD 600, and S04 is max(6, 10) x 25 = USD 250. S06 and S08 test the inclusive 336-hour boundary. S19 counts one business hour on Friday and three on Monday. S15 is deliberately unanswerable. The reference rationales make the complete answer key auditable; there is no independent human annotation study or inter-annotator agreement measurement.

The balanced synthetic sample is a diagnostic set, not a representative sample of production ticket frequency. One changed outcome moves a 20-case pass rate by five percentage points. Both prompts were fixed before full evaluation; the same cases were used for the paired comparison, without a separate held-out validation set.
