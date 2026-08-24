def correctness_evaluator(inputs, outputs, reference_outputs):
    """
    Checks whether the model classification
    exactly matches the expected classification.
    """

    predicted = outputs["classification"].strip().upper()
    expected = reference_outputs["expected_classification"].strip().upper()

    return {
        "key": "correctness",
        "score": 1 if predicted == expected else 0,
        "comment": f"Predicted: {predicted} | Expected: {expected}"
    }