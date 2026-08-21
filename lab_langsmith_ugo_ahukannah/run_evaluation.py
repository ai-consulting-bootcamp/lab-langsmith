"""Create the LangSmith dataset and run the evaluation experiments.

Steps 4, 7 and 14 of the lab.

  python run_evaluation.py --upload            create/refresh the dataset only
  python run_evaluation.py                     upload if needed, then run "mini"
  python run_evaluation.py --targets mini,gpt4o,terse    the A/B comparison

The dataset is created once and reused: LangSmith datasets are addressed by name,
and blindly re-creating one either errors or silently forks the examples out from
under an earlier experiment, which makes two experiments incomparable.

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(Path.home() / ".config/ironhack/.env.local")
load_dotenv(HERE / ".env", override=True)

PROJECT = os.getenv("LANGSMITH_PROJECT", "cardinal-trust-compliance-qa")
os.environ.setdefault("LANGSMITH_PROJECT", PROJECT)
os.environ.setdefault("LANGSMITH_TRACING", "true")

DATA_FILE = HERE / "dataset_examples.json"
RESULTS = HERE / "experiment_results.json"


def require_langsmith_key() -> str:
    """LangSmith accepts either env var name; check both before failing."""
    key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    if not key:
        sys.exit(
            "No LangSmith API key found.\n"
            "  Add LANGSMITH_API_KEY=... to ~/.config/ironhack/.env.local\n"
            "  (get one at https://smith.langchain.com -> Settings -> API Keys)\n"
            "  If your workspace is in the EU, also set\n"
            "  LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com"
        )
    os.environ["LANGSMITH_API_KEY"] = key
    os.environ.setdefault("LANGCHAIN_API_KEY", key)
    return key


def ensure_dataset(client, payload: dict, refresh: bool = False):
    """Create the dataset if absent; reuse it otherwise."""
    name = payload["dataset_name"]
    examples = payload["examples"]

    if client.has_dataset(dataset_name=name):
        ds = client.read_dataset(dataset_name=name)
        existing = list(client.list_examples(dataset_id=ds.id))
        print(f"dataset '{name}' exists with {len(existing)} examples")
        if not refresh:
            if len(existing) != len(examples):
                print(f"  WARNING: local file has {len(examples)} examples, "
                      f"LangSmith has {len(existing)}. Re-run with --refresh to sync.")
            return ds
        print(f"  --refresh: deleting {len(existing)} examples and re-uploading")
        for ex in existing:
            client.delete_example(example_id=ex.id)
    else:
        ds = client.create_dataset(dataset_name=name, description=payload["description"])
        print(f"created dataset '{name}'  id={ds.id}")

    client.create_examples(
        dataset_id=ds.id,
        inputs=[e["inputs"] for e in examples],
        outputs=[e["outputs"] for e in examples],
        metadata=[e["metadata"] for e in examples],
    )
    n = len(list(client.list_examples(dataset_id=ds.id)))
    print(f"uploaded {len(examples)} examples; dataset now holds {n}")
    if n != len(examples):
        sys.exit(f"upload verification failed: expected {len(examples)}, found {n}")
    return ds


def run_experiment(client, target_key: str, dataset_name: str, evaluators, concurrency: int):
    from target_function import TARGETS

    spec = TARGETS[target_key]
    print(f"\n=== experiment: {target_key} — {spec['label']} ===")
    t0 = time.perf_counter()
    results = client.evaluate(
        spec["fn"],
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix=f"cardinal-{target_key}",
        max_concurrency=concurrency,
        metadata={"model": spec["model"], "prompt_variant": spec["prompt"],
                  "target": target_key},
    )
    elapsed = time.perf_counter() - t0

    rows = []
    for r in results:
        run, example = r["run"], r["example"]
        outputs = run.outputs or {}
        feedback = {f.key: f.score for f in (r.get("evaluation_results", {}).get("results") or [])}
        comments = {f.key: f.comment for f in (r.get("evaluation_results", {}).get("results") or [])}
        rows.append({
            "example_id": (example.metadata or {}).get("example_id"),
            "category": (example.metadata or {}).get("category"),
            "difficulty": (example.metadata or {}).get("difficulty"),
            "question": (example.inputs or {}).get("question"),
            "reference_answer": (example.outputs or {}).get("answer"),
            "reference_clause_ids": (example.outputs or {}).get("clause_ids"),
            "answer": outputs.get("answer"),
            "clause_ids": outputs.get("clause_ids"),
            "prompt_tokens": outputs.get("prompt_tokens"),
            "completion_tokens": outputs.get("completion_tokens"),
            "cost_usd": outputs.get("cost_usd"),
            "error": outputs.get("error"),
            "scores": feedback,
            "comments": comments,
            "latency_s": (run.end_time - run.start_time).total_seconds()
                          if run.end_time and run.start_time else None,
        })

    experiment_name = getattr(results, "experiment_name", None)
    print(f"  {len(rows)} examples in {elapsed:.1f}s   experiment: {experiment_name}")
    return {
        "target": target_key,
        "label": spec["label"],
        "model": spec["model"],
        "prompt_variant": spec["prompt"],
        "experiment_name": experiment_name,
        "wall_seconds": round(elapsed, 2),
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", default="mini",
                    help="comma-separated: mini, gpt4o, terse")
    ap.add_argument("--upload", action="store_true", help="create/refresh dataset only")
    ap.add_argument("--refresh", action="store_true", help="re-upload all examples")
    ap.add_argument("--concurrency", type=int, default=3)
    args = ap.parse_args()

    require_langsmith_key()
    from langsmith import Client
    from evaluators import ALL_EVALUATORS

    payload = json.loads(DATA_FILE.read_text())
    client = Client()

    endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    print(f"LangSmith endpoint: {endpoint}\nproject: {PROJECT}")

    ds = ensure_dataset(client, payload, refresh=args.refresh)
    if args.upload:
        print("\n--upload: dataset ready, no experiment run")
        return 0

    experiments = [
        run_experiment(client, t.strip(), payload["dataset_name"],
                       ALL_EVALUATORS, args.concurrency)
        for t in args.targets.split(",") if t.strip()
    ]

    out = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_name": payload["dataset_name"],
        "dataset_id": str(ds.id),
        "project": PROJECT,
        "endpoint": endpoint,
        "evaluators": [e.__name__ for e in ALL_EVALUATORS],
        "experiments": experiments,
    }
    RESULTS.write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    print(f"\nwritten: {RESULTS.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
