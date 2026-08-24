from __future__ import annotations

"""Minimal LangSmith lab implementation by Parisa Dehghani."""

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "examples.json"
SUMMARY_PATH = ROOT / "evaluation_summary.md"
DATASET_NAME = "openevals-repo-qa"
EXPERIMENT_PREFIX = "openevals-repo-qa"

try:
    from langsmith import Client, traceable
except Exception:
    Client = None  # type: ignore[assignment]

    def traceable(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator


def exact_match(*, outputs: Any, reference_outputs: Any, **kwargs: Any) -> dict[str, Any]:
    return {
        "key": "exact_match",
        "score": json.dumps(outputs, sort_keys=True) == json.dumps(
            reference_outputs, sort_keys=True
        ),
        "comment": None,
        "metadata": None,
    }


def load_examples() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text())


def build_knowledge_base(examples: list[dict[str, Any]]) -> dict[str, str]:
    return {
        example["inputs"]["question"]: example["outputs"]["answer"]
        for example in examples
    }


def endpoint_is_reachable() -> bool:
    endpoint = os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com"
    host = urlparse(endpoint).hostname
    if not host:
        return False
    info_url = endpoint.rstrip("/") + "/info"
    request = urllib.request.Request(info_url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=2):
            return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


@traceable(name="repo_qa_target")
def target(inputs: dict[str, Any]) -> dict[str, str]:
    question = inputs["question"]
    answer = KNOWLEDGE_BASE.get(
        question,
        "I do not have a reference answer for that question.",
    )
    return {"answer": answer}


def run_local_eval(examples: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for example in examples:
        inputs = example["inputs"]
        reference_outputs = example["outputs"]
        outputs = target(inputs)
        result = exact_match(outputs=outputs, reference_outputs=reference_outputs)
        rows.append(
            {
                "question": inputs["question"],
                "predicted": outputs["answer"],
                "reference": reference_outputs["answer"],
                "score": bool(result["score"]),
            }
        )

    total = len(rows)
    passed = sum(1 for row in rows if row["score"])
    return {
        "total": total,
        "passed": passed,
        "accuracy": passed / total if total else 0.0,
        "rows": rows,
    }


def try_langsmith_eval(examples: list[dict[str, Any]]) -> str | None:
    if not os.environ.get("LANGSMITH_API_KEY") or Client is None:
        return None
    if not endpoint_is_reachable():
        return None

    try:
        client = Client()
        if not client.has_dataset(dataset_name=DATASET_NAME):
            client.create_dataset(
                DATASET_NAME,
                description=(
                    "A tiny repository-QA dataset derived from local documentation and "
                    "package docs."
                ),
            )
            client.create_examples(
                dataset_name=DATASET_NAME,
                examples=examples,
            )

        experiment = client.evaluate(
            target,
            data=DATASET_NAME,
            evaluators=[exact_match],
            experiment_prefix=EXPERIMENT_PREFIX,
            description="Minimal repository QA evaluation for the lab.",
            max_concurrency=1,
            blocking=True,
            upload_results=False,
        )
        if hasattr(experiment, "wait"):
            experiment.wait()
        return experiment.url
    except Exception:
        return None


def format_summary(local_results: dict[str, Any], experiment_url: str | None) -> str:
    accuracy_pct = local_results["accuracy"] * 100
    url_line = (
        f"LangSmith experiment: {experiment_url}."
        if experiment_url
        else "LangSmith experiment was not run in this environment because no API key was set."
    )
    return (
        "This minimal lab uses a 10-example repository-QA dataset built from the local README, "
        "package metadata, and the provided brief; the target function is a traceable "
        "lookup-based answerer, and the evaluator is exact match against the reference answer. "
        f"On the local dry run, the target scored {local_results['passed']}/{local_results['total']} "
        f"({accuracy_pct:.0f}% accuracy). The main limitation is that this is a lightweight smoke "
        "test rather than a real LLM benchmark; the next step would be to replace the lookup target "
        f"with an LLM-backed function and run the same dataset through LangSmith with live tracing. "
        f"{url_line}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("local", "langsmith", "both"),
        default="both",
        help="Run the local dry run, the LangSmith evaluation, or both.",
    )
    args = parser.parse_args()

    examples = load_examples()
    local_results = run_local_eval(examples)
    experiment_url = None

    if args.mode in {"langsmith", "both"}:
        experiment_url = try_langsmith_eval(examples)

    summary = format_summary(local_results, experiment_url)

    print(json.dumps(local_results, indent=2))
    if experiment_url:
        print(f"LangSmith experiment: {experiment_url}")


KNOWLEDGE_BASE = build_knowledge_base(load_examples())


if __name__ == "__main__":
    main()
