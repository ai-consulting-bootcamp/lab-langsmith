"""Summarize offline validation or a raw LangSmith export."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def main() -> None:
    live_path = DATA_DIR / "langsmith_evaluation_results_raw.csv"
    offline_path = DATA_DIR / "offline_validation_results.csv"
    path = live_path if live_path.exists() else offline_path
    frame = pd.read_csv(path)
    feedback_columns = [
        column
        for column in frame.columns
        if column.startswith("feedback.")
        or column in {"strategy_exact_match", "format_compliance"}
    ]
    if not feedback_columns:
        raise ValueError("No recognized evaluation score columns were found.")

    print(f"Source: {path.name}")
    print(f"Rows: {len(frame)}")
    for column in feedback_columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            print(f"{column}: mean={values.mean():.3f}, min={values.min():.3f}, max={values.max():.3f}")

    if "category" in frame.columns and "strategy_exact_match" in frame.columns:
        print("\nAccuracy by category:")
        print(frame.groupby("category")["strategy_exact_match"].mean().to_string())


if __name__ == "__main__":
    main()

