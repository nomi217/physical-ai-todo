"""Quick API test script"""
import requests

# Test creating a task
response = requests.post(
    "http://localhost:8000/api/v1/tasks",
    json={
        "title": "Test Task",
        "description": "Testing Phase 2 Backend",
        "priority": "high",
        "tags": ["test", "phase2"]
    }
)

print("CREATE Task Response:", response.status_code)
print(response.json())

# Test listing tasks
response = requests.get("http://localhost:8000/api/v1/tasks")
print("\nLIST Tasks Response:", response.status_code)
print(response.json())
