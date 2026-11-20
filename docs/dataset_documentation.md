# Dataset documentation: `eu-ai-act-consultant-qa-v1`

## Domain

EU AI Act advisory Q&A for AI consultants. Each example is a question that a client might
ask an external AI consultant, often as a short business scenario. The assistant has to
reach the right legal conclusion and state the facts that drive it, while staying in the
consultant's lane. It must not confirm compliance; only a lawyer can do that. Errors in this
domain carry real cost, such as a banned use that nobody stopped or a project planned
against an outdated deadline.

## Sources

| Source | Used for |
|---|---|
| Ironhack W7 Lesson 1: *Compliance, Legal, and the AI Consultant* (33 slides) | Risk levels, banned list, provider/deployer, log retention, consultant vs lawyer |
| Ironhack W7 Lesson 2: *EU AI Act for Consultants* (54 slides) | Article 5 details, Annex I/III, narrow-task exception, duties, FRIA, GPAI, Article 50, fines, timeline |
| Regulation (EU) 2026/1744 (Digital Omnibus), checked against White & Case, Orrick and CMS summaries (Jul 2026) | Confirms the post-Omnibus dates used in the 3 `post_cutoff_fact` examples |

## Data structure

Stored flat in the JSON file; the notebook splits each record into LangSmith inputs / outputs / metadata:

```json
{
  "question": "client question or scenario",                       // -> inputs
  "answer": "reference answer: conclusion first, then key facts",  // -> outputs
  "must_include": [["2 december 2027", "december 2, 2027"]],       // -> outputs (rule evaluator)
  "category": "timeline", "difficulty": "hard",                    // -> metadata
  "source": "Lesson 2 slide 27", "post_cutoff_fact": true          // -> metadata
}
```

| Field | Meaning |
|---|---|
| `question` (inputs) | What the target function receives. One question per example; the examples are independent of each other. |
| `answer` (outputs) | Ground truth for the correctness judge. It holds the conclusion (risk level, yes/no, role, date) and the facts that must not be contradicted. |
| `must_include` (outputs) | Groups of key terms for the rule-based evaluator; each group lists accepted spellings and all groups must appear. |
| `category` (metadata) | Topic. Used for per-category analysis. |
| `difficulty` (metadata) | **easy**: a single well-known rule. **medium**: a rule with a condition. **hard**: a trap from the lesson or a post-2025 date. |
| `source` (metadata) | Slide(s) the reference answer comes from, for traceability. |
| `post_cutoff_fact` (metadata) | `true` if the right answer depends on the July 2026 Omnibus. It isolates failures caused by stale training data. |

## Composition (18 examples)

| Category | n | Category | n |
|---|---|---|---|
| prohibited_practices | 3 | transparency | 2 |
| timeline (all post-cutoff) | 3 | fria | 1 |
| high_risk_duties | 3 | gpai | 1 |
| risk_classification | 2 | fines | 1 |
| roles | 1 | consultant_role | 1 |

Difficulty: 4 easy · 8 medium · 6 hard.

## Known limitations

- The ground truth is one instructor's slide deck, simplified for teaching, not the legal text.
  Some answers ("at least 6 months" of logs) are themselves simplifications.
- 18 examples give a coarse signal. One example is worth about 5.6 percentage points.
- The timeline answers are true as of November 2026 and will go stale as the Act changes.
