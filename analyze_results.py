import re
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths


BASE_DIR = Path(__file__).resolve().parent

RESULTS_FILE = (
    BASE_DIR
    / "results"
    / "evaluation_results.csv"
)

CATEGORY_FILE = (
    BASE_DIR
    / "results"
    / "category_summary.csv"
)

DIFFICULTY_FILE = (
    BASE_DIR
    / "results"
    / "difficulty_summary.csv"
)

FAILURES_FILE = (
    BASE_DIR
    / "results"
    / "failures.csv"
)

CONFUSIONS_FILE = (
    BASE_DIR
    / "results"
    / "label_confusions.csv"
)

ANALYSIS_FILE = (
    BASE_DIR
    / "results"
    / "analysis_summary.md"
)


# ---------------------------------------------------------
# Helpers


def normalize_boolean(value):
    """
    Make correctness robust whether pandas loads it
    as bool or as text.
    """

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() == "true"


def extract_label_confusions(
    results_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract exact expected -> predicted label mismatches
    from the deterministic evaluator comments.
    """

    pattern = re.compile(
        r"expected "
        r"(NOT APPLICABLE|NOT MET|UNKNOWN|MET), "
        r"got "
        r"(NOT APPLICABLE|NOT MET|UNKNOWN|MET|None)"
    )

    records = []

    for _, row in results_df.iterrows():

        comment = str(
            row["label_accuracy_comment"]
        )

        matches = pattern.findall(comment)

        for expected, predicted in matches:

            records.append(
                {
                    "case_id": row["case_id"],
                    "category": row["category"],
                    "difficulty": row["difficulty"],
                    "expected_label": expected,
                    "predicted_label": predicted,
                }
            )

    return pd.DataFrame(records)


# ---------------------------------------------------------
# Main analysis


def main():

    print("Loading evaluation results...")

    df = pd.read_csv(RESULTS_FILE)

    if len(df) != 15:
        raise ValueError(
            f"Expected 15 results, found {len(df)}."
        )

    df["correctness"] = df[
        "correctness"
    ].apply(normalize_boolean)

    # -----------------------------------------------------
    # Aggregate metrics
   

    mean_accuracy = df[
        "label_accuracy"
    ].mean()

    median_accuracy = df[
        "label_accuracy"
    ].median()

    min_accuracy = df[
        "label_accuracy"
    ].min()

    max_accuracy = df[
        "label_accuracy"
    ].max()

    correctness_passes = int(
        df["correctness"].sum()
    )

    correctness_rate = (
        correctness_passes / len(df)
    )

    perfect_label_cases = int(
        (df["label_accuracy"] == 1.0).sum()
    )

    perfect_label_rate = (
        perfect_label_cases / len(df)
    )

    # Score distribution
    distribution = (
        df["label_accuracy"]
        .value_counts()
        .sort_index()
    )

    # -----------------------------------------------------
    # Best / worst cases
    

    best_cases = df[
        df["label_accuracy"]
        == max_accuracy
    ]

    worst_cases = df[
        df["label_accuracy"]
        == min_accuracy
    ]

    # -----------------------------------------------------
    # Category analysis
   

    category_summary = (
        df.groupby("category")
        .agg(
            examples=("case_id", "count"),
            mean_label_accuracy=(
                "label_accuracy",
                "mean",
            ),
            correctness_rate=(
                "correctness",
                "mean",
            ),
        )
        .reset_index()
        .sort_values(
            "mean_label_accuracy",
            ascending=False,
        )
    )

    category_summary.to_csv(
        CATEGORY_FILE,
        index=False,
    )

    # -----------------------------------------------------
    # Difficulty analysis
   

    difficulty_summary = (
        df.groupby("difficulty")
        .agg(
            examples=("case_id", "count"),
            mean_label_accuracy=(
                "label_accuracy",
                "mean",
            ),
            correctness_rate=(
                "correctness",
                "mean",
            ),
        )
        .reset_index()
    )

    difficulty_summary.to_csv(
        DIFFICULTY_FILE,
        index=False,
    )

    # -----------------------------------------------------
    # Failure analysis
    

    failures = df[
        (df["label_accuracy"] < 1.0)
        | (~df["correctness"])
    ].copy()

    failures.to_csv(
        FAILURES_FILE,
        index=False,
    )

    # Cases where exact labels were right but the judge
    # still rejected the broader answer.
    reasoning_or_evidence_failures = df[
        (df["label_accuracy"] == 1.0)
        & (~df["correctness"])
    ]

    # -----------------------------------------------------
    # Label confusion analysis
   

    confusions = extract_label_confusions(df)

    if not confusions.empty:

        confusion_summary = (
            confusions.groupby(
                [
                    "expected_label",
                    "predicted_label",
                ]
            )
            .size()
            .reset_index(name="count")
            .sort_values(
                "count",
                ascending=False,
            )
        )

        confusion_summary.to_csv(
            CONFUSIONS_FILE,
            index=False,
        )

    else:

        confusion_summary = pd.DataFrame(
            columns=[
                "expected_label",
                "predicted_label",
                "count",
            ]
        )

    # -----------------------------------------------------
    # Terminal output
    

    print("\n=== Aggregate metrics ===")

    print(
        f"Mean label accuracy: "
        f"{mean_accuracy:.3f}"
    )

    print(
        f"Median label accuracy: "
        f"{median_accuracy:.3f}"
    )

    print(
        f"Perfect-label cases: "
        f"{perfect_label_cases}/{len(df)} "
        f"({perfect_label_rate:.1%})"
    )

    print(
        f"LLM-judge correctness: "
        f"{correctness_passes}/{len(df)} "
        f"({correctness_rate:.1%})"
    )

    print("\n=== Label accuracy distribution ===")

    print(distribution.to_string())

    print("\n=== Performance by category ===")

    print(
        category_summary.to_string(
            index=False
        )
    )

    print("\n=== Performance by difficulty ===")

    print(
        difficulty_summary.to_string(
            index=False
        )
    )

    print("\n=== Worst-performing cases ===")

    print(
        worst_cases[
            [
                "case_id",
                "category",
                "difficulty",
                "label_accuracy",
                "correctness",
            ]
        ].to_string(index=False)
    )

    print("\n=== Label confusions ===")

    if confusion_summary.empty:
        print("No label mismatches found.")
    else:
        print(
            confusion_summary.to_string(
                index=False
            )
        )

    # -----------------------------------------------------
    # Write Markdown analysis
    

    with open(
        ANALYSIS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "# Evaluation Analysis\n\n"
        )

        file.write(
            "## Aggregate Metrics\n\n"
        )

        file.write(
            f"- Mean label accuracy: "
            f"**{mean_accuracy:.3f}**\n"
        )

        file.write(
            f"- Median label accuracy: "
            f"**{median_accuracy:.3f}**\n"
        )

        file.write(
            f"- Perfect-label cases: "
            f"**{perfect_label_cases}/{len(df)} "
            f"({perfect_label_rate:.1%})**\n"
        )

        file.write(
            f"- LLM-judge correctness pass rate: "
            f"**{correctness_passes}/{len(df)} "
            f"({correctness_rate:.1%})**\n"
        )

        file.write(
            f"- Label accuracy range: "
            f"**{min_accuracy:.1f}–"
            f"{max_accuracy:.1f}**\n\n"
        )

        file.write(
            "## Performance by Category\n\n"
        )

        file.write(
            category_summary.to_markdown(
                index=False
            )
        )

        file.write("\n\n")

        file.write(
            "## Performance by Difficulty\n\n"
        )

        file.write(
            difficulty_summary.to_markdown(
                index=False
            )
        )

        file.write("\n\n")

        file.write(
            "## Label Confusions\n\n"
        )

        if confusion_summary.empty:

            file.write(
                "No label mismatches were found.\n"
            )

        else:

            file.write(
                confusion_summary.to_markdown(
                    index=False
                )
            )

        file.write("\n\n")

        file.write(
            "## Error Analysis\n\n"
        )

        file.write(
            f"- Cases with at least one evaluation "
            f"failure: **{len(failures)}/{len(df)}**.\n"
        )

        file.write(
            f"- Cases with perfect labels but failed "
            f"LLM-judge correctness: "
            f"**{len(reasoning_or_evidence_failures)}**.\n"
        )

        file.write(
            "- Detailed evaluator comments are stored "
            "in `failures.csv` for qualitative review.\n"
        )

    print("\nAnalysis complete.")

    print(
        f"Category summary: {CATEGORY_FILE}"
    )

    print(
        f"Difficulty summary: {DIFFICULTY_FILE}"
    )

    print(
        f"Failures: {FAILURES_FILE}"
    )

    print(
        f"Analysis summary: {ANALYSIS_FILE}"
    )


if __name__ == "__main__":
    main()