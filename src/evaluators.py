def exact_match_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """
    Evaluator that compares the target function's output to the dataset's ground truth.
    Returns a score of 1 if they match exactly (case-insensitive), otherwise 0.
    """
    # 1. Extract values using the keys defined in your target function and dataset
    # Since both use "expected_output", we extract that key from both dictionaries.
    actual = outputs.get("expected_output", "")
    expected = reference_outputs.get("expected_output", "")
    
    # 2. Handle potential API errors from the target function
    if actual == "Error":
        return {"key": "exact_match", "score": 0, "comment": "Target function API error"}
    
    # 3. Compare the strings (stripping whitespace and making lowercase for safety)
    is_correct = actual.strip().lower() == expected.strip().lower()
    
    # 4. Return the evaluation result in LangSmith's required format
    return {
        "key": "exact_match",
        "score": int(is_correct),
        "comment": f"Expected: '{expected}' | Got: '{actual}'"
    }

# Quick local test to verify our logic
if __name__ == "__main__":
    correct_test = exact_match_evaluator(
        inputs={"question": "some article..."},
        outputs={"expected_output": "Sports"},           # Mocking your target function
        reference_outputs={"expected_output": "Sports"}  # Mocking your dataset
    )
    print(f"Correct Test: {correct_test}")
    
    incorrect_test = exact_match_evaluator(
        inputs={"question": "some article..."},
        outputs={"expected_output": "Business"},         # Mocking your target function
        reference_outputs={"expected_output": "World"}   # Mocking your dataset
    )
    print(f"Incorrect Test: {incorrect_test}")