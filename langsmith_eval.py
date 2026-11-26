"""
LAB | Micromanage your agents - custom LangSmith dataset + evaluation

Domain: Q&A over internal operational-risk policies (fictional Northwind Payments GmbH).

Flow:
  docs/*.md + dataset_examples.json
    -> LangSmith dataset (created once, reused afterwards)
    -> target function (@traceable, wrapped OpenAI client -> every call is traced)
    -> evaluators: correctness (LLM-as-judge vs reference) + grounded_citation (code-based)
    -> client.evaluate()  -> experiment in LangSmith UI
    -> results/eval_results.csv, evaluation_summary.md, lab_proof.md

Run:   python langsmith_eval.py
Needs: .env with OPENAI_API_KEY, LANGSMITH_API_KEY
       (EU LangSmith account: also LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com)
"""
import csv
import json
import os
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_PROJECT", "policy-qa-eval")

for key in ("OPENAI_API_KEY", "LANGSMITH_API_KEY"):
    if not os.getenv(key):
        sys.exit(f"{key} missing. Add it to .env (see .env.example).")

from langsmith import Client, traceable  # noqa: E402
from langsmith.wrappers import wrap_openai  # noqa: E402
from openai import OpenAI  # noqa: E402

# ------------------------------------------------------------------ config
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", MODEL)
DATASET_NAME = "northwind-policy-qa-v1"
DATASET_DESC = (
    "14 Q&A pairs over two fictional operational-risk policies (incident management, "
    "vendor/outsourcing). Includes multi-condition reasoning questions and 2 out-of-scope "
    "questions that should be refused. Reference outputs: answer, policy file, section."
)
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(exist_ok=True)

POLICIES = "\n\n".join(p.read_text(encoding="utf-8") for p in sorted((HERE / "docs").glob("*.md")))
EXAMPLES = json.loads((HERE / "dataset_examples.json").read_text(encoding="utf-8"))

client = Client()
oai = wrap_openai(OpenAI())  # wrapped client: every OpenAI call shows up as a trace


def chat(model: str, messages: list, json_mode: bool = False) -> str:
    # No temperature / max_tokens: some newer OpenAI models reject them.
    kwargs = {"model": model, "messages": messages}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = oai.chat.completions.create(**kwargs)
    return (resp.choices[0].message.content or "").strip()


# ------------------------------------------------------------------ Step 3-4: dataset
def get_or_create_dataset():
    if client.has_dataset(dataset_name=DATASET_NAME):
        ds = client.read_dataset(dataset_name=DATASET_NAME)
        print(f"[dataset] reusing '{DATASET_NAME}'")
    else:
        ds = client.create_dataset(dataset_name=DATASET_NAME, description=DATASET_DESC)
        try:  # newer langsmith API
            client.create_examples(
                dataset_id=ds.id,
                examples=[{"inputs": e["inputs"], "outputs": e["outputs"], "metadata": e["metadata"]} for e in EXAMPLES],
            )
        except TypeError:  # older langsmith API
            client.create_examples(
                dataset_id=ds.id,
                inputs=[e["inputs"] for e in EXAMPLES],
                outputs=[e["outputs"] for e in EXAMPLES],
                metadata=[e["metadata"] for e in EXAMPLES],
            )
        print(f"[dataset] created '{DATASET_NAME}'")
    n = len(list(client.list_examples(dataset_id=ds.id)))
    print(f"[dataset] {n} examples in LangSmith (expected {len(EXAMPLES)})")
    return ds, n


# ------------------------------------------------------------------ Step 5: target function
SYSTEM_PROMPT = """You answer questions about the internal policies of Northwind Payments GmbH.
Use ONLY the policy text below. Cite the policy name and section number, e.g. "(Incident Management Policy, Section 4.1)".
If the policies do not answer the question, reply exactly: "Not covered in the policies."
Keep the answer to 1-3 sentences.

POLICIES:
{policies}"""


@traceable(name="policy_qa_target")
def target(inputs: dict) -> dict:
    """Input: {"question": str}. Output: {"answer": str}. Errors are returned, not raised."""
    try:
        answer = chat(
            MODEL,
            [
                {"role": "system", "content": SYSTEM_PROMPT.format(policies=POLICIES)},
                {"role": "user", "content": inputs["question"]},
            ],
        )
    except Exception as e:  # keep the experiment running if one call fails
        answer = f"ERROR: {type(e).__name__}: {e}"
    return {"answer": answer}


