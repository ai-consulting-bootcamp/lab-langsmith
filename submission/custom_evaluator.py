from langsmith.schemas import Run, Example


def format_compliance_evaluator(run: Run, example: Example) -> dict:
    """Evaluates whether the target function's output honors correct data 
    TYPES, independent of whether the extracted VALUE is semantically 
    correct. A downstream system ingesting this data would break silently 
    on type mismatches even if a human reader would call the answer 'right'."""

    predicted = run.outputs or {}

    checks = {
        "vendor_name_is_string": isinstance(predicted.get("vendor_name"), (str, type(None))),
        "award_amount_is_numeric_or_none": isinstance(predicted.get("award_amount"), (int, float, type(None))),
        "award_id_is_string_or_none": isinstance(predicted.get("award_id"), (str, type(None))),
        "no_currency_symbols_in_amount": (
            not isinstance(predicted.get("award_amount"), str)
        ),
        "handles_missing_data_as_none": True  # checked contextually below
    }

    # If the reference expects None (genuinely missing data) but the model 
    # fabricated a non-null value, that's a real format/honesty failure, 
    # not just a wrong value
    reference = example.outputs or {}
    if reference.get("award_amount") is None and predicted.get("award_amount") is not None:
        checks["handles_missing_data_as_none"] = False
    if reference.get("award_id") is None and predicted.get("award_id") is not None:
        checks["handles_missing_data_as_none"] = False

    passed = sum(checks.values())
    total = len(checks)
    score = passed / total

    failed_checks = [k for k, v in checks.items() if not v]

    return {
        "key": "format_type_compliance",
        "score": score,
        "comment": f"Failed: {failed_checks}" if failed_checks else "All format checks passed"
    }