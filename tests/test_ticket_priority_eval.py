import json
from collections import Counter
from pathlib import Path

import pytest

from ticket_priority_eval import load_examples, normalize_priority, priority_accuracy


def test_dataset_has_twelve_unique_balanced_examples():
    examples = load_examples()
    tickets = [example["inputs"]["ticket"] for example in examples]
    labels = Counter(example["outputs"]["priority"] for example in examples)

    assert len(examples) == 12
    assert len(tickets) == len(set(tickets))
    assert labels == {"P1": 4, "P2": 4, "P3": 4}


def test_every_example_has_useful_metadata():
    for example in load_examples():
        assert example["metadata"]["category"]
        assert example["metadata"]["difficulty"] in {"clear", "boundary"}
        assert example["metadata"]["reason"]


@pytest.mark.parametrize("raw, expected", [("P1", "P1"), ("priority: P2", "P2"), ('{"priority":"P3"}', "P3")])
def test_normalize_priority_accepts_one_label(raw, expected):
    assert normalize_priority(raw) == expected


@pytest.mark.parametrize("raw", ["", "urgent", "P1 or P2"])
def test_normalize_priority_rejects_missing_or_ambiguous_labels(raw):
    with pytest.raises(ValueError):
        normalize_priority(raw)


def test_evaluator_scores_exact_match_and_mismatch():
    correct = priority_accuracy({}, {"priority": "P2"}, {"priority": "P2"})
    incorrect = priority_accuracy({}, {"priority": "P3"}, {"priority": "P2"})

    assert correct["score"] == 1
    assert incorrect["score"] == 0
    assert correct["key"] == "priority_accuracy"


def test_dataset_file_is_valid_json():
    path = Path(__file__).parents[1] / "data" / "support_ticket_priority_examples.json"
    assert isinstance(json.loads(path.read_text(encoding="utf-8")), list)
