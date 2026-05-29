from typing import Any, Dict


def _format_number(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, int):
        return str(value)
    return "N/A"


def generate_explanation(operation: str, result: Dict[str, Any]) -> str:
    if operation == "summary":
        rows = result.get("rows", 0)
        columns = result.get("columns", 0)
        numeric_count = len(result.get("numeric_columns", []))
        categorical_count = len(result.get("categorical_columns", []))
        return (
            f"This dataset has {rows} rows and {columns} columns. "
            f"It includes {numeric_count} numeric columns and "
            f"{categorical_count} categorical or text columns."
        )

    if operation == "histogram":
        column = result.get("column", "the selected column")
        mean = _format_number(result.get("mean"))
        median = _format_number(result.get("median"))
        bins = result.get("bins", [])
        spread = "N/A"
        if len(bins) >= 2:
            spread = f"{_format_number(bins[0])} to {_format_number(bins[-1])}"

        return (
            f"The histogram for {column} shows values spread from {spread}. "
            f"The mean is {mean} and the median is {median}, which helps compare "
            "the center of the distribution with the typical middle value."
        )

    if operation == "missing":
        missing = result.get("missing", {})
        total_missing = sum(value for value in missing.values() if isinstance(value, int))
        affected_columns = sum(1 for value in missing.values() if isinstance(value, int) and value > 0)
        if total_missing == 0:
            return "No missing values were found in the dataset columns."

        return (
            f"The dataset contains {total_missing} missing values across "
            f"{affected_columns} columns. Columns with missing values may need cleaning "
            "before deeper analysis."
        )

    if operation == "groupby":
        results = result.get("results", [])
        aggregation = result.get("aggregation", "aggregation")
        target_column = result.get("target_column", "target")
        group_column = result.get("group_column", "group")
        valid_results = [
            item for item in results
            if isinstance(item, dict) and isinstance(item.get("value"), (int, float))
        ]

        if not valid_results:
            return (
                f"The grouped {aggregation} of {target_column} by {group_column} "
                "did not produce numeric comparison values."
            )

        highest = max(valid_results, key=lambda item: item["value"])
        lowest = min(valid_results, key=lambda item: item["value"])
        return (
            f"The {aggregation} of {target_column} varies by {group_column}. "
            f"The highest group is {highest.get('group')} at {_format_number(highest.get('value'))}, "
            f"while the lowest is {lowest.get('group')} at {_format_number(lowest.get('value'))}."
        )

    if operation == "correlation":
        value = result.get("value")
        if not isinstance(value, (int, float)):
            return "A correlation value could not be calculated for the numeric columns."

        strength = "weak"
        absolute_value = abs(value)
        if absolute_value >= 0.7:
            strength = "strong"
        elif absolute_value >= 0.3:
            strength = "moderate"

        direction = "positive" if value >= 0 else "negative"
        return (
            f"The correlation is {_format_number(value)}, indicating a {strength} "
            f"{direction} relationship between the selected numeric columns."
        )

    if operation == "trend":
        x_values = result.get("x_values", [])
        y_values = result.get("y_values", [])
        y_column = result.get("y_column", "value")
        x_column = result.get("x_column", "time")

        if len(y_values) < 2:
            return f"The trend for {y_column} over {x_column} has limited data points."

        start = y_values[0]
        end = y_values[-1]
        direction = "increased" if end > start else "decreased" if end < start else "stayed flat"
        return (
            f"The trend shows {y_column} {direction} from {_format_number(start)} "
            f"to {_format_number(end)} across {len(x_values)} ordered {x_column} values."
        )

    return "DataChat completed the requested analysis."
