from typing import Any, Dict

import pandas as pd


def run_missing(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "operation": "missing",
        "missing": {
            column: int(count)
            for column, count in df.isna().sum().to_dict().items()
        },
    }
