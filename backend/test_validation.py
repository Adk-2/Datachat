"""
Test script for Day 8 validation and error handling
"""
import requests
import json
import csv
import io
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_health():
    """Test 1: Backend health check"""
    print_section("Test 1: Backend Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def create_valid_csv():
    """Create a simple valid CSV for testing"""
    data = [
        ["name", "marks", "class", "date"],
        ["Alice", "85", "A", "2024-01-01"],
        ["Bob", "90", "B", "2024-01-02"],
        ["Charlie", "75", "A", "2024-01-03"],
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    return output.getvalue()

def create_empty_csv():
    """Create an empty CSV"""
    return ""

def test_valid_upload():
    """Test 2: Upload a valid CSV"""
    print_section("Test 2: Upload Valid CSV")
    csv_content = create_valid_csv()
    files = {"file": ("test.csv", csv_content.encode(), "text/csv")}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}...")
    return response.status_code == 200, data if response.status_code == 200 else None

def test_empty_upload():
    """Test 3: Upload empty CSV"""
    print_section("Test 3: Upload Empty CSV")
    files = {"file": ("empty.csv", b"", "text/csv")}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

def test_invalid_column_query(schema):
    """Test 4: Query with invalid column name 'grades' (fuzzy match to 'marks')"""
    print_section("Test 4: Query with Invalid Column 'grades'")
    payload = {"question": "Show histogram of grades"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Check if error contains suggestions
    has_error = data.get("error") == True
    has_suggestions = "suggestions" in data and len(data.get("suggestions", [])) > 0
    print(f"Has error: {has_error}")
    print(f"Has suggestions: {has_suggestions}")
    return has_error and has_suggestions

def test_non_numeric_histogram(schema):
    """Test 5: Query with non-numeric column for histogram"""
    print_section("Test 5: Histogram with Non-numeric Column")
    payload = {"question": "Show histogram of name"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    has_error = data.get("error") == True
    has_suggestions = "suggestions" in data
    print(f"Has error: {has_error}")
    print(f"Has suggestions: {has_suggestions}")
    return has_error

def test_unsupported_operation(schema):
    """Test 6: Query with unsupported operation"""
    print_section("Test 6: Unsupported Operation (Predict)")
    payload = {"question": "Predict future marks"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    has_error = data.get("error") == True
    print(f"Has error: {has_error}")
    return has_error

def test_valid_query(schema):
    """Test 7: Query with valid column"""
    print_section("Test 7: Query with Valid Column")
    payload = {"question": "Show histogram of marks"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    # Only print first 300 chars to avoid too much output
    response_str = json.dumps(data, indent=2)
    print(f"Response: {response_str[:300]}...")
    
    has_result = "result" in data and data.get("result") is not None
    has_error = data.get("error", False)
    print(f"Has result: {has_result}")
    print(f"Has error: {has_error}")
    return has_result and not has_error

def main():
    print("\n" + "*" * 70)
    print("*  DataChat Day 8: Validation and Error Handling Tests  *")
    print("*" * 70)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not running!")
        return
    
    print("\n✅ Backend is running")
    
    # Test 2: Upload valid CSV
    success, schema_data = test_valid_upload()
    if not success:
        print("\n❌ Failed to upload valid CSV")
        return
    
    print("\n✅ Valid CSV uploaded successfully")
    
    # Test 3: Upload empty CSV
    if test_empty_upload():
        print("✅ Empty CSV properly rejected with error")
    else:
        print("❌ Empty CSV should be rejected")
    
    # Test 4: Invalid column with fuzzy matching
    if test_invalid_column_query(schema_data):
        print("✅ Invalid column 'grades' returned error with fuzzy suggestions")
    else:
        print("❌ Invalid column should return error with suggestions")
    
    # Test 5: Non-numeric column for histogram
    if test_non_numeric_histogram(schema_data):
        print("✅ Non-numeric column properly rejected for histogram")
    else:
        print("❌ Non-numeric column should return error")
    
    # Test 6: Unsupported operation
    if test_unsupported_operation(schema_data):
        print("✅ Unsupported operation properly rejected")
    else:
        print("❌ Unsupported operation should return error")
    
    # Test 7: Valid query
    if test_valid_query(schema_data):
        print("✅ Valid query executed successfully")
    else:
        print("❌ Valid query should execute successfully")
    
    print("\n" + "*" * 70)
    print("*  All tests completed!")
    print("*" * 70 + "\n")

if __name__ == "__main__":
    main()
