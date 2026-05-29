"""
Complete test script for Day 8 validation and error handling
"""
import requests
import json
import csv
import io

BASE_URL = "http://127.0.0.1:8000"

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

def upload_csv():
    """Upload a valid CSV first"""
    csv_content = create_valid_csv()
    files = {"file": ("test.csv", csv_content.encode(), "text/csv")}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    return response.status_code == 200

def main():
    print("\n" + "*" * 70)
    print("*  Complete Validation & Error Handling Tests  *")
    print("*" * 70)
    
    # First, upload a valid CSV
    print("\nUploading test CSV...")
    if not upload_csv():
        print("Failed to upload test CSV!")
        return
    print("✅ Test CSV uploaded")
    
    # Test 1: Query with non-existent column
    print("\n" + "=" * 70)
    print("Test 1: Query with Non-existent Column 'student_id'")
    print("=" * 70)
    payload = {"question": "Show histogram of student_id"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    if data.get("error"):
        print("✅ Invalid column properly rejected")
    else:
        print("❌ Invalid column should return error")
    
    # Test 2: Query with non-numeric column
    print("\n" + "=" * 70)
    print("Test 2: Histogram with Non-numeric Column 'name'")
    print("=" * 70)
    payload = {"question": "Show histogram of name"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    if data.get("error") and data.get("suggestions"):
        print("✅ Non-numeric column rejected with suggestions")
    else:
        print("❌ Non-numeric column should return error with suggestions")
    
    # Test 3: Query with valid numeric column
    print("\n" + "=" * 70)
    print("Test 3: Histogram with Valid Numeric Column 'marks'")
    print("=" * 70)
    payload = {"question": "Show histogram of marks"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    data = response.json()
    # Only show first 300 chars
    response_str = json.dumps(data, indent=2)
    print(f"Response: {response_str[:300]}...")
    if data.get("result") and not data.get("error"):
        print("✅ Valid query executed successfully")
    else:
        print("❌ Valid query should execute successfully")
    
    # Test 4: Correlation with insufficient numeric columns
    print("\n" + "=" * 70)
    print("Test 4: Correlation Analysis")
    print("=" * 70)
    payload = {"question": "Show correlation"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:400]}...")
    # For this dataset we only have marks as numeric, so it should work or fail gracefully
    print(f"Result status: {'error' if data.get('error') else 'success'}")
    
    # Test 5: Empty/malformed CSV upload
    print("\n" + "=" * 70)
    print("Test 5: Upload Empty CSV")
    print("=" * 70)
    files = {"file": ("empty.csv", b"", "text/csv")}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"Error: {response.json()}")
        print("✅ Empty CSV properly rejected")
    else:
        print("❌ Empty CSV should be rejected with 400 error")
    
    # Test 6: Upload CSV with headers only
    print("\n" + "=" * 70)
    print("Test 6: Upload CSV with Headers Only")
    print("=" * 70)
    empty_data_csv = "name,marks,class\n"
    files = {"file": ("empty_data.csv", empty_data_csv.encode(), "text/csv")}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"Error: {response.json()}")
        print("✅ Empty data CSV properly rejected")
    else:
        print("❌ Empty data CSV should be rejected")
    
    # Test 7: Fuzzy matching test
    print("\n" + "=" * 70)
    print("Test 7: Fuzzy Column Name Matching")
    print("=" * 70)
    # Re-upload valid CSV first
    upload_csv()
    payload = {"question": "Show histogram of mks"}  # Similar to 'marks'
    response = requests.post(f"{BASE_URL}/query", json=payload)
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:400]}...")
    if data.get("result") or (data.get("error") and data.get("suggestions")):
        print("✅ Fuzzy matching working (either matched or provided suggestions)")
    
    print("\n" + "*" * 70)
    print("*  All tests completed!")
    print("*" * 70 + "\n")

if __name__ == "__main__":
    main()
