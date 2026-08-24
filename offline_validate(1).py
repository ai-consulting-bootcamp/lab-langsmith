"""Create an honest credential-free validation export from fixed fixtures.

This does not pretend to be a LangSmith or model run. It verifies the dataset,
scoring logic, and analysis path before any paid API call is made.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EXAMPLES_PATH = DATA_DIR / "evaluation_examples.json"
FIXTURES_PATH = DATA_DIR / "offline_fixture_outputs.json"
RESULTS_PATH = DATA_DIR / "offline_validation_results.csv"
METRICS_PATH = DATA_DIR / "offline_validation_metrics.json"
ALLOWED_STRATEGIES = {"HUMAN", "AUTOMATED", "HYBRID"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    examples = load_json(EXAMPLES_PATH)
    fixtures = {row["case_id"]: row for row in load_json(FIXTURES_PATH)}
    rows: list[dict] = []

    expected_counts: Counter[str] = Counter()
    correct_counts: Counter[str] = Counter()
    category_totals: defaultdict[str, int] = defaultdict(int)
    category_correct: defaultdict[str, int] = defaultdict(int)

    for example in examples:
        inputs = example["inputs"]
        reference = example["outputs"]
        metadata = example["metadata"]
        fixture = fixtures[inputs["case_id"]]
        exact = fixture["strategy"] == reference["strategy"]
        words = len(fixture["rationale"].split())
        format_ok = fixture["strategy"] in ALLOWED_STRATEGIES and 1 <= words <= 45

        expected_counts[reference["strategy"]] += 1
        correct_counts[reference["strategy"]] += int(exact)
        category_totals[metadata["category"]] += 1
        category_correct[metadata["category"]] += int(exact)

        rows.append(
            {
                "case_id": inputs["case_id"],
                "category": metadata["category"],
                "difficulty": metadata["difficulty"],
                "expected_strategy": reference["strategy"],
                "fixture_strategy": fixture["strategy"],
                "fixture_rationale": fixture["rationale"],
                "strategy_exact_match": int(exact),
                "format_compliance": int(format_ok),
                "validation_mode": "offline_fixed_fixture_not_model_output",
            }
        )

    with RESULTS_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    metrics = {
        "validation_mode": "offline_fixed_fixture_not_model_output",
        "case_count": total,
        "strategy_accuracy": sum(row["strategy_exact_match"] for row in rows) / total,
        "format_compliance_rate": sum(row["format_compliance"] for row in rows) / total,
        "accuracy_by_expected_strategy": {
            strategy: correct_counts[strategy] / expected_counts[strategy]
            for strategy in sorted(expected_counts)
        },
        "failed_case_ids": [
            row["case_id"] for row in rows if not row["strategy_exact_match"]
        ],
        "note": "These metrics validate the pipeline with fixed fixtures; they are not LangSmith experiment results.",
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

