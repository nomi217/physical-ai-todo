"""
Quick test to verify complete_task tool is being called
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1"

# You need to replace this with a valid access token
# For now, we'll just test if the endpoint works
def test_complete_task():
    # First, let's create a test task
    print("=" * 60)
    print("Testing chatbot completion functionality")
    print("=" * 60)

    # Test message
    chat_request = {
        "message": "complete Call my brother",
        "conversation_id": None  # New conversation
    }

    print(f"\n📤 Sending message: '{chat_request['message']}'")
    print("\nWaiting for chatbot response...")

    # Note: This will fail without auth, but we can check the logs
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json=chat_request,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print("\n✅ Response received:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 TIP: Make sure you're logged in to test this properly")
        print("💡 Check the backend logs for tool call debug messages")

if __name__ == "__main__":
    test_complete_task()
