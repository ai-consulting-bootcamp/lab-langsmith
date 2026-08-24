"""Credential-free quality checks for the local lab assets."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ALLOWED = {"HUMAN", "AUTOMATED", "HYBRID"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_dataset_has_twelve_unique_examples() -> None:
    examples = load(DATA_DIR / "evaluation_examples.json")
    case_ids = [row["inputs"]["case_id"] for row in examples]
    assert len(examples) == 12
    assert len(case_ids) == len(set(case_ids))


def test_reference_strategies_are_balanced_and_valid() -> None:
    examples = load(DATA_DIR / "evaluation_examples.json")
    counts = Counter(row["outputs"]["strategy"] for row in examples)
    assert set(counts) == ALLOWED
    assert counts == Counter({"HUMAN": 4, "AUTOMATED": 4, "HYBRID": 4})


def test_all_examples_have_required_fields() -> None:
    examples = load(DATA_DIR / "evaluation_examples.json")
    for row in examples:
        assert set(row) == {"inputs", "outputs", "metadata"}
        assert set(row["inputs"]) == {"case_id", "scenario", "constraints"}
        assert set(row["outputs"]) == {"strategy", "rationale"}
        assert set(row["metadata"]) == {"category", "difficulty", "source"}
        assert row["outputs"]["strategy"] in ALLOWED
        assert row["outputs"]["rationale"].strip()


def test_offline_fixtures_cover_every_case() -> None:
    examples = load(DATA_DIR / "evaluation_examples.json")
    fixtures = load(DATA_DIR / "offline_fixture_outputs.json")
    expected = {row["inputs"]["case_id"] for row in examples}
    actual = {row["case_id"] for row in fixtures}
    assert actual == expected

