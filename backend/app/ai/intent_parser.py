import json
import os
from typing import Any, Dict, List

from openai import OpenAI


SUPPORTED_OPERATIONS = ("summary", "histogram", "groupby", "correlation", "missing", "trend")
ALLOWED_AGGREGATIONS = ("sum", "mean", "count", "max", "min")
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
SYSTEM_PROMPT = "You are a data analysis intent parser. Return only valid JSON."
UNSUPPORTED_KEYWORDS = {
    "forecast",
    "predict",
    "prediction",
    "future",
    "next",
    "estimate",
    "scatter",
    "scatterplot",
    "scatter plot",
    "boxplot",
    "box plot",
    "pie",
    "pie chart",
    "heatmap",
    "violin",
    "density plot",
}
UNSUPPORTED_SUGGESTIONS = [
    "Show histogram of marks",
    "Average marks by class",
    "Show missing values",
]
EXPECTED_KEYS = {
    "summary": {"operation"},
    "histogram": {"operation", "column"},
    "groupby": {"operation", "target_column", "group_column", "aggregation"},
    "correlation": {"operation"},
    "missing": {"operation"},
    "trend": {"operation", "x_column", "y_column"},
}


def unsupported_operation_error() -> Dict[str, Any]:
    return {
        "error": True,
        "message": "This analysis type is not supported in the current MVP.",
        "suggestions": UNSUPPORTED_SUGGESTIONS,
    }


def detect_unsupported_query(question: str):
    q = question.lower()

    for keyword in sorted(UNSUPPORTED_KEYWORDS, key=len, reverse=True):
        if keyword in q:
            return {
                "error": True,
                "message": f'The requested analysis "{keyword}" is not supported in this MVP yet.',
                "suggestions": [
                    "Show histogram of marks",
                    "Average marks by class",
                    "Show missing values",
                    "Summarize this dataset",
                ],
            }

    return None


def call_groq(prompt: str, api_key: str) -> str:
    """Call Groq's OpenAI-compatible API and return the generated text."""
    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)

    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
    except Exception as exc:
        raise ValueError(f"Groq API error: {str(exc)}") from exc

    try:
        return response.choices[0].message.content or ""
    except (AttributeError, IndexError, TypeError) as exc:
        raise ValueError("Groq response did not include generated text") from exc


def format_schema_for_prompt(schema: List[Dict[str, Any]]) -> str:
    """Format the dataset schema for the prompt."""
    schema_text = "Dataset Schema:\n"
    for col in schema:
        sample_values = ", ".join(str(value) for value in col.get("sample_values", []))
        schema_text += (
            f"- {col['name']} ({col['type']}): "
            f"{col['unique_count']} unique values, "
            f"{col['missing_count']} missing"
        )
        if sample_values:
            schema_text += f", samples: {sample_values}"
        schema_text += "\n"
    return schema_text


def construct_prompt(question: str, schema: List[Dict[str, Any]]) -> str:
    """Construct the prompt for the LLM with schema context."""
    schema_context = format_schema_for_prompt(schema)
    operations_str = ", ".join(SUPPORTED_OPERATIONS)
    column_names = ", ".join(col["name"] for col in schema)

    prompt = f"""You are a data analysis intent parser.

{schema_context}
Available columns: {column_names}

Supported operations: {operations_str}

User question: "{question}"

You must ONLY return one of these operations:

- summary
- histogram
- groupby
- correlation
- missing
- trend

If the request asks for ANY unsupported analysis
(forecasting, prediction, scatter plots, box plots, pie charts, heatmaps, etc.)

Return EXACTLY:

{{"operation":"unsupported"}}

Do NOT map unsupported requests to another supported operation.
Do NOT guess.
Return strict JSON only.

Return ONLY one valid JSON object matching one of these exact formats:

For "summary" operation:
{{"operation": "summary"}}

For "histogram" operation:
{{"operation": "histogram", "column": "column_name"}}

For "groupby" operation:
{{"operation": "groupby", "target_column": "column_name", "group_column": "group_column_name", "aggregation": "sum|mean|count|max|min"}}

For "correlation" operation:
{{"operation": "correlation"}}

For "missing" operation:
{{"operation": "missing"}}

For "trend" operation:
{{"operation": "trend", "x_column": "time_column", "y_column": "value_column"}}

Rules:
- Use only the supported operations.
- Use only columns from the available columns list.
- Do not include extra fields.
- Return JSON only, with no markdown, no explanation, and no surrounding text."""

    return prompt


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Safely parse the LLM's JSON-only response."""
    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```"):
        lines = cleaned_text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].strip() == "```":
            cleaned_text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response was not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError("LLM response must be a JSON object")

    return parsed


def normalize_column_name(column_name: Any, schema: List[Dict[str, Any]]) -> str:
    """Validate a column against the uploaded schema and preserve schema casing."""
    if not isinstance(column_name, str) or not column_name.strip():
        raise ValueError("Column values must be non-empty strings")

    schema_columns = [col["name"] for col in schema]
    stripped_name = column_name.strip()

    if stripped_name in schema_columns:
        return stripped_name

    lower_to_actual = {col.lower(): col for col in schema_columns}
    matched_column = lower_to_actual.get(stripped_name.lower())
    if matched_column:
        return matched_column

    raise ValueError(f"Unknown column: {column_name}")


def validate_operation(operation_dict: Dict[str, Any], schema: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate and return a clean operation object."""
    operation_type = operation_dict.get("operation")

    if operation_type == "unsupported":
        return unsupported_operation_error()

    if operation_type not in SUPPORTED_OPERATIONS:
        raise ValueError(f"Unsupported operation: {operation_type}")

    expected_keys = EXPECTED_KEYS[operation_type]
    actual_keys = set(operation_dict.keys())
    if actual_keys != expected_keys:
        raise ValueError(f"Invalid fields for {operation_type}: {sorted(actual_keys)}")

    if operation_type == "histogram":
        return {
            "operation": "histogram",
            "column": normalize_column_name(operation_dict["column"], schema),
        }

    if operation_type == "groupby":
        aggregation = operation_dict["aggregation"]
        if not isinstance(aggregation, str) or aggregation.lower() not in ALLOWED_AGGREGATIONS:
            raise ValueError(f"Unsupported aggregation: {aggregation}")

        return {
            "operation": "groupby",
            "target_column": normalize_column_name(operation_dict["target_column"], schema),
            "group_column": normalize_column_name(operation_dict["group_column"], schema),
            "aggregation": aggregation.lower(),
        }

    if operation_type == "trend":
        return {
            "operation": "trend",
            "x_column": normalize_column_name(operation_dict["x_column"], schema),
            "y_column": normalize_column_name(operation_dict["y_column"], schema),
        }

    return {"operation": operation_type}


def parse_query(question: str, schema: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse a natural language query using Groq API.

    Args:
        question: User's natural language question.
        schema: List of column schema dictionaries.

    Returns:
        Dictionary with parsed intent or error information.
    """
    unsupported = detect_unsupported_query(question)
    if unsupported:
        return unsupported

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "Groq API key not configured"}

    try:
        prompt = construct_prompt(question, schema)

        response_text = call_groq(prompt, api_key)

        if not response_text:
            return {"error": "No response from Groq API"}

        parsed_operation = parse_llm_response(response_text)
        return validate_operation(parsed_operation, schema)

    except Exception as e:
        return {"error": f"Error parsing query: {str(e)}"}
