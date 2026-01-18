"""Test script for chatbot API"""
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxOCIsImV4cCI6MTc2NjM3NDEzMH0.jp0pgjMw6ISNWfqNpbwN3zJH_GkG4Dkn4r6aEohczbY"

def test_chat(message):
    """Test chatbot endpoint"""
    url = f"{BASE_URL}/api/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    data = {"message": message}

    print(f"\n{'='*60}")
    print(f"Testing: {message}")
    print(f"{'='*60}")

    response = requests.post(url, headers=headers, json=data)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.json()

if __name__ == "__main__":
    # Test 1: Add a task
    test_chat("add buy groceries")

    # Test 2: List tasks
    test_chat("show my tasks")

    # Test 3: Complete a task
    test_chat("mark task 1 as done")

    # Test 4: Delete a task
    test_chat("delete task 1")
