from typing import Any, Dict

import numpy as np
import pandas as pd

from app.utils.validator import get_error_response


def run_histogram(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Generate histogram data for a numeric column.
    
    Returns:
        Dictionary with histogram data or error information.
    """
    if column not in df.columns:
        return get_error_response(
            f"Column '{column}' not found in dataset",
            [col for col in df.columns.tolist()[:5]]
        )

    values = pd.to_numeric(df[column], errors="coerce").dropna()
    if values.empty:
        return get_error_response(
            f"Column '{column}' has no numeric values. Histogram requires numeric data.",
            [col for col in df.select_dtypes(include='number').columns.tolist()[:5]]
        )

    bin_count = min(10, max(1, int(values.nunique())))
    counts, bins = np.histogram(values, bins=bin_count)

    return {
        "operation": "histogram",
        "column": column,
        "bins": [float(value) for value in bins.tolist()],
        "counts": [int(value) for value in counts.tolist()],
        "mean": float(values.mean()),
        "median": float(values.median()),
    }
