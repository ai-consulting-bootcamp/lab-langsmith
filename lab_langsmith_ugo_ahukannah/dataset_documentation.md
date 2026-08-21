# Dataset Documentation

**LAB | Micromanage your agents** — Steps 1, 3 and 4
**Author:** Nnanyelugo Ahukannah

## Domain and documents (Step 1)

The domain is **consumer-credit compliance question answering** for Cardinal Trust
Bank, a fictional US regional lender. The compliance team asks day-to-day
questions about adverse-action notices — deadlines, required disclosures, what
may and may not go in a decline letter — and the system must answer from the
bank's own reference material rather than from general legal knowledge, and cite
the clause it relied on so a reviewer can check it.

**Sources.** Three documents in [`corpus/`](corpus/), 27 numbered clauses in
total, authored for this exercise and modelled on the public structure of
Regulation B, FCRA §615(a) and a plausible internal policy:

| Document | Clauses | Covers |
|---|---|---|
| `reg_b_adverse_action.md` | `RB-1`…`RB-11` | Definition of adverse action, notification deadlines, content, specificity of reasons, business credit, retention |
| `fcra_615a_notices.md` | `FC-1`…`FC-7` | Consumer-report disclosures, credit-score disclosure, non-CRA third-party information |
| `cardinal_trust_credit_policy.md` | `CT-1`…`CT-9` | The seven-element template, fixed disclosure text, protected characteristics, second review, retention, turnaround target |

**What makes a good example here.** The input is a question a compliance officer
would actually ask, phrased with the specifics of a real case ("we received it on
3 March but proof of income arrived on 20 March"). The expected output is two
parts: a short answer carrying the operative number or requirement, and the list
of clause IDs it rests on. That second part is what makes the domain worth
evaluating — an answer that is right but cites nothing verifiable is not usable in
a regulated workflow, and a metric that only reads the prose cannot tell the
difference.

**The ground truth is the corpus, not the law.** A model can give a
real-world-plausible answer that contradicts the document it was handed; in a
grounded-QA system that is still a failure. This dataset therefore measures
faithfulness to the supplied source. The corpus is not legal advice and has not
been reviewed by counsel.

## LangSmith dataset (Step 4)

| | |
|---|---|
| **Name** | `cardinal-trust-adverse-action-qa` |
| **ID** | `9f32b481-0b9d-4199-8cc9-25a4bb7a35c0` |
| **Workspace region** | EU (`https://eu.api.smith.langchain.com`) |
| **Project** | `cardinal-trust-compliance-qa` |
| **Examples** | 22 |

**Description as uploaded:**

> Grounded question answering over a three-document consumer-credit compliance
> corpus (Regulation B adverse-action duties, FCRA s615 disclosures, and Cardinal
> Trust Bank's internal notice policy). Each example cites the corpus clauses its
> reference answer is drawn from, so answers can be scored for faithfulness to the
> supplied source rather than for real-world legal correctness. Corpus authored
> for training use; not legal advice.

Upload is idempotent: `run_evaluation.py` checks for the dataset by name and
reuses it, because re-creating a dataset between experiments silently makes two
experiments incomparable. `--refresh` deletes and re-uploads deliberately. The
uploader verifies the example count after writing and exits non-zero if it does
not match the local file.

## Data structure (Step 3)

Each example is built by `build_dataset.py` from `questions.json` joined against
the clauses parsed out of the corpus by `corpus_index.py`:

```json
{
  "inputs":  { "question": "…the compliance question…" },
  "outputs": { "answer": "…the reference answer…",
               "clause_ids": ["RB-3"] },
  "metadata": { "example_id": "Q01", "category": "regulation_b",
                "difficulty": "easy", "clause_ids": ["RB-3"],
                "source_docs": ["reg_b_adverse_action.md"], "n_clauses": 1 }
}
```

| Field | Purpose |
|---|---|
| `inputs.question` | What the model is asked. The only thing it receives besides the corpus. |
| `outputs.answer` | Reference answer, used by the correctness judge. |
| `outputs.clause_ids` | The clauses the reference rests on — used by the deterministic citation evaluators, and the reason those evaluators need no model. |
| `metadata.category` | `regulation_b` (9), `fcra` (5), `internal_policy` (4), `edge_case` (4) — drives the per-category analysis. |
| `metadata.difficulty` | `easy` (7), `medium` (9), `hard` (6). |
| `metadata.source_docs` | Which corpus files the answer draws on. |
| `metadata.n_clauses` | 4 examples are multi-clause, which is where partial citation shows up. |

**Coverage:** 24 of 27 clauses are exercised by at least one example (`CT-2`,
`FC-1` and `RB-6` are unused). Difficulty rises with the need to combine clauses
or to resist an intuitive but wrong answer — the `edge_case` items include a
business-credit applicant, an internal target that does not displace a regulatory
deadline, and a reason a reviewer believes but that is not in the decision record.

## Quality control

`build_dataset.py` refuses to emit a dataset that is unsound, and exits non-zero:

- every `clause_ids` entry must resolve to a clause that exists in the corpus
- example IDs must be unique, and question text must not repeat
- no required field may be empty
- at least 10 examples must survive (the lab's floor)

The validator is checked against deliberately corrupted inputs rather than
trusted: a fabricated citation, a duplicate ID, an empty answer and a duplicated
question are each caught, and each is reported against the right example. A
dataset builder that never rejects anything looks exactly like one that works.
