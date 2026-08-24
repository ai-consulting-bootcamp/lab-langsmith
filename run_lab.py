from __future__ import annotations

"""Simple end-to-end LangSmith evaluation lab."""

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "examples.json"
SUMMARY_PATH = ROOT / "evaluation_summary.md"
ANALYSIS_PATH = ROOT / "analysis.md"
RESULTS_PATH = ROOT / "results.csv"
LINKS_PATH = ROOT / "langsmith_links.md"

DATASET_NAME = "openevals-repo-qa-v2"
DATASET_DESCRIPTION = (
    "A 10-example repository/documentation Q&A dataset about the official "
    "OpenEvals project. Each example contains a question and supporting context "
    "as inputs, a reference answer as output, and source/topic/difficulty metadata."
)
EXPERIMENT_PREFIX = "openevals-repo-qa"
EU_ENDPOINT = "https://eu.api.smith.langchain.com"
DEFAULT_PROJECT = "lab-langsmith-parisa-dehghani"

load_dotenv(ROOT / ".env")

# This lab uses the EU LangSmith instance.
os.environ.setdefault("LANGSMITH_ENDPOINT", EU_ENDPOINT)
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_PROJECT", DEFAULT_PROJECT)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
_openai_client = None


def require_environment() -> None:
    """Fail clearly when a required key or setting is missing."""
    missing = [
        name
        for name in ("LANGSMITH_API_KEY", "OPENAI_API_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Add them to a local .env file."
        )

    if os.environ.get("LANGSMITH_TRACING", "").lower() != "true":
        raise RuntimeError("LANGSMITH_TRACING must be set to true.")

    if os.environ.get("LANGSMITH_ENDPOINT") != EU_ENDPOINT:
        raise RuntimeError(
            f"This project is configured for the EU endpoint: {EU_ENDPOINT}"
        )


def load_examples() -> list[dict[str, Any]]:
    examples = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if len(examples) < 10:
        raise ValueError("The lab requires at least 10 examples.")
    return examples


def verify_langsmith_connection(client: Client) -> None:
    """Make a real LangSmith API request and print the active setup."""
    _ = client.info
    print("LangSmith connection: OK")
    print("LangSmith project:", os.environ["LANGSMITH_PROJECT"])
    print("LangSmith endpoint:", os.environ["LANGSMITH_ENDPOINT"])
    print("Tracing enabled:", os.environ["LANGSMITH_TRACING"])


def canonical_example(example: Any) -> str:
    """Create a stable comparison string for local or LangSmith examples."""
    if isinstance(example, dict):
        inputs = example.get("inputs")
        outputs = example.get("outputs")
        metadata = example.get("metadata")
    else:
        inputs = example.inputs
        outputs = example.outputs
        metadata = example.metadata

    metadata = metadata or {}
    kept_metadata = {
        key: metadata.get(key)
        for key in ("source", "source_url", "source_section", "topic", "difficulty")
    }

    return json.dumps(
        {"inputs": inputs, "outputs": outputs, "metadata": kept_metadata},
        sort_keys=True,
        default=str,
    )


def create_or_verify_dataset(
    client: Client, examples: list[dict[str, Any]]
):
    """Create the LangSmith dataset once, then verify it on later runs."""
    if client.has_dataset(dataset_name=DATASET_NAME):
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
        remote_examples = list(client.list_examples(dataset_id=dataset.id))

        local_set = {canonical_example(item) for item in examples}
        remote_set = {canonical_example(item) for item in remote_examples}

        if local_set != remote_set:
            raise RuntimeError(
                f"LangSmith dataset '{DATASET_NAME}' already exists but its "
                "examples do not match examples.json. Delete that old dataset "
                "in LangSmith and rerun this script."
            )
        print(f"Dataset already exists and is verified: {DATASET_NAME}")
    else:
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description=DATASET_DESCRIPTION,
            metadata={
                "domain": "OpenEvals repository/documentation Q&A",
                "example_count": len(examples),
                "input_fields": ["question", "context"],
                "output_fields": ["answer"],
            },
        )
        client.create_examples(dataset_id=dataset.id, examples=examples)
        print(f"Dataset created: {DATASET_NAME}")

    uploaded = list(client.list_examples(dataset_id=dataset.id))
    if len(uploaded) != len(examples):
        raise RuntimeError(
            f"Dataset verification failed: expected {len(examples)} examples, "
            f"found {len(uploaded)}."
        )

    print(f"Dataset verification: {len(uploaded)} examples present")
    print("Dataset URL:", dataset.url or "Open the dataset in the LangSmith UI")
    return dataset


