import ast
import json
import re
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths


BASE_DIR = Path(__file__).resolve().parent

SOURCE_FILE = (
    BASE_DIR
    / "data"
    / "trialgpt_criterion_annotations.parquet"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "curated_examples.json"
)


# ---------------------------------------------------------
# Curated case definitions


CASE_DEFINITIONS = [
    {
        "id": "case_01_clear_inclusion",
        "annotation_ids": [38],
        "category": "clear_inclusion",
        "difficulty": "easy",
    },
    {
        "id": "case_02_clear_inclusion",
        "annotation_ids": [417],
        "category": "clear_inclusion",
        "difficulty": "easy",
    },
    {
        "id": "case_03_clear_exclusion",
        "annotation_ids": [56],
        "category": "clear_exclusion",
        "difficulty": "easy",
    },
    {
        "id": "case_04_clear_exclusion",
        "annotation_ids": [96],
        "category": "clear_exclusion",
        "difficulty": "easy",
    },
    {
        "id": "case_05_missing_information",
        "annotation_ids": [15],
        "category": "missing_information",
        "difficulty": "medium",
    },
    {
        "id": "case_06_missing_information",
        "annotation_ids": [455],
        "category": "missing_information",
        "difficulty": "medium",
    },
    {
        "id": "case_07_ambiguous_evidence",
        "annotation_ids": [43],
        "category": "ambiguous_evidence",
        "difficulty": "hard",
    },
    {
        "id": "case_08_ambiguous_evidence",
        "annotation_ids": [454],
        "category": "ambiguous_evidence",
        "difficulty": "hard",
    },
    {
        "id": "case_09_multiple_criteria",
        "annotation_ids": [2, 4, 13, 15],
        "category": "multiple_criteria",
        "difficulty": "medium",
    },
    {
        "id": "case_10_multiple_criteria",
        "annotation_ids": [68, 69, 73, 74, 76],
        "category": "multiple_criteria",
        "difficulty": "hard",
    },
    {
        "id": "case_11_temporal_reasoning",
        "annotation_ids": [459],
        "category": "temporal_reasoning",
        "difficulty": "hard",
    },
    {
        "id": "case_12_boundary_value",
        "annotation_ids": [49],
        "category": "boundary_value",
        "difficulty": "medium",
    },
    {
        "id": "case_13_medical_terminology",
        "annotation_ids": [437],
        "category": "medical_terminology",
        "difficulty": "hard",
    },
    {
        "id": "case_14_mixed_evidence",
        "annotation_ids": [22],
        "category": "mixed_evidence",
        "difficulty": "hard",
    },
    {
        "id": "case_15_not_applicable",
        "annotation_ids": [42],
        "category": "not_applicable",
        "difficulty": "medium",
    },
]


# ---------------------------------------------------------
# Label normalization


def normalize_label(
    criterion_type: str,
    expert_label: str,
) -> str:
    """
    Convert TrialGPT labels into our common eligibility labels.
    """

    criterion_type = criterion_type.strip().lower()
    expert_label = expert_label.strip().lower()

    if expert_label == "not enough information":
        return "UNKNOWN"

    if expert_label == "not applicable":
        return "NOT APPLICABLE"

    if criterion_type == "inclusion":
        if expert_label == "included":
            return "MET"

        if expert_label == "not included":
            return "NOT MET"

    if criterion_type == "exclusion":
        if expert_label == "not excluded":
            return "MET"

        if expert_label == "excluded":
            return "NOT MET"

    raise ValueError(
        "Could not normalize label: "
        f"criterion_type={criterion_type}, "
        f"expert_label={expert_label}"
    )


# ---------------------------------------------------------
# Expert evidence handling


def parse_sentence_ids(value) -> list[int]:
    """
    Convert TrialGPT expert_sentences such as '[0, 2]'
    into a Python list [0, 2].
    """

    if pd.isna(value):
        return []

    if isinstance(value, list):
        return [int(item) for item in value]

    parsed = ast.literal_eval(str(value))

    return [int(item) for item in parsed]


def split_numbered_note(note: str) -> dict[int, str]:
    """
    Split a TrialGPT patient note into its numbered sentences.

    Example:
        '0. Patient is 58 years old. 1. She reports chest pain.'

    becomes:
        {
            0: 'Patient is 58 years old.',
            1: 'She reports chest pain.'
        }
    """

    matches = list(
        re.finditer(
            r"(?:^|\s)(\d+)\.\s",
            note,
        )
    )

    sentences = {}

    for index, match in enumerate(matches):

        sentence_id = int(match.group(1))
        text_start = match.end()

        if index + 1 < len(matches):
            text_end = matches[index + 1].start()
        else:
            text_end = len(note)

        sentence_text = note[
            text_start:text_end
        ].strip()

        sentences[sentence_id] = sentence_text

    return sentences


def extract_expert_evidence(
    note: str,
    sentence_ids: list[int],
) -> list[str]:
    """
    Return the patient-note sentences identified by the experts.
    """

    numbered_sentences = split_numbered_note(note)

    return [
        numbered_sentences[sentence_id]
        for sentence_id in sentence_ids
        if sentence_id in numbered_sentences
    ]


# ---------------------------------------------------------
# Build one evaluation example


