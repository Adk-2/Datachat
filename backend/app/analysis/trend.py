from typing import Any, Dict

import pandas as pd

from app.utils.validator import get_error_response


def run_trend(df: pd.DataFrame, x_column: str, y_column: str) -> Dict[str, Any]:
    """
    Calculate trend data for x and y columns.
    
    Returns:
        Dictionary with trend data or error information.
    """
    if x_column not in df.columns:
        return get_error_response(
            f"Column '{x_column}' not found in dataset",
            [col for col in df.columns.tolist()[:5]]
        )
    if y_column not in df.columns:
        return get_error_response(
            f"Column '{y_column}' not found in dataset",
            [col for col in df.columns.tolist()[:5]]
        )

    working_df = df[[x_column, y_column]].dropna().copy()
    working_df[y_column] = pd.to_numeric(working_df[y_column], errors="coerce")
    working_df = working_df.dropna(subset=[y_column])

    if working_df.empty:
        return get_error_response(
            f"Trend analysis requires at least one valid data point with numeric values in '{y_column}'. "
            f"No valid data points found after removing missing values.",
            ["Show summary instead", "Show histogram instead", "Check missing values"]
        )

    sort_values = pd.to_datetime(working_df[x_column], errors="coerce")
    if sort_values.notna().any():
        working_df = working_df.assign(_sort_key=sort_values).sort_values("_sort_key")
    else:
        working_df = working_df.sort_values(x_column)

    return {
        "operation": "trend",
        "x_column": x_column,
        "y_column": y_column,
        "x_values": [str(value) for value in working_df[x_column].tolist()],
        "y_values": [float(value) for value in working_df[y_column].tolist()],
    }
