"""Build the evaluation dataset from the corpus and the question bank.

Step 3 of the lab. Two jobs:

1. Join `questions.json` against the clauses parsed out of `corpus/`, producing
   LangSmith-shaped examples: inputs {question}, outputs {answer, clause_ids},
   metadata {category, difficulty, source_docs, ...}.
2. Refuse to build if the join is unsound. Every cited clause must resolve, IDs
   must be unique, and no field may be empty. A dataset that quietly disagrees
   with its own source documents produces confident scores about nothing.

Run:  python build_dataset.py            # writes dataset_examples.json
      python build_dataset.py --check    # validate only, no write

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

from corpus_index import load_clauses

HERE = Path(__file__).resolve().parent
QUESTIONS = HERE / "questions.json"
OUT = HERE / "dataset_examples.json"

DATASET_NAME = "cardinal-trust-adverse-action-qa"
DATASET_DESCRIPTION = (
    "Grounded question answering over a three-document consumer-credit compliance "
    "corpus (Regulation B adverse-action duties, FCRA s615 disclosures, and Cardinal "
    "Trust Bank's internal notice policy). Each example cites the corpus clauses its "
    "reference answer is drawn from, so answers can be scored for faithfulness to the "
    "supplied source rather than for real-world legal correctness. Corpus authored for "
    "training use; not legal advice."
)


def validate(questions: list[dict], clauses: dict[str, dict]) -> list[str]:
    """Return a list of problems. Empty list means the dataset is sound."""
    problems: list[str] = []
    known = set(clauses)
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()

    for q in questions:
        qid = q.get("id", "<missing id>")

        for field in ("id", "question", "answer", "category", "difficulty", "clause_ids"):
            if not q.get(field):
                problems.append(f"{qid}: empty or missing field {field!r}")

        if qid in seen_ids:
            problems.append(f"{qid}: duplicate example id")
        seen_ids.add(qid)

        norm = " ".join(q.get("question", "").lower().split())
        if norm and norm in seen_questions:
            problems.append(f"{qid}: duplicate question text")
        seen_questions.add(norm)

        # The check this file exists for.
        for cid in q.get("clause_ids", []):
            if cid not in known:
                problems.append(f"{qid}: cites {cid}, which is not in the corpus")

    return problems


def build(questions: list[dict], clauses: dict[str, dict]) -> list[dict]:
    examples = []
    for q in questions:
        cited = [clauses[c] for c in q["clause_ids"]]
        examples.append(
            {
                "inputs": {"question": q["question"]},
                "outputs": {
                    "answer": q["answer"],
                    "clause_ids": q["clause_ids"],
                },
                "metadata": {
                    "example_id": q["id"],
                    "category": q["category"],
                    "difficulty": q["difficulty"],
                    "clause_ids": q["clause_ids"],
                    "source_docs": sorted({c["source"] for c in cited}),
                    "n_clauses": len(cited),
                },
            }
        )
    return examples


def summarise(examples: list[dict]) -> str:
    cat = collections.Counter(e["metadata"]["category"] for e in examples)
    dif = collections.Counter(e["metadata"]["difficulty"] for e in examples)
    multi = sum(1 for e in examples if e["metadata"]["n_clauses"] > 1)
    lines = [
        f"{len(examples)} examples",
        "  by category:   " + ", ".join(f"{k}={v}" for k, v in sorted(cat.items())),
        "  by difficulty: " + ", ".join(f"{k}={v}" for k, v in
                                        sorted(dif.items(), key=lambda kv: "emh".index(kv[0][0]))),
        f"  multi-clause:  {multi} examples cite more than one clause",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="validate only, do not write")
    args = ap.parse_args()

    clauses = load_clauses()
    questions = json.loads(QUESTIONS.read_text())
    print(f"corpus: {len(clauses)} clauses   question bank: {len(questions)} entries")

    problems = validate(questions, clauses)
    if problems:
        print(f"\nDATASET INVALID — {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    print("validation: every citation resolves, ids unique, no empty fields")

    if len(questions) < 10:
        print(f"\nFAIL: lab requires at least 10 examples, got {len(questions)}",
              file=sys.stderr)
        return 1

    examples = build(questions, clauses)
    print("\n" + summarise(examples))

    cited = collections.Counter(c for e in examples for c in e["metadata"]["clause_ids"])
    unused = sorted(set(clauses) - set(cited))
    print(f"  clause coverage: {len(cited)}/{len(clauses)} clauses exercised"
          + (f"; unused: {', '.join(unused)}" if unused else ""))

    if args.check:
        print("\n--check: not written")
        return 0

    OUT.write_text(json.dumps(
        {"dataset_name": DATASET_NAME,
         "description": DATASET_DESCRIPTION,
         "examples": examples}, indent=2, ensure_ascii=False))
    print(f"\nwritten: {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
