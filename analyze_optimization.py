from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths


BASE_DIR = Path(__file__).resolve().parent

RESULTS_FILE = (
    BASE_DIR
    / "results"
    / "optimization_results.csv"
)

SUMMARY_FILE = (
    BASE_DIR
    / "results"
    / "optimization_summary.csv"
)

CASE_COMPARISON_FILE = (
    BASE_DIR
    / "results"
    / "optimization_case_comparison.csv"
)


# ---------------------------------------------------------
# Helpers


def normalize_boolean(value):
    """
    Convert correctness values safely to booleans.
    """

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() == "true"


# ---------------------------------------------------------
# Main


def main():

    print("Loading optimization results...")

    df = pd.read_csv(RESULTS_FILE)

    expected_rows = 30

    if len(df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows "
            f"(15 examples x 2 models), "
            f"found {len(df)}."
        )

    df["correctness"] = (
        df["correctness"]
        .apply(normalize_boolean)
    )

    # -----------------------------------------------------
    # Aggregate model metrics
    

    summary = (
        df.groupby("model")
        .agg(
            examples=(
                "case_id",
                "count",
            ),

            mean_label_accuracy=(
                "label_accuracy",
                "mean",
            ),

            median_label_accuracy=(
                "label_accuracy",
                "median",
            ),

            fully_correct_cases=(
                "correctness",
                "sum",
            ),

            correctness_rate=(
                "correctness",
                "mean",
            ),

            total_input_tokens=(
                "input_tokens",
                "sum",
            ),

            total_output_tokens=(
                "output_tokens",
                "sum",
            ),

            total_tokens=(
                "total_tokens",
                "sum",
            ),

            total_cost_usd=(
                "estimated_cost_usd",
                "sum",
            ),

            mean_cost_per_example_usd=(
                "estimated_cost_usd",
                "mean",
            ),

            mean_latency_seconds=(
                "latency_seconds",
                "mean",
            ),

            median_latency_seconds=(
                "latency_seconds",
                "median",
            ),
        )
        .reset_index()
    )

    # -----------------------------------------------------
    # Cost per fully correct response
    # -----------------------------------------------------

    summary["cost_per_correct_case_usd"] = (
        summary["total_cost_usd"]
        /
        summary["fully_correct_cases"]
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False,
    )

    # -----------------------------------------------------
    # Case-by-case comparison
    

    comparison = df.pivot(
        index="case_id",
        columns="model",
        values="label_accuracy",
    ).reset_index()

    comparison["difference_gpt4.1_minus_mini"] = (
        comparison["gpt-4.1"]
        - comparison["gpt-4o-mini"]
    )

    comparison["winner"] = comparison[
        "difference_gpt4.1_minus_mini"
    ].apply(
        lambda difference:
            "gpt-4.1"
            if difference > 0
            else (
                "gpt-4o-mini"
                if difference < 0
                else "tie"
            )
    )

    comparison.to_csv(
        CASE_COMPARISON_FILE,
        index=False,
    )

    # -----------------------------------------------------
    # Extract model rows
   

    mini = summary[
        summary["model"] == "gpt-4o-mini"
    ].iloc[0]

    strong = summary[
        summary["model"] == "gpt-4.1"
    ].iloc[0]

    accuracy_gain = (
        strong["mean_label_accuracy"]
        - mini["mean_label_accuracy"]
    )

    correctness_gain = (
        strong["correctness_rate"]
        - mini["correctness_rate"]
    )

    cost_multiplier = (
        strong["total_cost_usd"]
        / mini["total_cost_usd"]
    )

    latency_difference = (
        strong["mean_latency_seconds"]
        - mini["mean_latency_seconds"]
    )

    gpt41_wins = (
        comparison["winner"]
        == "gpt-4.1"
    ).sum()

    mini_wins = (
        comparison["winner"]
        == "gpt-4o-mini"
    ).sum()

    ties = (
        comparison["winner"]
        == "tie"
    ).sum()

    # -----------------------------------------------------
    # Terminal output
    

    print("\n=== Model Summary ===")

    display_columns = [
        "model",
        "mean_label_accuracy",
        "correctness_rate",
        "total_cost_usd",
        "mean_cost_per_example_usd",
        "cost_per_correct_case_usd",
        "mean_latency_seconds",
    ]

    print(
        summary[
            display_columns
        ].to_string(
            index=False
        )
    )

    print("\n=== Performance Difference ===")

    print(
        f"Mean label accuracy gain "
        f"(gpt-4.1 - mini): "
        f"{accuracy_gain:+.3f}"
    )

    print(
        f"Correctness-rate gain: "
        f"{correctness_gain:+.1%}"
    )

    print(
        f"Cost multiplier: "
        f"{cost_multiplier:.1f}x"
    )

    print(
        f"Mean latency difference: "
        f"{latency_difference:+.3f} seconds"
    )

    print("\n=== Case-Level Wins ===")

    print(
        f"gpt-4.1 better: {gpt41_wins}"
    )

    print(
        f"gpt-4o-mini better: {mini_wins}"
    )

    print(
        f"Ties: {ties}"
    )

    print("\n=== Case Comparison ===")

    print(
        comparison.to_string(
            index=False
        )
    )

    print("\nAnalysis complete.")

    print(
        f"Summary saved to: "
        f"{SUMMARY_FILE}"
    )

    print(
        f"Case comparison saved to: "
        f"{CASE_COMPARISON_FILE}"
    )


if __name__ == "__main__":
    main()