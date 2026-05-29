"""
Direct unit tests for validation module
"""
import sys
sys.path.insert(0, "d:\\Data Sciece Mastery\\Data analytics AI\\datachat\\backend")

import pandas as pd
from app.utils.validator import (
    get_column_suggestions,
    validate_column_exists,
    get_column_type,
    validate_operation_compatibility,
    validate_csv_data,
    get_error_response
)

def test_fuzzy_column_matching():
    """Test fuzzy column name matching"""
    print("\n" + "=" * 70)
    print("Test 1: Fuzzy Column Name Matching")
    print("=" * 70)
    
    available = ["name", "marks", "class", "date"]
    
    # Test 1: Exact match
    exists, corrected, suggestions = validate_column_exists("marks", available)
    print(f"'marks' exists: {exists}, corrected: {corrected}")
    assert exists and corrected == "marks"
    
    # Test 2: Case-insensitive match
    exists, corrected, suggestions = validate_column_exists("MARKS", available)
    print(f"'MARKS' exists: {exists}, corrected: {corrected}")
    assert exists and corrected == "marks"
    
    # Test 3: Fuzzy match (close but not exact)
    exists, corrected, suggestions = validate_column_exists("mark", available)
    print(f"'mark' exists: {exists}, suggestions: {suggestions}")
    assert not exists and "marks" in suggestions
    
    # Test 4: Complete mismatch
    exists, corrected, suggestions = validate_column_exists("xyz", available)
    print(f"'xyz' exists: {exists}, suggestions: {suggestions}")
    assert not exists
    
    print("✅ All fuzzy matching tests passed")

def test_column_type_detection():
    """Test column type detection"""
    print("\n" + "=" * 70)
    print("Test 2: Column Type Detection")
    print("=" * 70)
    
    df = pd.DataFrame({
        "numeric": [1, 2, 3],
        "text": ["a", "b", "c"],
        "float": [1.5, 2.5, 3.5]
    })
    
    print(f"numeric type: {get_column_type(df, 'numeric')}")
    print(f"text type: {get_column_type(df, 'text')}")
    print(f"float type: {get_column_type(df, 'float')}")
    
    assert get_column_type(df, "numeric") == "numeric"
    assert get_column_type(df, "text") == "categorical"
    assert get_column_type(df, "float") == "numeric"
    
    print("✅ All column type detection tests passed")

def test_operation_compatibility():
    """Test operation compatibility validation"""
    print("\n" + "=" * 70)
    print("Test 3: Operation Compatibility Validation")
    print("=" * 70)
    
    df = pd.DataFrame({
        "marks": [85, 90, 75],
        "name": ["Alice", "Bob", "Charlie"],
        "class": ["A", "B", "A"]
    })
    
    # Test 1: Histogram with numeric column (valid)
    valid, msg = validate_operation_compatibility("histogram", df, column_name="marks")
    print(f"Histogram on 'marks': valid={valid}")
    assert valid
    
    # Test 2: Histogram with non-numeric column (invalid)
    valid, msg = validate_operation_compatibility("histogram", df, column_name="name")
    print(f"Histogram on 'name': valid={valid}, message: {msg[:60]}...")
    assert not valid and "numeric" in msg
    
    # Test 3: Correlation with insufficient numeric columns
    valid, msg = validate_operation_compatibility("correlation", df)
    print(f"Correlation: valid={valid}, message: {msg[:80] if msg else 'N/A'}...")
    # Only marks is numeric, so should fail
    assert not valid
    
    # Test 4: GroupBy with numeric target column (valid if we add more numeric columns)
    df_with_numbers = df.copy()
    df_with_numbers["score"] = [100, 95, 85]
    valid, msg = validate_operation_compatibility("groupby", df_with_numbers, x_column="class", y_column="score")
    print(f"GroupBy on numeric: valid={valid}")
    assert valid
    
    # Test 5: GroupBy with non-numeric target column (invalid)
    valid, msg = validate_operation_compatibility("groupby", df, x_column="class", y_column="name")
    print(f"GroupBy on non-numeric: valid={valid}, message: {msg[:60]}...")
    assert not valid
    
    print("✅ All operation compatibility tests passed")

def test_csv_validation():
    """Test CSV data validation"""
    print("\n" + "=" * 70)
    print("Test 4: CSV Data Validation")
    print("=" * 70)
    
    # Test 1: Valid CSV
    df_valid = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    valid, msg = validate_csv_data(df_valid)
    print(f"Valid CSV: valid={valid}")
    assert valid
    
    # Test 2: Empty CSV
    df_empty = pd.DataFrame()
    valid, msg = validate_csv_data(df_empty)
    print(f"Empty CSV: valid={valid}, message: {msg}")
    assert not valid and "empty" in msg
    
    # Test 3: CSV with all NaN
    df_nan = pd.DataFrame({"a": [None, None], "b": [None, None]})
    valid, msg = validate_csv_data(df_nan)
    print(f"All NaN CSV: valid={valid}, message: {msg}")
    assert not valid
    
    print("✅ All CSV validation tests passed")

def test_error_response_format():
    """Test error response formatting"""
    print("\n" + "=" * 70)
    print("Test 5: Error Response Format")
    print("=" * 70)
    
    # Test 1: Error with suggestions
    error = get_error_response("Column not found", ["col1", "col2"])
    print(f"Error with suggestions: {error}")
    assert error["error"] == True
    assert error["message"] == "Column not found"
    assert error["suggestions"] == ["col1", "col2"]
    
    # Test 2: Error without suggestions
    error = get_error_response("Something went wrong")
    print(f"Error without suggestions: {error}")
    assert error["error"] == True
    assert "suggestions" not in error or error.get("suggestions") is None
    
    print("✅ All error response tests passed")

def main():
    print("\n" + "*" * 70)
    print("*  Direct Unit Tests for Validation Module  *")
    print("*" * 70)
    
    try:
        test_fuzzy_column_matching()
        test_column_type_detection()
        test_operation_compatibility()
        test_csv_validation()
        test_error_response_format()
        
        print("\n" + "*" * 70)
        print("*  ✅ All unit tests passed!  *")
        print("*" * 70 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
