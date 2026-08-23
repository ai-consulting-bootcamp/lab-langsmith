import json

from langsmith import traceable

from config import openai_client


TARGET_MODEL = "gpt-4o-mini"

ALLOWED_LABELS = {
    "MET",
    "NOT MET",
    "UNKNOWN",
    "NOT APPLICABLE",
}


SYSTEM_PROMPT = """
You are a clinical trial eligibility screening assistant.

Your task is to compare a patient note with clinical trial eligibility
criteria.

For EACH criterion, classify the patient's status using exactly one of:

MET
- For an inclusion criterion: the patient satisfies the requirement.
- For an exclusion criterion: the exclusion condition is absent.

NOT MET
- For an inclusion criterion: the patient clearly does not satisfy the
  requirement.
- For an exclusion criterion: the exclusion condition is present.

UNKNOWN
- The patient note does not contain enough information to determine
  whether the criterion is satisfied.
- Do not infer missing information.
- Do not calculate or derive values that are not explicitly reported.

NOT APPLICABLE
- The criterion clearly does not apply to this patient based on explicit
  information in the patient note.

Rules:
1. Use only the supplied patient note.
2. Do not invent clinical facts.
3. Do not infer that an unmentioned condition is absent.
4. Return exactly one result for every supplied criterion.
5. Preserve each criterion_id exactly.
6. Evidence must come directly from the patient note.
7. If there is no supporting evidence, return an empty evidence list.
8. Give a short explanation for each classification.
9. This is screening support only. Do not make a final enrollment decision.

Return valid JSON only.
"""


def format_criteria(criteria: list[dict]) -> str:
    """
    Convert the list of trial criteria into readable prompt text.
    """

    formatted = []

    for criterion in criteria:
        formatted.append(
            f"""
Criterion ID: {criterion["criterion_id"]}
Type: {criterion["criterion_type"]}
Criterion: {criterion["criterion_text"]}
""".strip()
        )

    return "\n\n".join(formatted)


def derive_screening_summary(results: list[dict]) -> str:
    """
    Produce a deterministic overall screening summary from
    criterion-level labels.
    """

    labels = {
        result["label"]
        for result in results
    }

    if "NOT MET" in labels:
        return (
            "At least one trial criterion is not met. "
            "Human review is required; this is not a final "
            "enrollment decision."
        )

    if "UNKNOWN" in labels:
        return (
            "No criterion is currently classified as NOT MET, "
            "but at least one criterion is UNKNOWN. Additional "
            "information and human review are required."
        )

    return (
        "All assessed applicable criteria are MET. "
        "Human review is still required before any enrollment decision."
    )


def validate_results(
    results: list[dict],
    input_criteria: list[dict],
) -> None:
    """
    Validate the model output before returning it.
    """

    if len(results) != len(input_criteria):
        raise ValueError(
            "The model returned a different number of criteria "
            "than it received."
        )

    expected_ids = {
        criterion["criterion_id"]
        for criterion in input_criteria
    }

    returned_ids = {
        result["criterion_id"]
        for result in results
    }

    if returned_ids != expected_ids:
        raise ValueError(
            "Returned criterion IDs do not match input criterion IDs."
        )

    for result in results:

        if result["label"] not in ALLOWED_LABELS:
            raise ValueError(
                f"Invalid label: {result['label']}"
            )

        if not isinstance(result["evidence"], list):
            raise ValueError(
                "Evidence must be returned as a list."
            )


@traceable(
    name="clinical-trial-eligibility-target",
    metadata={"model": TARGET_MODEL},
)
def screen_patient(inputs: dict) -> dict:
    """
    Evaluate one patient note against one or more
    clinical-trial eligibility criteria.
    """

    patient_note = inputs["patient_note"]
    trial_title = inputs["trial_title"]
    criteria = inputs["criteria"]

    user_prompt = f"""
Clinical trial:
{trial_title}

PATIENT NOTE:
{patient_note}

ELIGIBILITY CRITERIA:
{format_criteria(criteria)}

Return JSON in exactly this structure:

{{
  "criteria": [
    {{
      "criterion_id": 123,
      "label": "MET",
      "evidence": [
        "Exact supporting text from the patient note."
      ],
      "reasoning": "Brief explanation."
    }}
  ]
}}
"""

    try:
        response = openai_client.chat.completions.create(
            model=TARGET_MODEL,
            temperature=0,
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        parsed = json.loads(content)

        results = parsed["criteria"]

        validate_results(
            results=results,
            input_criteria=criteria,
        )

        return {
            "criteria": results,
            "screening_summary": (
                derive_screening_summary(results)
            ),
        }

    except Exception as error:
        raise RuntimeError(
            "Clinical trial eligibility target failed."
        ) from error


if __name__ == "__main__":

    from pathlib import Path

    DATA_FILE = (
        Path(__file__).resolve().parent
        / "data"
        / "curated_examples.json"
    )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        examples = json.load(file)

    test_case_ids = {
        "case_01_clear_inclusion",
        "case_09_multiple_criteria",
        "case_15_not_applicable",
    }

    for example in examples:

        if example["id"] not in test_case_ids:
            continue

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"Testing: {example['id']}"
        )

        result = screen_patient(
            example["inputs"]
        )

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )


'''
======================================================================
Testing: case_01_clear_inclusion
{
  "criteria": [
    {
      "criterion_id": 38,
      "label": "MET",
      "evidence": [
        "He presents in March to the ER with fever up to 39 C, dyspnea and cough for 2 days."
      ],
      "reasoning": "The patient has both cough and shortness of breath (dyspnea), satisfying the inclusion criterion."
    }
  ],
  "screening_summary": "All assessed applicable criteria are MET. Human review is still required before any enrollment decision."
}

======================================================================
Testing: case_09_multiple_criteria
{
  "criteria": [
    {
      "criterion_id": 2,
      "label": "MET",
      "evidence": [
        "A 58-year-old African-American woman"
      ],
      "reasoning": "The patient is 58 years old, which falls within the age range of 25 to 65 years."
    },
    {
      "criterion_id": 4,
      "label": "MET",
      "evidence": [
        "The patient will provide informed consent"
      ],
      "reasoning": "The patient has indicated that she will provide informed consent, satisfying the requirement."
    },
    {
      "criterion_id": 13,
      "label": "NOT MET",
      "evidence": [
        "She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease."
      ],
      "reasoning": "The patient does not have IDDM (Type-1 diabetes mellitus) as she denies having diabetes."
    },
    {
      "criterion_id": 15,
      "label": "NOT APPLICABLE",
      "evidence": [],
      "reasoning": "The patient is a 58-year-old woman and there is no indication that she is pregnant or nursing."
    }
  ],
  "screening_summary": "At least one trial criterion is not met. Human review is required; this is not a final enrollment decision."
}

======================================================================
Testing: case_15_not_applicable
{
  "criteria": [
    {
      "criterion_id": 42,
      "label": "NOT MET",
      "evidence": [],
      "reasoning": "The patient is an 8-year-old male, and the criterion regarding pregnant women does not apply."
    }
  ],
  "screening_summary": "At least one trial criterion is not met. Human review is required; this is not a final enrollment decision."
}
'''