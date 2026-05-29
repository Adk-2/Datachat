from typing import Any, Dict

import pandas as pd

from app.analysis.correlation import run_correlation
from app.analysis.groupby import run_groupby
from app.analysis.histogram import run_histogram
from app.analysis.missing import run_missing
from app.analysis.summary import run_summary
from app.analysis.trend import run_trend
from app.utils.validator import validate_operation_compatibility, get_error_response


def execute_analysis(intent: Dict[str, Any], dataframe: pd.DataFrame) -> Dict[str, Any]:
    """
    Execute analysis based on intent.
    
    Returns:
        Dictionary with either result data or error information.
    """
    operation = intent.get("operation")

    if operation == "summary":
        return run_summary(dataframe)

    if operation == "histogram":
        column = intent.get("column")
        # Validate before execution
        is_valid, error_msg = validate_operation_compatibility(operation, dataframe, column_name=column)
        if not is_valid:
            return get_error_response(error_msg, [
                "Show summary instead",
                "Show missing values",
                "Show histogram of different column"
            ])
        return run_histogram(dataframe, column)

    if operation == "groupby":
        target_column = intent.get("target_column")
        group_column = intent.get("group_column")
        aggregation = intent.get("aggregation")
        # Validate before execution
        is_valid, error_msg = validate_operation_compatibility(
            operation, dataframe, x_column=group_column, y_column=target_column
        )
        if not is_valid:
            return get_error_response(error_msg, [
                "Show summary instead",
                "Group by different columns",
                "Show missing values"
            ])
        return run_groupby(dataframe, target_column, group_column, aggregation)

    if operation == "correlation":
        # Validate before execution
        is_valid, error_msg = validate_operation_compatibility(operation, dataframe)
        if not is_valid:
            return get_error_response(error_msg, [
                "Show summary instead",
                "Show missing values",
                "Upload a dataset with numeric columns"
            ])
        return run_correlation(dataframe)

    if operation == "missing":
        return run_missing(dataframe)

    if operation == "trend":
        x_column = intent.get("x_column")
        y_column = intent.get("y_column")
        # Validate before execution
        is_valid, error_msg = validate_operation_compatibility(
            operation, dataframe, x_column=x_column, y_column=y_column
        )
        if not is_valid:
            return get_error_response(error_msg, [
                "Show summary instead",
                "Show histogram instead",
                "Show missing values"
            ])
        return run_trend(dataframe, x_column, y_column)

    return get_error_response(
        f"Unsupported operation: {operation}",
        ["summary", "histogram", "groupby", "correlation", "missing", "trend"]
    )