def get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = wrap_openai(OpenAI())
    return _openai_client


@traceable(name="openevals_repo_qa_target")
def target(inputs: dict[str, Any]) -> dict[str, str]:
    """Answer one documentation question with an actual LLM call."""
    question = inputs.get("question", "")
    context = inputs.get("context", "")

    if not question or not context:
        return {"answer": "The question or context is missing."}

    response = get_openai_client().chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the documentation question using only the provided "
                    "context. Keep the answer short and factual."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}",
            },
        ],
    )
    answer = response.choices[0].message.content or ""
    return {"answer": answer.strip()}


def build_correctness_evaluator():
    """Create the required OpenEvals correctness LLM-as-judge evaluator."""
    judge = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        feedback_key="correctness",
        model=f"openai:{MODEL}",
    )

    def correctness_evaluator(
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        reference_outputs: dict[str, Any],
    ):
        return judge(
            inputs=inputs,
            outputs=outputs,
            reference_outputs=reference_outputs,
        )

    return correctness_evaluator


def smoke_test(examples: list[dict[str, Any]]) -> None:
    """Test the LLM-backed target on three examples before the full run."""
    print("\nTarget function smoke test (3 examples)")
    for example in examples[:3]:
        result = target(example["inputs"])
        print("-", example["inputs"]["question"])
        print("  Model:", result["answer"])
        print("  Reference:", example["outputs"]["answer"])


