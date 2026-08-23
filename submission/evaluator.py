from langsmith.schemas import Run, Example


def correctness_evaluator(run: Run, example: Example) -> dict:
    """Scores whether the target function correctly extracted vendor_name, 
    award_amount, and award_id compared to the dataset's ground truth. 
    Returns a structured score with per-field breakdown."""

    predicted = run.outputs or {}
    reference = example.outputs or {}

    def normalize(value):
        return (value or "").strip().upper()

    vendor_correct = normalize(predicted.get("vendor_name")) == normalize(reference.get("vendor_name"))

    predicted_amount = predicted.get("award_amount")
    reference_amount = reference.get("award_amount")
    if reference_amount is None:
        amount_correct = predicted_amount is None
    else:
        amount_correct = (
            predicted_amount is not None
            and abs(predicted_amount - reference_amount) < 0.01
        )

    award_id_correct = normalize(predicted.get("award_id")) == normalize(reference.get("award_id"))

    fields_correct = sum([vendor_correct, amount_correct, award_id_correct])
    score = fields_correct / 3

    return {
        "key": "field_extraction_correctness",
        "score": score,
        "comment": (
            f"vendor: {'✓' if vendor_correct else '✗'}, "
            f"amount: {'✓' if amount_correct else '✗'}, "
            f"award_id: {'✓' if award_id_correct else '✗'}"
        )
    }