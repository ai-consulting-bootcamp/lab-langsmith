"""Analyse the experiment results and draw the figures.

Steps 9 and 11-15 of the lab. Four passes:

  1. Headline metrics per experiment, plus cost and latency.
  2. Breakdown by category and difficulty (the dataset metadata earns its keep).
  3. Error analysis - which examples failed, and how.
  4. An audit of the judges themselves: openevals is told to end its reasoning
     with "Thus, the score should be: X", so that sentence can be parsed and
     compared against the score actually recorded. Any gap is the judge
     disagreeing with itself, and it is measured every run rather than assumed
     away.

Run:  python analyze_results.py

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import collections
import json
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "experiment_results.json"
FIGDIR = HERE / "figures"
ANALYSIS = HERE / "analysis_summary.json"

SCORE_KEYS = ["correctness", "citation_validity", "citation_wellformed",
              "citation_fabricated_free", "groundedness"]
JUDGE_KEYS = ["correctness", "groundedness"]

STATED = re.compile(r"the score should be:?\s*\**\s*(true|false)\s*\.?\s*$", re.I | re.M)
MONTHLY_QUERIES = 20_000


def mean(vals) -> float:
    vals = [v for v in vals if v is not None]
    return round(statistics.mean(vals), 3) if vals else 0.0


def headline(exp: dict) -> dict:
    rows = exp["rows"]
    cost = sum(r["cost_usd"] or 0 for r in rows)
    lat = [r["latency_s"] for r in rows if r["latency_s"]]
    return {
        "target": exp["target"],
        "label": exp["label"],
        "model": exp["model"],
        "prompt_variant": exp["prompt_variant"],
        "experiment_name": exp["experiment_name"],
        "n": len(rows),
        "errors": sum(1 for r in rows if r.get("error")),
        "scores": {k: mean([r["scores"].get(k) for r in rows]) for k in SCORE_KEYS},
        "cost_usd_total": round(cost, 6),
        "cost_usd_per_query": round(cost / len(rows), 8),
        "cost_per_1k_queries": round(cost / len(rows) * 1000, 4),
        "monthly_cost_usd": round(cost / len(rows) * MONTHLY_QUERIES, 2),
        "latency_mean_s": round(statistics.mean(lat), 2) if lat else None,
        "wall_seconds": exp["wall_seconds"],
    }


def by_group(exp: dict, field: str) -> dict:
    out: dict[str, dict] = {}
    groups = collections.defaultdict(list)
    for r in exp["rows"]:
        groups[r[field]].append(r)
    for g, rows in sorted(groups.items()):
        out[g] = {"n": len(rows),
                  **{k: mean([r["scores"].get(k) for r in rows]) for k in SCORE_KEYS}}
    return out


def judge_audit(experiments: list[dict]) -> dict:
    """Does each judge's reasoning agree with the score it recorded?"""
    tally = {k: {"judgements": 0, "parseable": 0, "mismatches": 0, "examples": []}
             for k in JUDGE_KEYS}
    for exp in experiments:
        for r in exp["rows"]:
            for k in JUDGE_KEYS:
                c = r["comments"].get(k)
                if not c:
                    continue
                t = tally[k]
                t["judgements"] += 1
                m = STATED.search(c.strip())
                if not m:
                    continue
                t["parseable"] += 1
                stated = m.group(1).lower() == "true"
                if stated != bool(r["scores"].get(k)):
                    t["mismatches"] += 1
                    if len(t["examples"]) < 5:
                        t["examples"].append(
                            f"{exp['target']}/{r['example_id']}: reasoning said "
                            f"{stated}, score recorded {bool(r['scores'].get(k))}")
    for k, t in tally.items():
        t["mismatch_rate"] = round(t["mismatches"] / t["parseable"], 4) if t["parseable"] else None
    return tally


def error_analysis(exp: dict) -> dict:
    rows = exp["rows"]
    modes = collections.Counter()
    detail = collections.defaultdict(list)
    for r in rows:
        s = r["scores"]
        eid = r["example_id"]
        if r.get("error"):
            modes["api_error"] += 1; detail["api_error"].append(eid)
        if s.get("citation_fabricated_free") == 0:
            modes["fabricated_citation"] += 1; detail["fabricated_citation"].append(eid)
        if s.get("citation_wellformed") == 0:
            modes["unverifiable_citation"] += 1; detail["unverifiable_citation"].append(eid)
        if s.get("citation_validity") == 0:
            modes["wrong_or_missing_clause"] += 1; detail["wrong_or_missing_clause"].append(eid)
        if s.get("correctness") == 0:
            modes["incorrect_answer"] += 1; detail["incorrect_answer"].append(eid)
        if s.get("groundedness") == 0:
            modes["ungrounded_claim"] += 1; detail["ungrounded_claim"].append(eid)
    return {"counts": dict(modes), "examples": {k: sorted(v) for k, v in detail.items()}}


