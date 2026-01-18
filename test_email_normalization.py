"""
Test Email Normalization Fix
Tests that login is case-insensitive after normalization fix
"""
import requests
import time
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

def test_email_normalization():
    """Test that email login is case-insensitive"""

    print("=" * 60)
    print("EMAIL NORMALIZATION TEST")
    print("=" * 60)
    print()

    # Generate unique test email
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email_mixed_case = f"Test.User{timestamp}@Example.COM"
    test_password = "TestPassword123!"
    test_name = "Test User"

    print(f"📧 Test Email (Mixed Case): {test_email_mixed_case}")
    print(f"🔑 Password: {test_password}")
    print()

    # Step 1: Register with mixed case email
    print("Step 1: Registering user with mixed case email...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json={
                "email": test_email_mixed_case,
                "password": test_password,
                "full_name": test_name
            }
        )

        if response.status_code == 201:
            user_data = response.json()
            stored_email = user_data.get("email")
            print(f"✅ Registration successful!")
            print(f"   Stored email: {stored_email}")
            print(f"   Expected: {test_email_mixed_case.lower()}")

            if stored_email == test_email_mixed_case.lower():
                print("   ✅ Email normalized to lowercase!")
            else:
                print("   ⚠️ Email NOT normalized!")
                return False
        else:
            error = response.json()
            print(f"❌ Registration failed: {error.get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

    print()

    # Get verification token from response
    # In development mode, we need to verify manually or skip verification
    # For this test, we'll verify the user directly using the backend

    print("Step 2: Testing login with different case variations...")
    print()

    # Test cases with different email case variations
    test_cases = [
        (test_email_mixed_case.lower(), "lowercase"),
        (test_email_mixed_case.upper(), "UPPERCASE"),
        (test_email_mixed_case, "MixedCase (original)"),
    ]

    results = []

    for email_variant, description in test_cases:
        print(f"Testing login with {description}: {email_variant}")

        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": email_variant,
                    "password": test_password
                }
            )

            # We expect 403 (unverified) because email isn't verified
            # But we should NOT get 401 (invalid credentials) due to case mismatch
            if response.status_code == 403:
                error = response.json()
                if "verify your email" in error.get("detail", "").lower():
                    print(f"   ✅ User found (email verification required)")
                    print(f"      This confirms email normalization is working!")
                    results.append(True)
                else:
                    print(f"   ⚠️ Unexpected error: {error.get('detail')}")
                    results.append(False)
            elif response.status_code == 401:
                error = response.json()
                print(f"   ❌ Login failed: {error.get('detail')}")
                print(f"      This suggests case-sensitive email matching!")
                results.append(False)
            elif response.status_code == 200:
                print(f"   ✅ Login successful (user already verified)")
                results.append(True)
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                results.append(False)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(False)

        print()
        time.sleep(0.5)  # Small delay between requests

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if all(results):
        print()
        print("🎉 SUCCESS! Email normalization is working correctly!")
        print("   All case variations of the email can find the user.")
        print()
        print("✅ Fix Verified:")
        print("   - Emails are normalized to lowercase on registration")
        print("   - Login works regardless of email case")
        print("   - Case-insensitive email matching implemented")
        return True
    else:
        print()
        print("❌ FAILED! Email normalization may have issues.")
        print("   Some case variations did not work as expected.")
        return False

if __name__ == "__main__":
    try:
        # Check if backend is running
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=2)
        if response.status_code != 200:
            print("❌ Backend not responding correctly")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ Backend not running! Start with: cd backend && uvicorn app.main:app --reload")
        exit(1)

    success = test_email_normalization()
    exit(0 if success else 1)
