"""Parse the corpus into addressable clauses.

Every clause in the corpus carries an ID (RB-3, FC-6, CT-9). Those IDs are the
join key between the source documents and the dataset: a dataset example cites
the clauses its expected answer comes from, and `build_dataset.py` refuses to emit
an example whose citation does not resolve here.

That check is the reason this module exists. A grounded-QA dataset whose ground
truth drifts away from its own source documents is worse than no dataset, because
every downstream score is then measuring the wrong thing confidently.

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import re
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"

# **RB-3 — Timing: completed applications.**
CLAUSE_RE = re.compile(r"^\*\*((?:RB|FC|CT)-\d+)\s+—\s+(.+?)\.\*\*\s*$", re.MULTILINE)


def load_clauses() -> dict[str, dict]:
    """Return {clause_id: {id, title, body, source}} for the whole corpus."""
    clauses: dict[str, dict] = {}
    for path in sorted(CORPUS_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text()
        matches = list(CLAUSE_RE.finditer(text))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[m.end():end].strip()
            cid = m.group(1)
            if cid in clauses:
                raise ValueError(f"duplicate clause id {cid} in {path.name}")
            clauses[cid] = {
                "id": cid,
                "title": m.group(2).strip(),
                "body": body,
                "source": path.name,
            }
    if not clauses:
        raise ValueError(f"no clauses parsed from {CORPUS_DIR}")
    return clauses


def corpus_as_context(clauses: dict[str, dict] | None = None) -> str:
    """The whole corpus, flattened, as the context block given to the model.

    Small enough (~1,600 words) to pass in full, which keeps the evaluation about
    grounded answering rather than about retrieval quality.
    """
    clauses = clauses or load_clauses()
    return "\n\n".join(
        f"[{c['id']}] {c['title']}\n{c['body']}" for c in clauses.values()
    )


def known_ids(clauses: dict[str, dict] | None = None) -> set[str]:
    return set((clauses or load_clauses()).keys())


if __name__ == "__main__":
    cl = load_clauses()
    by_source: dict[str, list[str]] = {}
    for c in cl.values():
        by_source.setdefault(c["source"], []).append(c["id"])
    print(f"{len(cl)} clauses parsed")
    for src, ids in by_source.items():
        print(f"  {src:38} {len(ids):>2}  {', '.join(ids)}")
    print(f"\ncontext block: {len(corpus_as_context(cl).split())} words")
