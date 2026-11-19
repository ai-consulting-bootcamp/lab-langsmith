"""Rebuild aggregate tables and figures from saved experiment evidence, without API calls."""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.evaluation import OUT, write_json

METRICS = ["correctness", "citation_coverage", "groundedness"]


def latest_folder():
    return OUT / json.loads((OUT / "latest_run.json").read_text())["run_id"]


def wilson_interval(successes, n, z=1.959963984540054):
    p = successes / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return center-half, center+half


def analyze(folder=None):
    folder = Path(folder) if folder else latest_folder()
    manifest = json.loads((folder / "manifest.json").read_text())
    frames = [pd.read_json(folder / f"results_{cfg}.json") for cfg in manifest["experiments"]]
    df = pd.concat(frames, ignore_index=True)
    if df[METRICS].isna().any().any():
        raise ValueError("Missing scores must be resolved before aggregation")
    if df.duplicated(["configuration", "example_id"]).any():
        raise ValueError("Duplicate result rows")
    summaries, metric_rows = [], []
    for config, g in df.groupby("configuration", sort=False):
        n = len(g); passed = int(g.correctness.sum())
        low, high = wilson_interval(passed, n)
        total_cost = float(g.estimated_cost_usd.sum())
        row = {"configuration": config, "n": n, "correct": passed,
               "correctness": passed/n, "correctness_ci95_low": low, "correctness_ci95_high": high,
               "citation_coverage": float(g.citation_coverage.mean()), "groundedness": float(g.groundedness.mean()),
               "all_metrics_pass": float(g[METRICS].all(axis=1).mean()),
               "target_errors": int(g.error.notna().sum()), "prompt_tokens": int(g.prompt_tokens.sum()),
               "completion_tokens": int(g.completion_tokens.sum()), "cached_tokens": int(g.cached_tokens.sum()),
               "target_cost_usd": total_cost, "cost_per_example_usd": total_cost/n,
               "cost_per_correct_usd": total_cost/passed if passed else None,
               "mean_latency_seconds": float(g.latency_seconds.mean()),
               "median_latency_seconds": float(g.latency_seconds.median()),
               "p95_latency_seconds": float(g.latency_seconds.quantile(.95))}
        summaries.append(row)
        for metric in METRICS:
            scores = g[metric].astype(float)
            metric_rows.append({"configuration": config, "metric": metric, "n": len(scores),
                "mean": float(scores.mean()), "median": float(scores.median()),
                "passed": int(scores.sum()), "failed": int(len(scores)-scores.sum())})
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "comparison_summary.csv", index=False)
    pd.DataFrame(metric_rows).to_csv(OUT / "metric_summary.csv", index=False)
    df.to_csv(OUT / "all_results.csv", index=False)
    for field in ("category", "difficulty"):
        grouped = df.groupby(["configuration", field])[METRICS].agg(["mean", "count"])
        grouped.columns = ["_".join(c) for c in grouped.columns]
        grouped.to_csv(OUT / f"scores_by_{field}.csv")
    failures = df.loc[~df[METRICS].all(axis=1)].copy()
    failures.to_csv(OUT / "flagged_examples.csv", index=False)
    discrepancies = df.loc[df.correctness != df.groundedness].copy()
    discrepancies.to_csv(OUT / "evaluator_disagreements.csv", index=False)
    pairs = df.pivot(index="case_id", columns="configuration", values="correctness").astype(int)
    difference = pairs["policy_aware"].to_numpy()-pairs["baseline"].to_numpy()
    rng = np.random.default_rng(42)
    boot = rng.choice(difference, size=(10000, len(difference)), replace=True).mean(axis=1)
    b_wins = int((difference < 0).sum()); p_wins = int((difference > 0).sum()); discordant = b_wins + p_wins
    exact_p = min(1., 2*sum(math.comb(discordant,k) for k in range(min(b_wins,p_wins)+1))/2**discordant) if discordant else 1.
    stats = {"run_id": manifest["run_id"], "paired_n": len(difference),
             "difference_policy_aware_minus_baseline": float(difference.mean()),
             "paired_bootstrap_ci95": [float(v) for v in np.quantile(boot,[.025,.975])],
             "bootstrap_seed":42,"bootstrap_samples":10000,
             "baseline_only_correct":b_wins,"policy_aware_only_correct":p_wins,
             "exact_mcnemar_p":exact_p,
             "caveat":"Intervals are descriptive resampling summaries for this small synthetic set; they do not measure judge bias or establish production generalization."}
    write_json(OUT / "paired_statistics.json", stats)
    ledger = pd.read_json(folder / "api_usage.jsonl", lines=True)
    ledger.groupby("role").agg(calls=("response_id","count"), prompt_tokens=("prompt_tokens","sum"),
        completion_tokens=("completion_tokens","sum"), cached_tokens=("cached_tokens","sum"),
        estimated_cost_usd=("estimated_cost_usd","sum")).to_csv(OUT / "suite_costs.csv")
    calibration = json.loads((folder / "calibration.json").read_text())
    cal_metrics = []
    for key in METRICS:
        observed = [bool(x[key]) for x in calibration]; expected = [x[key+"_expected"] for x in calibration]
        tp=sum(a and b for a,b in zip(observed,expected)); fp=sum(a and not b for a,b in zip(observed,expected))
        fn=sum(not a and b for a,b in zip(observed,expected)); tn=sum(not a and not b for a,b in zip(observed,expected))
        cal_metrics.append({"metric":key,"n":len(expected),"tp":tp,"tn":tn,"fp":fp,"fn":fn,
            "accuracy":(tp+tn)/len(expected),"precision":tp/(tp+fp) if tp+fp else None,
            "recall":tp/(tp+fn) if tp+fn else None,"f1":2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None})
    pd.DataFrame(cal_metrics).to_csv(OUT / "calibration_metrics.csv", index=False)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.spines.top":False,"axes.spines.right":False})
    colors = ["#3267A8", "#D77A35"]
    fig,ax=plt.subplots(figsize=(9,5),layout="constrained")
    x=np.arange(len(METRICS)); width=.34
    for i,row in summary.iterrows():
        heights=[row[k]*100 for k in METRICS]
        bars=ax.bar(x+(i-.5)*width,heights,width,label=row.configuration.replace("_"," "),color=colors[i])
        ax.bar_label(bars,labels=[f"{v:.0f}%" for v in heights],padding=3)
    ax.set(xticks=x,xticklabels=["Correctness","Citation coverage","Groundedness"],ylim=(0,110),ylabel="Pass rate (%)",title="CloudDesk support: 20 cases per configuration")
    ax.legend(loc="lower left");fig.savefig(OUT/"metric_comparison.png",dpi=180);plt.close(fig)
    category=df.groupby(["category","configuration"]).correctness.mean().unstack()*100
    ax=category.plot.bar(figsize=(10,5),color=colors,rot=0,width=.7)
    ax.set(ylabel="Correctness pass rate (%)",xlabel="",ylim=(0,110),title="Correctness by category (4 cases per category)")
    ax.legend(title="Configuration",loc="lower left");ax.figure.tight_layout();ax.figure.savefig(OUT/"pass_rate_by_category.png",dpi=180);plt.close(ax.figure)
    fig,ax=plt.subplots(figsize=(9,5),layout="constrained")
    for i,row in summary.iterrows():
        ax.scatter(row.cost_per_example_usd*1000,row.correctness*100,s=100,color=colors[i])
        ax.annotate(row.configuration.replace("_"," "),(row.cost_per_example_usd*1000,row.correctness*100),xytext=(8,-12 if i else 8),textcoords="offset points")
        ax.errorbar(row.cost_per_example_usd*1000,row.correctness*100,
            yerr=[[100*(row.correctness-row.correctness_ci95_low)],[100*(row.correctness_ci95_high-row.correctness)]],fmt="none",color=colors[i],capsize=5)
    ax.set(xlabel="Estimated target cost per 1,000 answers (USD)",ylabel="Correctness pass rate (%)",ylim=(45,102),title="Target cost and correctness (95% Wilson intervals)")
    ax.margins(x=.65);fig.savefig(OUT/"cost_vs_performance.png",dpi=180);plt.close(fig)
    return summary, df, stats


if __name__ == "__main__":
    summary, _, stats = analyze()
    print(summary.to_string(index=False))
    print(json.dumps(stats,indent=2))
