"""Target functions under evaluation — grounded QA over the compliance corpus.

Step 5 of the lab. A target function takes one dataset input ({"question": ...})
and returns an output dict. Tracing is automatic: the OpenAI client is wrapped
with LangSmith's `wrap_openai`, and each target is decorated with `@traceable`,
so every call appears in the project as a trace with its inputs, outputs, tokens
and latency.

Three configurations are registered, which is what makes the optional
cost/performance comparison possible:

  mini      gpt-4o-mini with the full grounded-QA system prompt
  gpt4o     gpt-4o with the same prompt          -> isolates the MODEL
  terse     gpt-4o-mini with a stripped prompt   -> isolates the PROMPT

The third exists because "which model" is the question people ask and "which
prompt" is usually the one that matters. Running both ablations on one dataset is
the only way to find out which is true here.

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

from corpus_index import corpus_as_context

HERE = Path(__file__).resolve().parent
load_dotenv(Path.home() / ".config/ironhack/.env.local")
load_dotenv(HERE / ".env", override=True)

CONTEXT = corpus_as_context()

# The real prompt: answer only from the corpus, cite clause IDs, refuse to guess.
SYSTEM_PROMPT = f"""You answer questions for Cardinal Trust Bank's compliance team
about consumer adverse-action notices.

Answer ONLY from the reference clauses below. They are the authority for this
task, and they override anything you believe about the law from other sources.
If the clauses do not settle the question, say so plainly rather than filling the
gap from general knowledge.

Cite the clause IDs your answer rests on. Cite only IDs that appear below; never
invent one.

Answer in two or three sentences. Be direct and specific — give the actual number,
deadline or requirement rather than describing where to find it.

REFERENCE CLAUSES
{CONTEXT}

Return a single JSON object and nothing else:
{{"answer": "<your answer>", "clause_ids": ["<ID>", ...]}}"""

# The ablation: same corpus, same model, none of the grounding discipline.
TERSE_SYSTEM_PROMPT = f"""Answer the compliance question using these reference
clauses.

{CONTEXT}

Return JSON: {{"answer": "...", "clause_ids": [...]}}"""


PRICING = {  # USD per 1M tokens, list price at time of run
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}

_client: OpenAI | None = None


def client() -> OpenAI:
    """Wrapped OpenAI client. wrap_openai is what puts each call in the trace."""
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise SystemExit("OPENAI_API_KEY not found in ~/.config/ironhack/.env.local")
        _client = wrap_openai(OpenAI(api_key=key))
    return _client


def _ask(question: str, model: str, system_prompt: str) -> dict:
    """One grounded answer. Errors are returned, not raised, so a single bad
    example cannot abort a 22-example experiment."""
    try:
        resp = client().chat.completions.create(
            model=model,
            temperature=0,
            seed=7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        )
    except Exception as exc:  # network, rate limit, bad model name
        return {"answer": "", "clause_ids": [], "error": f"{type(exc).__name__}: {exc}"}

    raw = resp.choices[0].message.content or ""
    try:
        parsed = json.loads(raw)
        answer = str(parsed.get("answer", "")).strip()
        cids = parsed.get("clause_ids", []) or []
        cids = [str(c).strip() for c in cids if str(c).strip()]
    except json.JSONDecodeError:
        # An unparseable answer is a failure, not a crash: score it as empty and
        # let the evaluators mark it down.
        answer, cids = raw.strip(), []

    usage = resp.usage
    price = PRICING.get(model, {"input": 0.0, "output": 0.0})
    cost = (usage.prompt_tokens / 1e6 * price["input"]
            + usage.completion_tokens / 1e6 * price["output"])

    return {
        "answer": answer,
        "clause_ids": cids,
        "model": model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "cost_usd": round(cost, 8),
        "error": None,
    }


@traceable(name="compliance_qa_mini")
def target_mini(inputs: dict) -> dict:
    return _ask(inputs["question"], "gpt-4o-mini", SYSTEM_PROMPT)


@traceable(name="compliance_qa_gpt4o")
def target_gpt4o(inputs: dict) -> dict:
    return _ask(inputs["question"], "gpt-4o", SYSTEM_PROMPT)


@traceable(name="compliance_qa_mini_terse")
def target_mini_terse(inputs: dict) -> dict:
    return _ask(inputs["question"], "gpt-4o-mini", TERSE_SYSTEM_PROMPT)


TARGETS = {
    "mini": {"fn": target_mini, "model": "gpt-4o-mini", "prompt": "full",
             "label": "gpt-4o-mini + grounded prompt"},
    "gpt4o": {"fn": target_gpt4o, "model": "gpt-4o", "prompt": "full",
              "label": "gpt-4o + grounded prompt"},
    "terse": {"fn": target_mini_terse, "model": "gpt-4o-mini", "prompt": "terse",
              "label": "gpt-4o-mini + terse prompt"},
}


if __name__ == "__main__":
    # Step 5 asks for the function to be tested on 2-3 examples before use.
    data = json.loads((HERE / "dataset_examples.json").read_text())
    for ex in data["examples"][:3]:
        q = ex["inputs"]["question"]
        ref = ex["outputs"]
        print("=" * 78)
        print("Q:", q)
        out = target_mini({"question": q})
        print(f"\n  answer      : {out['answer']}")
        print(f"  cited       : {out['clause_ids']}   (reference: {ref['clause_ids']})")
        print(f"  tokens      : {out['prompt_tokens']} in / {out['completion_tokens']} out"
              f"   cost ${out['cost_usd']:.6f}   error: {out['error']}")
