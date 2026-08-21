"""Evaluators — one built-in, two custom.

Step 6 (correctness) and Optional Part 1 (custom dimensions).

  correctness        openevals LLM-as-judge against the reference answer
  citation_validity  DETERMINISTIC - do the cited clause IDs exist, and do they
                     match the clauses the reference answer was drawn from?
  groundedness       custom LLM-as-judge - is every claim in the answer actually
                     supported by the text of the clauses it cites?

Why three. Correctness alone cannot tell a right answer from a right answer
reached by luck, and it says nothing about whether the model invented a citation.
`citation_validity` needs no model at all, so it is the one number in this lab
that cannot itself be wrong about the corpus. `groundedness` catches the case
`citation_validity` cannot see: a real clause cited in support of a claim it does
not actually make.

All three use the LangSmith evaluator signature
(inputs, outputs, reference_outputs) and return a dict with `key`, `score` and
`comment`.

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

from corpus_index import load_clauses

HERE = Path(__file__).resolve().parent
load_dotenv(Path.home() / ".config/ironhack/.env.local")
load_dotenv(HERE / ".env", override=True)

JUDGE_MODEL = "openai:gpt-4o-mini"
CLAUSES = load_clauses()
KNOWN_IDS = set(CLAUSES)


# --------------------------------------------------------------------------
# 1. Correctness — the built-in openevals judge (Step 6)
# --------------------------------------------------------------------------

_correctness_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    feedback_key="correctness",
    model=JUDGE_MODEL,
)


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Does the answer match the reference answer? openevals' stock prompt."""
    result = _correctness_judge(
        inputs=inputs.get("question", ""),
        outputs=outputs.get("answer", ""),
        reference_outputs=reference_outputs.get("answer", ""),
    )
    return {
        "key": "correctness",
        "score": bool(result.get("score")),
        "comment": result.get("comment", ""),
    }


# --------------------------------------------------------------------------
# 2. Citation evaluators — deterministic, no model (custom)
# --------------------------------------------------------------------------
#
# The first version of this collapsed "invented a clause" and "wrote the clause
# reference badly" into one metric called citation_hallucination. On the terse
# prompt it reported 77% hallucination, which was wrong and would have been the
# headline finding. The model had cited "6" instead of "FC-6": it found the right
# clause and dropped the prefix. Nothing was invented — 0 of 31 citations across
# that experiment failed to correspond to a real clause.
#
# Those two failures need different fixes (a format instruction vs. not trusting
# the model), so they are now measured separately.

# Bare-number citations like "6" are ambiguous: RB-6, FC-6 and CT-6 all exist.
_BY_SUFFIX: dict[str, list[str]] = {}
for _cid in KNOWN_IDS:
    _BY_SUFFIX.setdefault(_cid.split("-")[1], []).append(_cid)


def _resolve(raw: str) -> tuple[str | None, str]:
    """Map a cited string to a clause id. Returns (clause_id_or_None, status).

    status is one of: exact, normalised, ambiguous, fabricated.
    """
    c = str(raw).strip().upper().replace(" ", "").replace("_", "-")
    if c in KNOWN_IDS:
        return c, "exact"
    if c.replace("-", "") in {k.replace("-", "") for k in KNOWN_IDS}:
        hit = next(k for k in KNOWN_IDS if k.replace("-", "") == c.replace("-", ""))
        return hit, "normalised"
    digits = c.lstrip("RBFCT-")
    if digits.isdigit() and digits in _BY_SUFFIX:
        opts = _BY_SUFFIX[digits]
        return (opts[0], "normalised") if len(opts) == 1 else (None, "ambiguous")
    return None, "fabricated"


def _classify(outputs: dict) -> dict:
    cited = [c for c in (outputs.get("clause_ids") or []) if str(c).strip()]
    out = {"exact": [], "normalised": [], "ambiguous": [], "fabricated": [], "resolved": []}
    for c in cited:
        cid, status = _resolve(c)
        out[status].append(str(c))
        if cid:
            out["resolved"].append(cid)
    out["n_cited"] = len(cited)
    return out


