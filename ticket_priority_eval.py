"""Create the LangSmith dataset and evaluate an LLM ticket-priority classifier."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

DATA_PATH = Path(__file__).parent / "data" / "support_ticket_priority_examples.json"
DATASET_NAME = "ironhack-support-ticket-priority-v1"
PROJECT_NAME = "ironhack-ticket-priority-evaluation"
DEFAULT_MODEL = "gpt-5.6-luna"
VALID_PRIORITIES = {"P1", "P2", "P3"}

SYSTEM_INSTRUCTIONS = """You triage SaaS support tickets using exactly one priority label.

P1: an active outage, security/privacy incident, data loss, or revenue-critical function is unavailable with no practical workaround.
P2: a major feature is materially degraded or blocked for multiple users, but the service still works or a workaround exists.
P3: a routine question, feature request, cosmetic issue, or narrow minor bug with an easy workaround.

Return only P1, P2, or P3. Do not add punctuation or explanation."""


def load_examples(path: Path = DATA_PATH) -> list[dict[str, Any]]:
    """Load and validate the local source-of-truth examples."""
    examples = json.loads(path.read_text(encoding="utf-8"))
    if len(examples) < 10:
        raise ValueError("The evaluation dataset must contain at least 10 examples")

    seen_tickets: set[str] = set()
    for index, example in enumerate(examples, start=1):
        ticket = example.get("inputs", {}).get("ticket", "").strip()
        priority = example.get("outputs", {}).get("priority")
        metadata = example.get("metadata", {})
        if not ticket or ticket in seen_tickets:
            raise ValueError(f"Example {index} has an empty or duplicate ticket")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Example {index} has invalid priority {priority!r}")
        if not metadata.get("category") or not metadata.get("reason"):
            raise ValueError(f"Example {index} lacks useful metadata")
        seen_tickets.add(ticket)
    return examples


def normalize_priority(value: str) -> str:
    """Extract one valid label while rejecting missing or ambiguous responses."""
    labels = set(re.findall(r"\bP[123]\b", value.upper()))
    if len(labels) != 1:
        raise ValueError(f"Expected exactly one priority label, received {value!r}")
    return labels.pop()


def priority_accuracy(
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> dict[str, Any]:
    """Score exact agreement between the generated and reference priorities."""
    del inputs
    try:
        predicted = normalize_priority(str(outputs.get("priority", "")))
    except ValueError as error:
        return {"key": "priority_accuracy", "score": 0, "comment": str(error)}
    expected = str(reference_outputs["priority"]).upper()
    return {
        "key": "priority_accuracy",
        "score": int(predicted == expected),
        "comment": f"predicted={predicted}; expected={expected}",
    }


def build_target() -> Any:
    """Build the traced LLM target only after credentials are available."""
    from langsmith import traceable, wrappers
    from openai import OpenAI

    traced_openai = wrappers.wrap_openai(OpenAI())
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    @traceable(name="classify_support_ticket", run_type="chain")
    def classify_support_ticket(inputs: dict[str, Any]) -> dict[str, str]:
        response = traced_openai.responses.create(
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=inputs["ticket"],
        )
        return {"priority": normalize_priority(response.output_text)}

    return classify_support_ticket


def require_hosted_credentials() -> None:
    missing = [name for name in ("LANGSMITH_API_KEY", "OPENAI_API_KEY") if not os.getenv(name)]
    if missing:
        raise SystemExit(
            "Missing required environment variable(s): " + ", ".join(missing) + ". Copy .env.example to .env and add real keys."
        )


def get_or_create_dataset(client: Any, examples: list[dict[str, Any]]) -> Any:
    """Create the named dataset once and verify its remote example count."""
    dataset_name = os.getenv("LANGSMITH_DATASET_NAME", DATASET_NAME)
    if client.has_dataset(dataset_name=dataset_name):
        dataset = client.read_dataset(dataset_name=dataset_name)
    else:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Twelve balanced SaaS support tickets labelled P1, P2, or P3 for exact-match evaluation.",
        )
        client.create_examples(dataset_id=dataset.id, examples=examples)

    remote_examples = list(client.list_examples(dataset_id=dataset.id))
    if len(remote_examples) != len(examples):
        raise RuntimeError(
            f"Remote dataset contains {len(remote_examples)} examples; expected {len(examples)}. "
            "Use a new LANGSMITH_DATASET_NAME or reconcile the dataset in LangSmith."
        )
    print(f"Verified LangSmith dataset {dataset.name!r}: {len(remote_examples)} examples (id={dataset.id})")
    return dataset


def run_hosted_evaluation() -> None:
    """Upload/verify the dataset and run one real LangSmith experiment."""
    from langsmith import Client

    require_hosted_credentials()
    examples = load_examples()
    client = Client()
    dataset = get_or_create_dataset(client, examples)
    experiment_prefix = os.getenv("LANGSMITH_EXPERIMENT_PREFIX", "ticket-priority-baseline")
    results = client.evaluate(
        build_target(),
        data=dataset.name,
        evaluators=[priority_accuracy],
        experiment_prefix=experiment_prefix,
        max_concurrency=2,
        metadata={"model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL), "dataset_version": "v1"},
    )
    print(results)
    print("Open the experiment URL printed by LangSmith and record the actual metrics in evaluation_summary.md.")


def validate_local() -> None:
    """Run credential-free validation and print reproducible dataset statistics."""
    examples = load_examples()
    distribution = Counter(example["outputs"]["priority"] for example in examples)
    print(f"Validated {len(examples)} unique examples")
    print("Label distribution: " + ", ".join(f"{label}={distribution[label]}" for label in sorted(distribution)))


def main() -> None:
    load_dotenv()
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_PROJECT", PROJECT_NAME)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("validate", "evaluate"),
        nargs="?",
        default="validate",
        help="validate runs offline; evaluate requires LangSmith and OpenAI credentials",
    )
    args = parser.parse_args()
    if args.command == "evaluate":
        run_hosted_evaluation()
    else:
        validate_local()


if __name__ == "__main__":
    main()