def parse_score(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return 1.0
        if lowered == "false":
            return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def find_score_column(df: pd.DataFrame) -> str:
    """Find the correctness feedback column returned by LangSmith."""
    candidates = [
        col for col in df.columns if "correctness" in str(col).lower()
    ]
    for col in candidates:
        parsed = df[col].map(parse_score)
        if parsed.notna().any():
            return str(col)
    raise RuntimeError(
        "Could not find the correctness score column in the LangSmith results."
    )


def question_from_row(row: pd.Series) -> str:
    if "inputs.question" in row.index and isinstance(row["inputs.question"], str):
        return row["inputs.question"]

    if "inputs" in row.index and isinstance(row["inputs"], dict):
        return str(row["inputs"].get("question", ""))

    for col in row.index:
        if str(col).lower().endswith("question") and isinstance(row[col], str):
            return row[col]

    return ""


def write_reports(
    df: pd.DataFrame,
    examples: list[dict[str, Any]],
    dataset_url: str,
    experiment_url: str,
) -> None:
    """Save results, analysis, and the required short evaluation summary."""
    df.to_csv(RESULTS_PATH, index=False)

    score_col = find_score_column(df)
    score_values = df[score_col].map(parse_score)
    valid_scores = score_values.dropna()

    if valid_scores.empty:
        raise RuntimeError("No correctness scores were available for analysis.")

    mean_score = float(valid_scores.mean())
    median_score = float(valid_scores.median())
    pass_count = int((valid_scores >= 0.5).sum())
    total = int(valid_scores.count())
    fail_count = total - pass_count
    pass_rate = pass_count / total

    metadata_by_question = {
        item["inputs"]["question"]: item["metadata"] for item in examples
    }

    topic_rows: dict[str, list[float]] = {}
    failed_questions: list[str] = []

    for idx, row in df.iterrows():
        score = parse_score(df.loc[idx, score_col])
        if score is None:
            continue

        question = question_from_row(row)
        topic = metadata_by_question.get(question, {}).get("topic", "unknown")
        topic_rows.setdefault(topic, []).append(score)

        if score < 0.5:
            failed_questions.append(question or f"row {idx}")

    if fail_count == 0:
        pattern = (
            "No correctness failures were observed; all examples received the "
            "same passing score, so there was no meaningful best/worst split. "
            "Because every question includes focused supporting context, this "
            "small dataset may be relatively easy for the model."
        )
    else:
        failed_topics = sorted(
            {
                metadata_by_question.get(question, {}).get("topic", "unknown")
                for question in failed_questions
            }
        )
        pattern = (
            f"{fail_count} example(s) failed, concentrated in these topic(s): "
            + ", ".join(failed_topics)
            + "."
        )

    topic_lines = [
        "| Topic | Examples | Mean score |",
        "|---|---:|---:|",
    ]
    for topic, values in sorted(topic_rows.items()):
        topic_lines.append(
            f"| {topic} | {len(values)} | {sum(values)/len(values):.2f} |"
        )

    failed_block = (
        "\n".join(f"- {question}" for question in failed_questions)
        if failed_questions
        else "- None"
    )

    analysis = f"""# Evaluation Analysis

## Key metrics
- Examples evaluated: {total}
- Mean correctness: {mean_score:.2f}
- Median correctness: {median_score:.2f}
- Pass rate: {pass_rate:.0%}
- Score distribution: {pass_count} pass / {fail_count} fail
- Best score: {float(valid_scores.max()):.2f}
- Worst score: {float(valid_scores.min()):.2f}

## Performance by topic
{chr(10).join(topic_lines)}

## Pattern and interpretation
{pattern}

## Low-scoring examples
{failed_block}

## Recommendation
Keep this 10-example set as a simple baseline, then add a few harder questions that require combining information from more than one documentation section. This should reveal weaknesses that the current focused-context questions may not expose.
"""
    ANALYSIS_PATH.write_text(analysis, encoding="utf-8")

    summary = f"""# Evaluation Summary

This evaluation tested a 10-example OpenEvals repository/documentation Q&A dataset in LangSmith using a traced, LLM-backed target function with `{MODEL}` at temperature 0 and an OpenEvals `CORRECTNESS_PROMPT` LLM-as-judge evaluator. The completed experiment produced a mean correctness score of {mean_score:.2f}, median of {median_score:.2f}, and pass rate of {pass_rate:.0%} ({pass_count}/{total} examples). {pattern} The main limitations are the small manually curated dataset, the use of short supplied context passages, and possible variation in LLM-as-judge scoring. The next recommendation is to keep this as the baseline and add several harder cross-section documentation questions. LangSmith evidence: [dataset]({dataset_url}) and [experiment]({experiment_url}).

- Dataset: `{DATASET_NAME}`
- Model: `{MODEL}`
- Correctness pass rate: {pass_rate:.0%}
- Results export: `results.csv`
- Detailed analysis: `analysis.md`
"""
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    links = f"""# LangSmith Links

- Dataset: {dataset_url}
- Experiment: {experiment_url}
"""
    LINKS_PATH.write_text(links, encoding="utf-8")


def main() -> None:
    require_environment()
    examples = load_examples()

    client = Client()
    verify_langsmith_connection(client)

    dataset = create_or_verify_dataset(client, examples)
    smoke_test(examples)

    print("\nRunning LangSmith evaluation...")
    results = client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[build_correctness_evaluator()],
        experiment_prefix=EXPERIMENT_PREFIX,
        max_concurrency=2,
        blocking=True,
        metadata={
            "domain": "OpenEvals repository/documentation Q&A",
            "target_model": MODEL,
            "judge_model": MODEL,
        },
    )

    # We intentionally do NOT set upload_results=False.
    # Therefore the experiment and traces are recorded in LangSmith.
    experiment = client.read_project(
        project_name=results.experiment_name,
        include_stats=True,
    )
    experiment_url = experiment.url or "Open the experiment in the LangSmith UI"
    dataset_url = dataset.url or "Open the dataset in the LangSmith UI"

    df = results.to_pandas()
    write_reports(
        df=df,
        examples=examples,
        dataset_url=dataset_url,
        experiment_url=experiment_url,
    )

    print("\nEvaluation complete")
    print("Experiment name:", results.experiment_name)
    print("Experiment URL:", experiment_url)
    print("Dataset URL:", dataset_url)
    print("Saved:", RESULTS_PATH.name, ANALYSIS_PATH.name, SUMMARY_PATH.name)


if __name__ == "__main__":
    main()