def citation_fabricated_free(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Did the model invent a clause reference that corresponds to nothing?

    The serious failure: a fabricated authority. Scored alone so that a format
    problem elsewhere cannot dilute or disguise it.
    """
    c = _classify(outputs)
    bad = c["fabricated"]
    return {
        "key": "citation_fabricated_free",
        "score": 0.0 if bad else 1.0,
        "comment": (f"fabricated references: {bad}" if bad
                    else f"no fabricated references ({c['n_cited']} cited)"),
    }


def citation_wellformed(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Is every citation written so a human could actually look it up?

    A citation of "6" is not verifiable — RB-6, FC-6 and CT-6 all exist. The model
    may well have meant the right one, but an auditor cannot tell, and an
    unverifiable citation in a compliance answer is worth nothing.
    """
    c = _classify(outputs)
    if not c["n_cited"]:
        return {"key": "citation_wellformed", "score": 0.0, "comment": "no citations given"}
    broken = c["ambiguous"] + c["fabricated"]
    bits = []
    if c["ambiguous"]:
        bits.append(f"ambiguous {c['ambiguous']}")
    if c["fabricated"]:
        bits.append(f"fabricated {c['fabricated']}")
    if c["normalised"]:
        bits.append(f"recoverable-but-malformed {c['normalised']}")
    return {
        "key": "citation_wellformed",
        "score": 0.0 if broken else 1.0,
        "comment": "; ".join(bits) or f"all {c['n_cited']} citations exactly formed",
    }


def citation_validity(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Did the model point at the right clauses?

    Judged on RESOLVED ids, so a prefix-less citation is not punished twice —
    citation_wellformed already covers the format. Extra valid clauses are
    tolerated: over-citing is untidy, not dangerous. Missing one the reference
    answer rests on is not.
    """
    c = _classify(outputs)
    expected = set(reference_outputs.get("clause_ids") or [])
    if not c["n_cited"]:
        return {"key": "citation_validity", "score": 0.0, "comment": "no clauses cited at all"}

    missing = sorted(expected - set(c["resolved"]))
    extra = sorted(set(c["resolved"]) - expected)
    unresolved = c["ambiguous"] + c["fabricated"]

    score = 1.0 if (not missing and not unresolved) else 0.0
    bits = []
    if missing:
        bits.append(f"missing {missing}")
    if unresolved:
        bits.append(f"unresolved {unresolved}")
    if extra:
        bits.append(f"extra (valid) {extra}")
    return {"key": "citation_validity", "score": score,
            "comment": "; ".join(bits) or f"resolved exactly to {sorted(expected)}"}


# --------------------------------------------------------------------------
# 3. Groundedness — custom LLM-as-judge (Optional Part 1, Step 11)
# --------------------------------------------------------------------------

# The first version of this prompt disagreed with itself on 7.8% of judgements
# (5 of 64): the reasoning ended "Thus, the score should be: true" while the
# structured score field came back false, always in that direction. The stock
# openevals correctness prompt was 100% self-consistent over the same 65
# judgements, so the harness was not at fault — the prompt was. Two causes were
# fixed: the prompt led with prohibitions ("NOT checking...") which biases toward
# false, and it carried a note about output format that openevals also controls.
# `analyze_results.py` re-measures this every run rather than assuming it stayed
# fixed.

GROUNDEDNESS_PROMPT = """You are judging whether an answer is supported by the
source clauses it cites.

<Rubric>
  A grounded answer:
  - makes only claims that the cited clause text states or directly entails
  - may paraphrase, condense or reorder the clause text freely
  - may apply a stated rule to the facts in the question, including simple
    arithmetic on a stated period
  An ungrounded answer:
  - states a number, deadline, obligation or exception that the cited text does
    not contain
  - contradicts the cited text
  - answers from general legal knowledge where the cited text is silent

  Judge support, not style, completeness or helpfulness. A faithful paraphrase is
  grounded. Wording that differs from the clause is not, by itself, a defect.
  A partial answer whose claims are all supported is still grounded.
</Rubric>

<Instructions>
  - Break the answer into its individual factual claims
  - For each claim, find the sentence in the cited clause text that supports it
  - Score true if every claim is supported; score false if any claim is
    unsupported by, or contradicts, the cited text
  - Name each unsupported claim in your reasoning
</Instructions>

<input>
{inputs}
</input>

<output>
{outputs}
</output>

The text of the clauses the answer cited:

<reference_outputs>
{reference_outputs}
</reference_outputs>"""

_groundedness_judge = create_llm_as_judge(
    prompt=GROUNDEDNESS_PROMPT,
    feedback_key="groundedness",
    model=JUDGE_MODEL,
)


def _cited_clause_text(outputs: dict) -> str:
    """The text of the clauses the MODEL cited - not the reference clauses.

    This is the point of the evaluator: it judges the answer against the source
    the model itself pointed at, so citing a real clause that does not support
    the claim is caught.
    """
    cited = [c.strip() for c in (outputs.get("clause_ids") or []) if str(c).strip()]
    known = [c for c in cited if c in KNOWN_IDS]
    if not known:
        return "(the answer cited no clause that exists in the corpus)"
    return "\n\n".join(f"[{c}] {CLAUSES[c]['title']}\n{CLAUSES[c]['body']}" for c in known)


def groundedness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Is every claim supported by the text of the clauses the answer cited?"""
    result = _groundedness_judge(
        inputs=inputs.get("question", ""),
        outputs=outputs.get("answer", ""),
        reference_outputs=_cited_clause_text(outputs),
    )
    return {
        "key": "groundedness",
        "score": bool(result.get("score")),
        "comment": result.get("comment", ""),
    }


ALL_EVALUATORS = [correctness, citation_validity, citation_wellformed,
                  citation_fabricated_free, groundedness]


if __name__ == "__main__":
    # Controls. Deterministic evaluators are checked against constructed inputs,
    # so these are exact assertions rather than illustrations; the LLM judge is
    # checked on a grounded/ungrounded pair it must separate.
    ok = True

    print("citation_validity  (did it point at the right clauses?)")
    for name, cited, expected, want in [
        ("exact match",      ["RB-3"],         ["RB-3"],         1.0),
        ("extra valid",      ["RB-3", "RB-4"], ["RB-3"],         1.0),
        ("missing one",      ["RB-3"],         ["RB-3", "CT-8"], 0.0),
        ("prefix dropped",   ["10"],           ["RB-10"],        1.0),
        ("ambiguous number", ["6"],            ["FC-6"],         0.0),
        ("fabricated",       ["RB-99"],        ["RB-3"],         0.0),
        ("nothing cited",    [],               ["RB-3"],         0.0),
    ]:
        got = citation_validity({}, {"clause_ids": cited}, {"clause_ids": expected})
        flag = "PASS" if got["score"] == want else "FAIL"
        ok &= got["score"] == want
        print(f"  {flag}  {name:17} cited={str(cited):16} -> {got['score']}  ({got['comment']})")

    print("\ncitation_fabricated_free  (did it invent an authority?)")
    for name, cited, want in [
        ("real id",          ["RB-3"], 1.0),
        ("prefix dropped",   ["6"],    1.0),   # ambiguous, but NOT fabricated
        ("invented",         ["ZZ-1"], 0.0),
        ("invented number",  ["RB-99"], 0.0),
    ]:
        got = citation_fabricated_free({}, {"clause_ids": cited}, {})
        flag = "PASS" if got["score"] == want else "FAIL"
        ok &= got["score"] == want
        print(f"  {flag}  {name:17} cited={str(cited):16} -> {got['score']}  ({got['comment']})")

    print("\ncitation_wellformed  (could an auditor look it up?)")
    for name, cited, want in [
        ("exact",            ["RB-3"], 1.0),
        ("unambiguous bare", ["10"],   1.0),
        ("ambiguous bare",   ["6"],    0.0),
        ("fabricated",       ["ZZ-9"], 0.0),
    ]:
        got = citation_wellformed({}, {"clause_ids": cited}, {})
        flag = "PASS" if got["score"] == want else "FAIL"
        ok &= got["score"] == want
        print(f"  {flag}  {name:17} cited={str(cited):16} -> {got['score']}  ({got['comment']})")

    print("\ngroundedness  (live judge — needs OPENAI_API_KEY)")
    probes = [
        ("faithful paraphrase", "25 months from the date the applicant was notified.",
         ["RB-11"], True),
        ("added obligation",
         "36 months, and the notice must also be filed with the state regulator.",
         ["RB-11"], False),
        ("applies the rule to the facts",
         "Only one notice is needed, and it must go to the primary applicant where "
         "one is readily apparent.", ["RB-9"], True),
    ]
    for name, answer, cids, want in probes:
        got = groundedness({"question": "compliance question"},
                           {"answer": answer, "clause_ids": cids}, {})
        flag = "PASS" if got["score"] is want else "FAIL"
        ok &= got["score"] is want
        print(f"  {flag}  {name:30} -> {got['score']}")
        if got["score"] is not want:
            print(f"        judge said: {got['comment'][:200]}")

    print(f"\n{'ALL CONTROLS PASSED' if ok else 'SOME CONTROLS FAILED'}")
    raise SystemExit(0 if ok else 1)
