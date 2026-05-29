from typing import Any, Dict

import pandas as pd


def run_summary(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = [col for col in df.columns if col not in numeric_columns]

    return {
        "operation": "summary",
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
    }
