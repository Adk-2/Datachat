"""
Extended test script for Day 8 validation and error handling - Test truly invalid column
"""
import requests
import json
import csv
import io

BASE_URL = "http://127.0.0.1:8000"

def test_truly_invalid_column():
    """Test with a column that absolutely doesn't exist"""
    print("\n" + "=" * 70)
    print("Test: Query with Truly Invalid Column 'student_id'")
    print("=" * 70)
    payload = {"question": "Show histogram of student_id"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    has_error = data.get("error") == True
    has_suggestions = "suggestions" in data and len(data.get("suggestions", [])) > 0
    print(f"Has error: {has_error}")
    print(f"Has suggestions: {has_suggestions}")
    if has_suggestions:
        print(f"Suggestions: {data['suggestions']}")
    return has_error and has_suggestions

def test_invalid_column_2():
    """Test with column 'xyz' which doesn't exist"""
    print("\n" + "=" * 70)
    print("Test: Query with Non-existent Column 'xyz'")
    print("=" * 70)
    payload = {"question": "Show histogram of xyz"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    has_error = data.get("error") == True
    print(f"Has error: {has_error}")
    return has_error

def test_malformed_csv():
    """Test uploading a malformed CSV"""
    print("\n" + "=" * 70)
    print("Test: Upload Malformed CSV")
    print("=" * 70)
    # Create CSV with mismatched columns
    malformed_csv = "name,marks\nAlice,85,extra\nBob,90"
    files = {"file": ("malformed.csv", malformed_csv.encode(), "text/csv")}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:300]}...")
    return response.status_code in [200, 400]  # Either parses or rejects gracefully

def main():
    print("\n" + "*" * 70)
    print("*  Extended Validation Tests  *")
    print("*" * 70)
    
    # Test truly invalid column
    if test_truly_invalid_column():
        print("✅ Truly invalid column returns error with suggestions")
    else:
        print("❌ Truly invalid column should return error with suggestions")
    
    # Test another invalid column
    if test_invalid_column_2():
        print("✅ Non-existent column properly rejected")
    else:
        print("❌ Non-existent column should return error")
    
    # Test malformed CSV
    if test_malformed_csv():
        print("✅ Malformed CSV handled gracefully")
    else:
        print("❌ Malformed CSV should be handled")
    
    print("\n" + "*" * 70)
    print("*  Extended tests completed!")
    print("*" * 70 + "\n")

if __name__ == "__main__":
    main()
