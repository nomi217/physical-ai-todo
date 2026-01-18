"""Test auth cookie flow"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("1. Logging in...")
session = requests.Session()
response = session.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "nauman.khalid@example.com",
        "password": input("Enter password: ")
    }
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Login successful!")
    print(f"Cookies: {session.cookies.get_dict()}")

    # Test creating a task
    print("\n2. Creating a task...")
    task_response = session.post(
        f"{BASE_URL}/tasks",
        json={
            "title": "Test Task from Script",
            "description": "Testing auth cookie",
            "priority": "medium"
        }
    )

    print(f"Status: {task_response.status_code}")
    if task_response.status_code == 201:
        print("✓ Task created successfully!")
        print(f"Task: {task_response.json()}")
    else:
        print(f"✗ Task creation failed: {task_response.text}")
else:
    print(f"✗ Login failed: {response.text}")
