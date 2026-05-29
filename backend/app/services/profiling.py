import pandas as pd
import numpy as np
from datetime import datetime


def detect_column_type(series: pd.Series) -> str:
    """
    Detect the data type of a pandas Series.
    Returns: 'numeric', 'categorical', 'datetime', 'text'
    """
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    
    # Try to detect if it should be categorical (low cardinality relative to length)
    unique_count = series.nunique()
    total_count = len(series) - series.isna().sum()
    
    if total_count > 0 and unique_count / total_count < 0.05:
        return "categorical"
    
    return "text"


def get_sample_values(series: pd.Series, n: int = 3) -> list:
    """
    Get first n unique non-null values from a series.
    """
    non_null = series.dropna()
    unique_vals = non_null.unique()
    
    # Convert numpy types to Python types for JSON serialization
    samples = []
    for val in unique_vals[:n]:
        if isinstance(val, (np.integer, np.floating)):
            samples.append(float(val) if isinstance(val, np.floating) else int(val))
        elif isinstance(val, np.bool_):
            samples.append(bool(val))
        else:
            samples.append(str(val))
    
    return samples


def profile_column(series: pd.Series) -> dict:
    """
    Profile a single column and return its analysis.
    """
    col_type = detect_column_type(series)
    missing_count = int(series.isna().sum())
    unique_count = int(series.nunique())
    sample_values = get_sample_values(series, n=3)
    
    profile = {
        "name": series.name,
        "type": col_type,
        "missing_count": missing_count,
        "unique_count": unique_count,
        "sample_values": sample_values,
    }
    
    # Add numeric statistics if applicable
    if col_type == "numeric":
        numeric_series = pd.to_numeric(series, errors="coerce")
        profile["stats"] = {
            "min": float(numeric_series.min()),
            "max": float(numeric_series.max()),
            "mean": float(numeric_series.mean()),
        }
    
    return profile


def profile_dataset(df: pd.DataFrame) -> list:
    """
    Profile all columns in a dataframe.
    Returns a list of column profiles.
    """
    schema = []
    for col in df.columns:
        profile = profile_column(df[col])
        schema.append(profile)
    
    return schema