def build_example(
    dataframe: pd.DataFrame,
    case_definition: dict,
) -> dict:

    annotation_ids = case_definition["annotation_ids"]

    rows = (
        dataframe[
            dataframe["annotation_id"].isin(annotation_ids)
        ]
        .copy()
        .sort_values("annotation_id")
    )

    # Confirm every requested source row exists.
    found_ids = set(
        rows["annotation_id"].astype(int).tolist()
    )

    expected_ids = set(annotation_ids)

    if found_ids != expected_ids:
        raise ValueError(
            f"{case_definition['id']}: "
            f"Expected annotation IDs {expected_ids}, "
            f"but found {found_ids}."
        )

    # All criteria grouped into one example must belong
    # to the same patient and the same clinical trial.
    if rows["patient_id"].nunique() != 1:
        raise ValueError(
            f"{case_definition['id']} contains "
            "more than one patient."
        )

    if rows["trial_id"].nunique() != 1:
        raise ValueError(
            f"{case_definition['id']} contains "
            "criteria from more than one trial."
        )

    first_row = rows.iloc[0]

    patient_note = first_row["note"]

    input_criteria = []
    reference_criteria = []

    for _, row in rows.iterrows():

        annotation_id = int(row["annotation_id"])

        criterion_type = row["criterion_type"]
        criterion_text = row["criterion_text"]

        expert_label = row["expert_eligibility"]

        normalized_label = normalize_label(
            criterion_type,
            expert_label,
        )

        expert_sentence_ids = parse_sentence_ids(
            row["expert_sentences"]
        )

        expert_evidence = extract_expert_evidence(
            patient_note,
            expert_sentence_ids,
        )

        # What the model receives
        input_criteria.append(
            {
                "criterion_id": annotation_id,
                "criterion_type": criterion_type,
                "criterion_text": criterion_text,
            }
        )

        # Ground truth used by the evaluator
        reference_criteria.append(
            {
                "criterion_id": annotation_id,
                "label": normalized_label,
                "expert_label": expert_label,
                "expert_sentence_ids": expert_sentence_ids,
                "evidence": expert_evidence,
            }
        )

    example = {
        "id": case_definition["id"],

        "inputs": {
            "patient_note": patient_note,
            "trial_title": first_row["trial_title"],
            "criteria": input_criteria,
        },

        "outputs": {
            "criteria": reference_criteria,
        },

        "metadata": {
            "category": case_definition["category"],
            "difficulty": case_definition["difficulty"],
            "source": "TrialGPT-Criterion-Annotations",
            "patient_id": first_row["patient_id"],
            "trial_id": first_row["trial_id"],
            "source_annotation_ids": annotation_ids,
            "number_of_criteria": len(annotation_ids),
        },
    }

    return example


# ---------------------------------------------------------
# Main dataset preparation


def main():

    print("Loading TrialGPT source data...")

    dataframe = pd.read_parquet(SOURCE_FILE)

    print(
        f"Source dataset: "
        f"{len(dataframe)} rows"
    )

    curated_examples = []

    for case_definition in CASE_DEFINITIONS:

        example = build_example(
            dataframe,
            case_definition,
        )

        curated_examples.append(example)

    # ---------------------------------------------
    # Quality checks
   

    if len(curated_examples) != 15:
        raise ValueError(
            "Expected exactly 15 curated examples."
        )

    unique_source_ids = {
        annotation_id
        for case in CASE_DEFINITIONS
        for annotation_id in case["annotation_ids"]
    }

    # ---------------------------------------------
    # Save JSON
    

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            curated_examples,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ---------------------------------------------
    # Summary
    

    print("\nCuration complete.")
    print(
        f"Final evaluation examples: "
        f"{len(curated_examples)}"
    )

    print(
        f"Unique TrialGPT source rows used: "
        f"{len(unique_source_ids)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print("\nCases:")

    for example in curated_examples:

        metadata = example["metadata"]

        print(
            f"- {example['id']}: "
            f"{metadata['category']} | "
            f"{metadata['difficulty']} | "
            f"{metadata['number_of_criteria']} criterion/criteria"
        )


if __name__ == "__main__":
    main()



'''
Source dataset: 1015 rows

Curation complete.
Final evaluation examples: 15
Unique TrialGPT source rows used: 21
Saved to: /Users/nevena/Ironhack_Labs/week7/lab-langsmith/data/curated_examples.json

Cases:
- case_01_clear_inclusion: clear_inclusion | easy | 1 criterion/criteria
- case_02_clear_inclusion: clear_inclusion | easy | 1 criterion/criteria
- case_03_clear_exclusion: clear_exclusion | easy | 1 criterion/criteria
- case_04_clear_exclusion: clear_exclusion | easy | 1 criterion/criteria
- case_05_missing_information: missing_information | medium | 1 criterion/criteria
- case_06_missing_information: missing_information | medium | 1 criterion/criteria
- case_07_ambiguous_evidence: ambiguous_evidence | hard | 1 criterion/criteria
- case_08_ambiguous_evidence: ambiguous_evidence | hard | 1 criterion/criteria
- case_09_multiple_criteria: multiple_criteria | medium | 4 criterion/criteria
- case_10_multiple_criteria: multiple_criteria | hard | 5 criterion/criteria
- case_11_temporal_reasoning: temporal_reasoning | hard | 1 criterion/criteria
- case_12_boundary_value: boundary_value | medium | 1 criterion/criteria
- case_13_medical_terminology: medical_terminology | hard | 1 criterion/criteria
- case_14_mixed_evidence: mixed_evidence | hard | 1 criterion/criteria
- case_15_not_applicable: not_applicable | medium | 1 criterion/criteria
'''