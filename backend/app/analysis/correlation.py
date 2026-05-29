from typing import Any, Dict

import pandas as pd

from app.utils.validator import get_error_response


def run_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate correlation between the first two numeric columns.
    
    Returns:
        Dictionary with correlation data or error information.
    """
    numeric_df = df.select_dtypes(include="number")
    numeric_columns = numeric_df.columns.tolist()

    if len(numeric_columns) < 2:
        return get_error_response(
            f"Correlation requires at least 2 numeric columns, but only {len(numeric_columns)} found. "
            f"Your dataset needs more numeric columns for correlation analysis.",
            ["Show summary instead", "Show missing values", "Upload a dataset with more numeric columns"]
        )

    x_column = numeric_columns[0]
    y_column = numeric_columns[1]
    value = numeric_df[x_column].corr(numeric_df[y_column])

    return {
        "operation": "correlation",
        "x_column": x_column,
        "y_column": y_column,
        "value": None if pd.isna(value) else float(value),
    }
