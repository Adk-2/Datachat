from typing import Any, Dict

import pandas as pd

from app.utils.validator import get_error_response


def run_groupby(
    df: pd.DataFrame,
    target_column: str,
    group_column: str,
    aggregation: str,
) -> Dict[str, Any]:
    """
    Group by a column and aggregate target column.
    
    Returns:
        Dictionary with groupby results or error information.
    """
    if target_column not in df.columns:
        return get_error_response(
            f"Column '{target_column}' not found in dataset",
            [col for col in df.columns.tolist()[:5]]
        )
    if group_column not in df.columns:
        return get_error_response(
            f"Column '{group_column}' not found in dataset",
            [col for col in df.columns.tolist()[:5]]
        )

    if aggregation not in {"sum", "mean", "count", "max", "min"}:
        return get_error_response(
            f"Unsupported aggregation: {aggregation}",
            ["sum", "mean", "count", "max", "min"]
        )

    working_df = df[[group_column, target_column]].copy()
    if aggregation != "count":
        working_df[target_column] = pd.to_numeric(working_df[target_column], errors="coerce")

    grouped = (
        working_df.groupby(group_column, dropna=False)[target_column]
        .agg(aggregation)
        .reset_index(name="value")
    )

    if grouped.empty:
        return get_error_response(
            f"No results after grouping by '{group_column}'. Check your data.",
            ["Show summary instead", "Show missing values", "Try different columns"]
        )

    results = []
    for row in grouped.to_dict(orient="records"):
        value = row["value"]
        if pd.isna(value):
            clean_value = None
        elif isinstance(value, float):
            clean_value = float(value)
        else:
            clean_value = int(value) if isinstance(value, int) else value

        group_value = row[group_column]
        results.append(
            {
                "group": None if pd.isna(group_value) else group_value,
                "value": clean_value,
            }
        )

    return {
        "operation": "groupby",
        "target_column": target_column,
        "group_column": group_column,
        "aggregation": aggregation,
        "results": results,
    }