def draw(analysis: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGDIR.mkdir(exist_ok=True)
    heads = analysis["headline"]
    labels = [h["target"] for h in heads]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 4.8))

    x = range(len(SCORE_KEYS))
    w = 0.26
    colours = ["#2e7d32", "#1565c0", "#c62828"]
    for i, h in enumerate(heads):
        vals = [h["scores"][k] for k in SCORE_KEYS]
        ax1.bar([v + (i - 1) * w for v in x], vals, w,
                label=f"{h['target']} ({h['model']}, {h['prompt_variant']})",
                color=colours[i % 3])
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([k.replace("citation_", "cite:\n").replace("_", " ")
                         for k in SCORE_KEYS], fontsize=8)
    ax1.set_ylim(0, 1.18)
    ax1.set_ylabel("mean score")
    ax1.set_title("Same model, different prompt — where it breaks",
                  fontweight="bold", fontsize=11)
    ax1.legend(fontsize=7.5, loc="upper center", ncol=3, frameon=False)
    ax1.spines[["top", "right"]].set_visible(False)

    costs = [h["cost_per_1k_queries"] for h in heads]
    corr = [h["scores"]["correctness"] for h in heads]
    ax2.scatter(costs, corr, s=140, c=colours[:len(heads)], zorder=3)
    for h, c, y in zip(heads, costs, corr):
        ax2.annotate(f" {h['target']}\n ${c:.2f}/1k", (c, y), fontsize=8.5,
                     va="center", ha="left")
    ax2.set_xscale("log")
    ax2.set_xlabel("cost per 1,000 queries (USD, log scale)")
    ax2.set_ylabel("correctness")
    ax2.set_xlim(min(costs) * 0.55, max(costs) * 3.2)
    ax2.set_ylim(0, 1.1)
    ax2.set_title("Cost vs correctness", fontweight="bold", fontsize=11)
    ax2.grid(alpha=0.25, zorder=0)
    ax2.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(FIGDIR / "experiment_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()

    # by-difficulty, correctness only, per experiment
    fig, ax = plt.subplots(figsize=(7.5, 4))
    order = ["easy", "medium", "hard"]
    for i, h in enumerate(heads):
        d = analysis["by_difficulty"][h["target"]]
        ax.plot(order, [d.get(o, {}).get("correctness", 0) for o in order],
                marker="o", label=h["target"], color=colours[i % 3])
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("correctness")
    ax.set_title("Correctness by question difficulty", fontweight="bold", fontsize=11)
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGDIR / "difficulty_breakdown.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"figures written to {FIGDIR.name}/")


def main() -> int:
    data = json.loads(RESULTS.read_text())
    exps = data["experiments"]

    analysis = {
        "dataset_name": data["dataset_name"],
        "dataset_id": data["dataset_id"],
        "project": data["project"],
        "endpoint": data["endpoint"],
        "evaluators": data["evaluators"],
        "headline": [headline(e) for e in exps],
        "by_category": {e["target"]: by_group(e, "category") for e in exps},
        "by_difficulty": {e["target"]: by_group(e, "difficulty") for e in exps},
        "errors": {e["target"]: error_analysis(e) for e in exps},
        "judge_audit": judge_audit(exps),
    }

    line = "=" * 92
    print(f"\n{line}\nCARDINAL TRUST COMPLIANCE QA — LANGSMITH EVALUATION\n{line}")
    print(f"dataset {analysis['dataset_name']}  ({exps[0]['rows'].__len__()} examples)   "
          f"project {analysis['project']}")

    print(f"\n{'-' * 92}\nHEADLINE\n{'-' * 92}")
    hdr = f"{'target':7}{'model':14}{'prompt':8}" + "".join(f"{k[:11]:>13}" for k in SCORE_KEYS)
    print(hdr)
    for h in analysis["headline"]:
        row = f"{h['target']:7}{h['model']:14}{h['prompt_variant']:8}"
        row += "".join(f"{h['scores'][k]:>13.3f}" for k in SCORE_KEYS)
        print(row)

    print(f"\n{'target':7}{'$/1k queries':>14}{'$/month@20k':>13}{'latency':>10}{'errors':>8}")
    for h in analysis["headline"]:
        print(f"{h['target']:7}{h['cost_per_1k_queries']:>14.4f}{h['monthly_cost_usd']:>13.2f}"
              f"{h['latency_mean_s']:>9.2f}s{h['errors']:>8}")

    print(f"\n{'-' * 92}\nBY DIFFICULTY (correctness)\n{'-' * 92}")
    for t, d in analysis["by_difficulty"].items():
        bits = "  ".join(f"{k}={v['correctness']:.2f}(n={v['n']})"
                         for k, v in sorted(d.items(), key=lambda kv: "emh".index(kv[0][0])))
        print(f"  {t:7} {bits}")

    print(f"\n{'-' * 92}\nBY CATEGORY (correctness)\n{'-' * 92}")
    for t, d in analysis["by_category"].items():
        bits = "  ".join(f"{k}={v['correctness']:.2f}" for k, v in d.items())
        print(f"  {t:7} {bits}")

    print(f"\n{'-' * 92}\nFAILURE MODES\n{'-' * 92}")
    for t, e in analysis["errors"].items():
        print(f"  {t}")
        if not e["counts"]:
            print("    none")
        for mode, n in sorted(e["counts"].items(), key=lambda kv: -kv[1]):
            print(f"    {mode:26} {n:>3}   {', '.join(e['examples'][mode][:8])}")

    print(f"\n{'-' * 92}\nJUDGE AUDIT — does the judge agree with its own reasoning?\n{'-' * 92}")
    for k, t in analysis["judge_audit"].items():
        rate = f"{t['mismatch_rate']:.1%}" if t["mismatch_rate"] is not None else "n/a"
        print(f"  {k:14} {t['judgements']:>3} judgements, {t['parseable']:>3} parseable, "
              f"{t['mismatches']:>2} self-contradictions ({rate})")
        for ex in t["examples"]:
            print(f"      {ex}")

    ANALYSIS.write_text(json.dumps(analysis, indent=2, ensure_ascii=False))
    print(f"\nwritten: {ANALYSIS.name}")
    draw(analysis)
    print(f"{line}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