# ------------------------------------------------------------------ Step 6: evaluators
JUDGE_PROMPT = """You grade an answer to a question about internal company policies.
The ANSWER is correct if it states the same key facts (numbers, deadlines, roles, classification) as the REFERENCE
and does not add facts that contradict the reference or that are not supported by it. Extra wording or a citation is fine.
If the REFERENCE says the question is not covered, the ANSWER is correct only if it also says it is not covered.

QUESTION: {question}
REFERENCE: {reference}
ANSWER: {answer}

Return JSON only: {{"reasoning": "<one or two sentences>", "correct": true or false}}"""


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """LLM-as-judge: does the answer match the reference answer's key facts? Score 1/0 + reasoning."""
    try:
        raw = chat(
            JUDGE_MODEL,
            [{"role": "user", "content": JUDGE_PROMPT.format(
                question=inputs["question"], reference=reference_outputs["answer"], answer=outputs.get("answer", ""))}],
            json_mode=True,
        )
        data = json.loads(raw)
        return {"key": "correctness", "score": int(bool(data.get("correct"))), "comment": data.get("reasoning", "")}
    except Exception as e:
        return {"key": "correctness", "score": 0, "comment": f"judge error: {type(e).__name__}: {e}"}


def grounded_citation(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Code-based custom evaluator.
    In-scope question: answer must cite the reference section number.
    Out-of-scope question: answer must say 'Not covered' instead of inventing facts."""
    answer = outputs.get("answer", "")
    section = str(reference_outputs.get("section", ""))
    if section == "none":
        ok = "not covered" in answer.lower()
        return {"key": "grounded_citation", "score": int(ok),
                "comment": "out-of-scope: refused" if ok else "out-of-scope: answered instead of refusing"}
    major = section.split(".")[0]
    ok = re.search(rf"(section|sec\.?|§)\s*{re.escape(major)}(\.\d+)?\b", answer, re.I) is not None
    return {"key": "grounded_citation", "score": int(ok),
            "comment": f"cites section {section}" if ok else f"missing citation of section {section}"}


# ------------------------------------------------------------------ Step 7: run experiment
def run_experiment():
    return client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[correctness, grounded_citation],
        experiment_prefix=f"policy-qa-{MODEL}",
        description=f"Target {MODEL}, context stuffing of both policies; judge {JUDGE_MODEL}.",
        max_concurrency=2,
        metadata={"model": MODEL, "judge_model": JUDGE_MODEL},
    )


# ------------------------------------------------------------------ Step 8-9: collect + analyse
def collect(results) -> list[dict]:
    meta_by_q = {e["inputs"]["question"]: e["metadata"] for e in EXAMPLES}
    rows = []
    for r in results:
        ex, run = r["example"], r["run"]
        fb = {er.key: er for er in r["evaluation_results"]["results"]}
        q = ex.inputs["question"]
        md = ex.metadata or meta_by_q.get(q, {})
        latency = None
        if getattr(run, "end_time", None) and getattr(run, "start_time", None):
            latency = round((run.end_time - run.start_time).total_seconds(), 2)
        rows.append({
            "id": md.get("id", ""),
            "category": md.get("category", ""),
            "difficulty": md.get("difficulty", ""),
            "question": q,
            "reference": ex.outputs.get("answer", ""),
            "section": ex.outputs.get("section", ""),
            "answer": (run.outputs or {}).get("answer", ""),
            "correctness": fb["correctness"].score if "correctness" in fb else None,
            "correctness_comment": fb["correctness"].comment if "correctness" in fb else "",
            "grounded_citation": fb["grounded_citation"].score if "grounded_citation" in fb else None,
            "citation_comment": fb["grounded_citation"].comment if "grounded_citation" in fb else "",
            "latency_s": latency,
        })
    rows.sort(key=lambda x: x["id"])
    return rows


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def analyse(rows):
    by = lambda field: {k: [r for r in rows if r[field] == k] for k in sorted({r[field] for r in rows})}
    cat = {k: (mean(r["correctness"] for r in v), len(v)) for k, v in by("category").items()}
    diff = {k: (mean(r["correctness"] for r in v), len(v)) for k, v in by("difficulty").items()}
    lat = [r["latency_s"] for r in rows if r["latency_s"] is not None]
    return {
        "n": len(rows),
        "acc": mean(r["correctness"] for r in rows),
        "n_correct": sum(1 for r in rows if r["correctness"] == 1),
        "cit": mean(r["grounded_citation"] for r in rows),
        "by_category": cat,
        "by_difficulty": diff,
        "median_latency": statistics.median(lat) if lat else None,
        "fails": [r for r in rows if r["correctness"] != 1],
        "cit_fails": [r for r in rows if r["grounded_citation"] != 1],
        "disagree": [r for r in rows if r["correctness"] != r["grounded_citation"]],
    }


# ------------------------------------------------------------------ Step 10: reports
def link(name, url):
    return f"[{name}]({url})" if url else f"`{name}`"


def table(d, label):
    out = [f"| {label} | n | correctness |", "|---|---|---|"]
    out += [f"| {k} | {n} | {acc:.0%} |" for k, (acc, n) in d.items()]
    return "\n".join(out)


def write_summary(m, exp_name, exp_url, ds_url):
    worst = min(m["by_category"].items(), key=lambda kv: kv[1][0])
    para = (
        f"I evaluated `{MODEL}` as a policy Q&A assistant on the custom LangSmith dataset "
        f"{link(DATASET_NAME, ds_url)} ({m['n']} questions over two fictional operational-risk policies, "
        f"including 2 out-of-scope questions that should be refused). The target function puts both policies "
        f"into the system prompt and must cite the section; outputs were scored by an LLM-as-judge correctness "
        f"evaluator (`{JUDGE_MODEL}`, compares key facts with the reference answer) and a code-based "
        f"`grounded_citation` evaluator (correct section cited, or \"Not covered\" for out-of-scope). "
        f"Correctness was **{m['acc']:.0%} ({m['n_correct']}/{m['n']})** and grounded citation **{m['cit']:.0%}**; "
        f"the weakest category was **{worst[0]}** ({worst[1][0]:.0%}). "
    )
    if m["fails"]:
        para += f"Correctness failures: {', '.join(r['id'] for r in m['fails'])} (details below). "
    else:
        para += "There were no correctness failures, which mainly shows the dataset is still too easy. "
    para += (
        "Limitations: 14 examples is a small sample, the judge comes from the same model family as the target "
        "(possible self-preference bias), and context stuffing only works because the corpus is tiny. "
        "Recommendation: add more multi-condition and out-of-scope questions and use a different judge model "
        "before relying on the score."
    )
    lines = [
        "# Evaluation summary\n", para, "",
        f"- Experiment: {link(exp_name, exp_url)}",
        f"- Median latency per question: {m['median_latency']} s" if m["median_latency"] is not None else "",
        "", table(m["by_category"], "Category"), "", table(m["by_difficulty"], "Difficulty"), "",
    ]
    if m["fails"] or m["cit_fails"]:
        lines += ["| ID | Question | Answer | correctness | citation | Judge comment |", "|---|---|---|---|---|---|"]
        for r in sorted({r["id"]: r for r in m["fails"] + m["cit_fails"]}.values(), key=lambda r: r["id"]):
            lines.append(f"| {r['id']} | {r['question']} | {r['answer'].replace('|', '/')} | "
                         f"{r['correctness']} | {r['grounded_citation']} | {r['correctness_comment'].replace('|', '/')} |")
    lines.append("\nFull per-example results: [results/eval_results.csv](results/eval_results.csv)")
    (HERE / "evaluation_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_proof(m, rows, n_uploaded, exp_name, exp_url, ds_url):
    run = next((r for r in rows if r["difficulty"] == "hard" and r["category"] != "out_of_scope"), rows[0])
    failure = (m["fails"] or m["cit_fails"] or [None])[0]
    L = [
        "# LAB | Micromanage your agents - lab_proof.md\n",
        f"Generated by `langsmith_eval.py` on {datetime.now():%Y-%m-%d %H:%M}. Target model `{MODEL}`, judge `{JUDGE_MODEL}`.\n",
        "## 1. Domain and documents\n",
        "Domain: question answering over internal operational-risk policies, the kind of assistant a risk team would "
        "use to look up deadlines, thresholds and approvers. Sources: two fictional policies written for this lab, "
        "[docs/incident_management_policy.md](docs/incident_management_policy.md) and "
        "[docs/vendor_outsourcing_policy.md](docs/vendor_outsourcing_policy.md). A good example is a question with "
        "one checkable answer in the policies (numbers, roles, classification) plus the section it comes from; "
        "out-of-scope questions test whether the model refuses instead of inventing facts.\n",
        "## 2. Workflow\n",
        "```",
        "dataset_examples.json -> client.create_dataset/create_examples -> LangSmith dataset",
        "target(inputs) = @traceable + wrap_openai(OpenAI()) -> {'answer': ...}",
        "client.evaluate(target, data=dataset, evaluators=[correctness, grounded_citation])",
        "results -> results/eval_results.csv -> evaluation_summary.md + lab_proof.md",
        "```\n",
        "| File | Purpose |\n|---|---|",
        "| [langsmith_eval.py](langsmith_eval.py) | Dataset creation, target function, evaluators, experiment, analysis, reports |",
        "| [dataset_examples.json](dataset_examples.json) | 14 examples: inputs `question`; outputs `answer`, `policy`, `section`; metadata `id`, `category`, `difficulty` |",
        "| [results/eval_results.csv](results/eval_results.csv) | Per-example output, scores and judge reasoning |",
        "| [evaluation_summary.md](evaluation_summary.md) | Short evaluation report |\n",
        "## 3. LangSmith evidence\n",
        f"- Dataset: {link(DATASET_NAME, ds_url)}: {n_uploaded} examples uploaded. Description: {DATASET_DESC}",
        f"- Experiment: {link(exp_name, exp_url)}",
        f"- Tracing project for the test calls: `{os.environ['LANGSMITH_PROJECT']}`\n",
        "## 4. One run: input, evidence, final output\n",
        f"**Input ({run['id']}, {run['category']}, {run['difficulty']}):** {run['question']}\n",
        f"**Reference answer (dataset):** {run['reference']} (section {run['section']})\n",
        f"**Final output (target):**\n\n```\n{run['answer']}\n```\n",
        "**Evidence produced by the evaluators:**\n",
        f"- correctness = {run['correctness']}: {run['correctness_comment']}",
        f"- grounded_citation = {run['grounded_citation']}: {run['citation_comment']}\n",
        "## 5. Results\n",
        f"Correctness **{m['acc']:.0%} ({m['n_correct']}/{m['n']})**, grounded citation **{m['cit']:.0%}**.\n",
        table(m["by_category"], "Category"), "",
        "## 6. Failure / limitation\n",
    ]
    if failure:
        L += [
            f"**Observed failure ({failure['id']}):** {failure['question']}\n",
            f"Output: `{failure['answer']}`\n",
            f"Reference: `{failure['reference']}`\n",
            f"correctness = {failure['correctness']} ({failure['correctness_comment']}); "
            f"grounded_citation = {failure['grounded_citation']} ({failure['citation_comment']})\n",
        ]
    else:
        L.append("No example failed in this run, so the main limitation is the dataset itself: it is too easy to "
                 "separate a good assistant from a weak one.\n")
    if m["disagree"]:
        L.append(f"The two evaluators disagree on {', '.join(r['id'] for r in m['disagree'])}: an answer can be factually "
                 "right but uncited, or cite the right section and still get a detail wrong. That is why both are kept.\n")
    L += [
        "**Limitation:** the correctness judge is an LLM from the same family as the target, so it can share the "
        "target's blind spots and be lenient on paraphrases. With 14 examples, one flipped judgement moves the score "
        "by about 7 percentage points, so the score is indicative, not a benchmark.",
    ]
    (HERE / "lab_proof.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ main
def main():
    print(f"[setup] LangSmith project: {os.environ['LANGSMITH_PROJECT']} | endpoint: "
          f"{os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com (default, US)')}")
    ds, n_uploaded = get_or_create_dataset()
    ds_url = getattr(ds, "url", None)

    print("[test] target on 2 examples:")
    for e in EXAMPLES[:2]:
        print("   ", e["inputs"]["question"], "->", target(e["inputs"])["answer"])

    results = run_experiment()
    exp_name = getattr(results, "experiment_name", "experiment")
    exp_url = None
    try:
        exp_url = getattr(client.read_project(project_name=exp_name), "url", None)
    except Exception:
        pass

    rows = collect(results)
    with open(RESULTS_DIR / "eval_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    m = analyse(rows)
    print(f"\n[results] correctness {m['acc']:.0%} ({m['n_correct']}/{m['n']}) | grounded_citation {m['cit']:.0%}")
    for k, (acc, n) in m["by_category"].items():
        print(f"    {k:<13} n={n:<3} correctness={acc:.0%}")
    for r in m["fails"]:
        print(f"    FAIL {r['id']}: {r['answer'][:90]}")

    write_summary(m, exp_name, exp_url, ds_url)
    write_proof(m, rows, n_uploaded, exp_name, exp_url, ds_url)
    print("\nWrote results/eval_results.csv, evaluation_summary.md, lab_proof.md")


if __name__ == "__main__":
    main()
