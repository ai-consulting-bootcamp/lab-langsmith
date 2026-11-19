"""Offline checks for corpus integrity, scoring semantics, and failure handling."""
import copy
import unittest
from unittest.mock import MagicMock
from src.evaluation import load_examples, validate_examples, citation_coverage, estimate_cost, make_target


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.examples = load_examples()

    def test_balanced_unique_corpus(self):
        self.assertEqual(validate_examples(self.examples)["unique_questions"], 20)
        counts = {}
        for e in self.examples:
            counts[e["metadata"]["category"]] = counts.get(e["metadata"]["category"], 0) + 1
        self.assertEqual(sorted(counts.values()), [4] * 5)

    def test_duplicate_is_rejected(self):
        cases = copy.deepcopy(self.examples)
        cases[-1] = cases[0]
        with self.assertRaises(ValueError):
            validate_examples(cases)

    def test_reference_context_drift_is_rejected(self):
        cases = copy.deepcopy(self.examples)
        cases[0]["inputs"]["context"] += "unsupported content"
        with self.assertRaises(ValueError):
            validate_examples(cases)

    def test_all_required_citations_and_error_status(self):
        ref = {"required_citations": ["PLAN-01", "PLAN-02"]}
        self.assertFalse(citation_coverage({"answer": "[PLAN-01]"}, ref)["score"])
        self.assertTrue(citation_coverage({"answer": "[PLAN-02] [PLAN-01]"}, ref)["score"])
        self.assertFalse(citation_coverage({"answer": "[PLAN-02] [PLAN-01]", "error": "Timeout"}, ref)["score"])

    def test_cached_input_cost(self):
        self.assertAlmostEqual(estimate_cost("gpt-4o-mini", 1000, 100, 400), 0.00018)

    def test_failure_does_not_leak_exception_payload(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = RuntimeError("sensitive provider payload")
        result = make_target(client, "baseline")(self.examples[0]["inputs"])
        self.assertEqual(result["answer"], "")
        self.assertEqual(result["error"], "RuntimeError")
        self.assertNotIn("sensitive", str(result))

    def test_invalid_input_never_calls_provider(self):
        client = MagicMock()
        result = make_target(client, "baseline")({"question": ""})
        self.assertEqual(result["error"], "ValueError")
        client.chat.completions.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
