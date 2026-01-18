"""Quick login solution - Create test user and get login credentials"""
import sys
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("=" * 60)
    print("QUICK LOGIN SOLUTION")
    print("=" * 60)

    # Option 1: Use existing verified account
    print("\n[OPTION 1] Login with existing verified account:")
    print("-" * 60)
    print("Email: nauman.khalid@example.com")
    print("Password: TestPass123")
    print("\nTry this at: http://localhost:3000/auth/signin")

    # Test if this works
    print("\n[TESTING] Attempting login with these credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "nauman.khalid@example.com",
                "password": "TestPass123"
            }
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("[SUCCESS] Login works! Use these credentials.")
            data = response.json()
            print(f"User ID: {data['user']['id']}")
            print(f"User Email: {data['user']['email']}")
            return 0
        else:
            error = response.json()
            print(f"[ERROR] {error.get('detail', 'Login failed')}")
            print("\nTrying Option 2...")
    except Exception as e:
        print(f"[ERROR] Cannot connect to backend: {e}")
        print("\nIs the backend running? Start it with:")
        print("  cd backend && python -m uvicorn app.main:app --reload")
        return 1

    # Option 2: Create fresh test user
    print("\n[OPTION 2] Creating fresh test user:")
    print("-" * 60)

    timestamp = datetime.now().strftime("%H%M%S")
    test_email = f"quicktest_{timestamp}@example.com"
    test_password = "QuickTest123!"

    print(f"Email: {test_email}")
    print(f"Password: {test_password}")

    # Create user
    try:
        print("\n[STEP 1] Creating user...")
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "full_name": "Quick Test User"
            }
        )

        if response.status_code != 201:
            print(f"[ERROR] Registration failed: {response.json()}")
            return 1

        print("[SUCCESS] User created!")

        # Verify user using backend script
        print("\n[STEP 2] Verifying user...")
        import subprocess
        result = subprocess.run(
            ["python", "verify_user.py", test_email],
            cwd="backend",
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("[SUCCESS] User verified!")
        else:
            print(f"[WARNING] Auto-verify failed: {result.stderr}")
            print("Manual verify:")
            print(f"  cd backend && python verify_user.py {test_email}")

        # Test login
        print("\n[STEP 3] Testing login...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )

        if response.status_code == 200:
            print("[SUCCESS] Login works!")
            print(f"\nUSE THESE CREDENTIALS:")
            print(f"  Email: {test_email}")
            print(f"  Password: {test_password}")
            print(f"  URL: http://localhost:3000/auth/signin")
            return 0
        else:
            print(f"[ERROR] Login failed: {response.json()}")
            return 1

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
