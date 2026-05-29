"""
Validation module for DataChat.
Provides validators for columns, operations, and data types.
"""
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from rapidfuzz import fuzz

# Column type categories
NUMERIC_TYPES = {"int64", "float64", "int32", "float32"}
DATETIME_TYPES = {"datetime64[ns]", "datetime64"}
CATEGORICAL_TYPES = {"object", "string", "category"}
FORECAST_KEYWORDS = {"predict", "prediction", "forecast", "future", "next", "estimate"}


def get_column_suggestions(
    missing_column: str, available_columns: List[str], top_n: int = 3
) -> List[str]:
    """
    Get fuzzy-matched column name suggestions.
    
    Args:
        missing_column: The column name that wasn't found
        available_columns: List of available column names
        top_n: Number of suggestions to return
    
    Returns:
        List of suggested column names, ordered by match quality
    """
    if not available_columns:
        return []
    
    scores = []
    for col in available_columns:
        # Use token_set_ratio for partial matches
        score = fuzz.token_set_ratio(missing_column.lower(), col.lower())
        scores.append((col, score))
    
    # Sort by score descending and return top matches with score > 50
    scores.sort(key=lambda x: x[1], reverse=True)
    suggestions = [col for col, score in scores if score > 50][:top_n]
    return suggestions


def is_forecast_request(question: str) -> bool:
    """Detect if a user question is asking for forecasting."""
    if not isinstance(question, str):
        return False

    normalized = question.lower()
    return any(keyword in normalized for keyword in FORECAST_KEYWORDS)


def find_schema_column_type(column_name: str, schema: List[Dict[str, Any]]) -> str:
    """Return the profile type for a schema column."""
    for col in schema:
        if col["name"] == column_name:
            return col.get("type", "unknown")
    return "unknown"


def schema_has_temporal_column(schema: List[Dict[str, Any]]) -> bool:
    """Return True if the schema contains at least one temporal column."""
    return any(col.get("type") == "datetime" for col in schema)


def is_temporal_column(df: pd.DataFrame, column_name: str) -> bool:
    """Detect whether a DataFrame column contains temporal values."""
    if column_name not in df.columns:
        return False

    if pd.api.types.is_datetime64_any_dtype(df[column_name]):
        return True

    if pd.api.types.is_string_dtype(df[column_name]) or pd.api.types.is_object_dtype(df[column_name]):
        parsed = pd.to_datetime(df[column_name], errors="coerce")
        non_null = parsed.notna().sum()
        total = df[column_name].dropna().shape[0]
        return total > 0 and non_null >= max(1, total // 2)

    return False


def validate_column_exists(
    column_name: str, available_columns: List[str]
) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate if a column exists in the dataset.
    
    Returns:
        (exists: bool, corrected_name: Optional[str], suggestions: List[str])
    """
    if column_name in available_columns:
        return True, column_name, []
    
    # Try case-insensitive match
    lower_to_actual = {col.lower(): col for col in available_columns}
    if column_name.lower() in lower_to_actual:
        return True, lower_to_actual[column_name.lower()], []
    
    # Get fuzzy suggestions
    suggestions = get_column_suggestions(column_name, available_columns)
    return False, None, suggestions


def get_column_type(df: pd.DataFrame, column_name: str) -> str:
    """Get the category of column type."""
    dtype_str = str(df[column_name].dtype)
    
    if dtype_str in NUMERIC_TYPES:
        return "numeric"
    if dtype_str in DATETIME_TYPES or pd.api.types.is_datetime64_any_dtype(df[column_name]):
        return "datetime"
    if dtype_str in CATEGORICAL_TYPES:
        return "categorical"
    
    return "unknown"


def validate_operation_compatibility(
    operation: str, df: pd.DataFrame, column_name: Optional[str] = None,
    x_column: Optional[str] = None, y_column: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate if an operation is compatible with the provided columns.
    
    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    if operation == "histogram":
        if not column_name:
            return False, "histogram requires a column"
        
        col_type = get_column_type(df, column_name)
        if col_type != "numeric":
            return False, (
                f"Histogram requires a numeric column, but '{column_name}' is {col_type}. "
                f"Try selecting a numeric column instead."
            )
        
        # Check if column has any numeric values
        numeric_values = pd.to_numeric(df[column_name], errors="coerce").dropna()
        if numeric_values.empty:
            return False, (
                f"Column '{column_name}' has no numeric values. "
                f"Histogram requires at least some numeric data."
            )
    
    elif operation == "trend":
        if not x_column or not y_column:
            return False, "trend requires both x_column and y_column"

        # Dataset must contain a temporal column for trend analysis.
        temporal_columns = [col for col in df.columns if is_temporal_column(df, col)]
        if not temporal_columns:
            return False, (
                "Trend analysis requires a temporal column (date/time), but none was detected in this dataset."
            )

        if not is_temporal_column(df, x_column):
            return False, (
                f"Trend analysis requires a temporal x-axis column, "
                f"but '{x_column}' is not temporal. "
                f"Select a date/time column for trend analysis."
            )

        y_type = get_column_type(df, y_column)
        if y_type != "numeric":
            return False, (
                f"Trend requires a numeric column for the y-axis, "
                f"but '{y_column}' is {y_type}. "
                f"Try selecting a numeric column."
            )

        numeric_values = pd.to_numeric(df[y_column], errors="coerce").dropna()
        if numeric_values.empty:
            return False, (
                f"Column '{y_column}' has no numeric values. "
                f"Trend requires at least some numeric data."
            )
    
    elif operation == "correlation":
        # Need at least 2 numeric columns
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) < 2:
            return False, (
                f"Correlation requires at least 2 numeric columns, "
                f"but only {len(numeric_cols)} found. "
                f"Your dataset needs more numeric columns for correlation analysis."
            )
    
    elif operation == "groupby":
        if not x_column or not y_column:
            return False, "groupby requires both target_column and group_column"
        
        # target_column should be numeric (for aggregation)
        y_type = get_column_type(df, y_column)
        if y_type != "numeric":
            return False, (
                f"GroupBy aggregation requires a numeric column, "
                f"but '{y_column}' is {y_type}. "
                f"Try selecting a numeric column for aggregation."
            )
    
    return True, None


def validate_csv_data(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validate CSV data.
    
    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    if df.empty:
        return False, "CSV file is empty. Please upload a file with data."
    
    if len(df.columns) == 0:
        return False, "CSV file has no columns. Please check your file format."
    
    # Check if all rows are NaN
    if df.isna().all(axis=None):
        return False, "CSV file contains only missing values. Please check your data."
    
    return True, None


def get_error_response(
    message: str, suggestions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a structured error response.
    
    Returns:
        Dictionary with error, message, and optional suggestions
    """
    response = {
        "error": True,
        "message": message,
    }
    
    if suggestions:
        response["suggestions"] = suggestions
    
    return response
