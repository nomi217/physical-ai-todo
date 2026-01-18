import requests
import json

# Test the chat endpoint directly
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "conversation_id": None,
        "message": "show me all my tasks"
    },
    cookies={
        "access_token": "your_token_here"  # Will use credentials
    },
    headers={
        "Content-Type": "application/json"
    }
)

print("Status Code:", response.status_code)
print("\nResponse:")
data = response.json()
print(json.dumps(data, indent=2))
print("\n\nAssistant Message Length:", len(data.get('assistant_message', '')))
print("Assistant Message:")
print(data.get('assistant_message', ''))
