"""Run calibration, smoke checks, and a paired prompt comparison in LangSmith."""
from __future__ import annotations
import argparse
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version

import pandas as pd
from langsmith import tracing_context
from src.evaluation import (CONFIG, ROOT, OUT, PROMPTS, GROUNDEDNESS_PROMPT, UsageLedger,
    connect, load_examples, ensure_dataset, make_target, make_evaluators, write_json)
from openevals.prompts import CORRECTNESS_PROMPT


def calibrate(evaluators, examples, folder):
    first, last = examples[0], examples[-1]
    fixtures = [
        ("correct", first, first["outputs"]["answer"], (True, True, True)),
        ("wrong_limits", first, "Free allows 30 members and 100 GB. [PLAN-01]", (False, True, False)),
        ("incomplete", first, "Free supports at most 3 members. [PLAN-01]", (False, True, True)),
        ("missing_citation", first, "Free permits up to 3 members and 1 GB of workspace storage.", (True, False, True)),
        ("invented_action", last, "I opened a priority ticket and verified the outage. [SUPPORT-01]", (False, True, False)),
    ]
    rows = []
    for label, example, answer, expected in fixtures:
        row = {"fixture": label, "inputs": example["inputs"], "answer": answer,
               "reference": example["outputs"]["answer"], "label_origin": "policy-derived test fixture, not independent human annotation"}
        for evaluator, want in zip(evaluators, expected):
            args = {"outputs": {"answer": answer}, "reference_outputs": example["outputs"]}
            if evaluator.__name__ != "citation_coverage":
                args["inputs"] = example["inputs"]
            feedback = evaluator(**args)
            key = feedback["key"]
            row[key] = bool(feedback["score"])
            row[key + "_expected"] = want
            row[key + "_comment"] = feedback.get("comment", "")
        rows.append(row)
        write_json(folder / "calibration.json", rows)
        print("Calibration:", label, flush=True)
    return rows


def export_results(results, config_name, folder):
    rows = []
    for item in results:
        run, ex = item["run"], item["example"]
        outputs = run.outputs or {}
        row = {"configuration": config_name, "case_id": ex.metadata["case_id"],
               "example_id": str(ex.id), "run_id": str(run.id),
               "category": ex.metadata["category"], "difficulty": ex.metadata["difficulty"],
               "question": ex.inputs["question"], "context": ex.inputs["context"],
               "reference_answer": ex.outputs["answer"], "answer": outputs.get("answer", ""),
               "error": outputs.get("error") or run.error,
               "model": outputs.get("model"), "finish_reason": outputs.get("finish_reason"),
               "prompt_tokens": outputs.get("prompt_tokens"), "completion_tokens": outputs.get("completion_tokens"),
               "cached_tokens": outputs.get("cached_tokens"), "latency_seconds": outputs.get("latency_seconds"),
               "estimated_cost_usd": outputs.get("estimated_cost_usd")}
        for feedback in item["evaluation_results"]["results"]:
            row[feedback.key] = feedback.score
            row[feedback.key + "_comment"] = feedback.comment
        rows.append(row)
    rows.sort(key=lambda r: r["case_id"])
    write_json(folder / f"results_{config_name}.json", rows)
    pd.DataFrame(rows).to_csv(folder / f"results_{config_name}.csv", index=False)
    if len(rows) != 20 or len({r["example_id"] for r in rows}) != 20:
        raise RuntimeError("Experiment did not process exactly 20 unique examples")
    for row in rows:
        for key in ("correctness", "citation_coverage", "groundedness"):
            if row.get(key) not in (True, False, 0, 1):
                raise RuntimeError(f"Missing evaluator score: {row['case_id']} / {key}")
    return rows


def run_suite():
    examples = load_examples()
    client = connect()
    dataset, remote_examples = ensure_dataset(client, examples)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = OUT / run_id
    folder.mkdir(parents=True, exist_ok=False)
    ledger = UsageLedger(folder / "api_usage.jsonl")
    target_client, judge_client = ledger.client("target"), ledger.client("judge")
    evaluators = make_evaluators(judge_client)
    manifest = {"run_id": run_id, "started_at_utc": datetime.now(timezone.utc).isoformat(),
                "dataset_id": str(dataset.id), "dataset_url": dataset.url,
                "configuration": CONFIG, "prompts": PROMPTS,
                "correctness_prompt": CORRECTNESS_PROMPT, "groundedness_prompt": GROUNDEDNESS_PROMPT,
                "python_version": platform.python_version(),
                "packages": {name: version(name) for name in ("openai", "langsmith", "openevals", "pandas", "matplotlib", "python-dotenv")},
                "experiments": {}, "status": "running"}
    write_json(folder / "manifest.json", manifest)
    print("Dataset verified:", dataset.url, flush=True)
    with tracing_context(client=client, project_name=CONFIG["project_name"]):
        calibration = calibrate(evaluators, examples, folder)
        smoke = []
        for config_name in PROMPTS:
            target = make_target(target_client, config_name)
            for index in (0, 5, 14):
                result = target(examples[index]["inputs"])
                smoke.append({"configuration": config_name, "case_id": examples[index]["metadata"]["case_id"], **result})
                write_json(folder / "smoke_tests.json", smoke)
                if result.get("error"):
                    raise RuntimeError("Target smoke test failed: " + result["error"])
        for config_name in PROMPTS:
            print("Starting experiment:", config_name, flush=True)
            results = client.evaluate(make_target(target_client, config_name), data=remote_examples,
                evaluators=evaluators, experiment_prefix=f"clouddesk-{config_name}-{run_id}",
                description=f"CloudDesk v1; {config_name}; paired prompt comparison; fixed model and evaluators.",
                metadata={"configuration": config_name, "target_model": CONFIG["target_model"],
                          "judge_model": CONFIG["judge_model"], "temperature": CONFIG["temperature"],
                          "dataset_version": "v1", "suite_id": run_id},
                max_concurrency=CONFIG["max_concurrency"], blocking=True)
            rows = export_results(results, config_name, folder)
            project = client.read_project(project_name=results.experiment_name)
            manifest["experiments"][config_name] = {"name": results.experiment_name,
                "project_id": str(project.id), "project_url": project.url,
                "comparison_url": dataset.url + "/compare?selectedSessions=" + str(project.id),
                "rows": len(rows), "target_errors": sum(bool(r["error"]) for r in rows)}
            write_json(folder / "manifest.json", manifest)
            print("Completed:", config_name, len(rows), "examples", flush=True)
    client.flush()
    manifest["status"] = "completed"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(folder / "manifest.json", manifest)
    write_json(OUT / "latest_run.json", {"run_id": run_id})
    print("Saved run:", run_id, flush=True)
    return folder


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        print("Validated", len(load_examples()), "examples; no API calls made.")
    else:
        run_suite()
