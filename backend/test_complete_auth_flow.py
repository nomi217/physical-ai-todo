"""
Complete authentication flow test
Tests: Register → Verify Email → Login → Get User → Logout
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/auth"
TEST_EMAIL = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
TEST_PASSWORD = "SecurePass123!"
TEST_NAME = "Test User"

async def test_auth_flow():
    """Test complete authentication flow"""
    async with httpx.AsyncClient() as client:
        print("\n" + "="*80)
        print("TESTING COMPLETE AUTHENTICATION FLOW")
        print("="*80 + "\n")

        # Test 1: Register
        print("[1] Testing Registration...")
        register_response = await client.post(
            f"{BASE_URL}/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": TEST_NAME
            }
        )

        if register_response.status_code == 201:
            user_data = register_response.json()
            print(f"   [OK] Registration successful!")
            print(f"   Email: {user_data['email']}")
            print(f"   Name: {user_data['full_name']}")
            print(f"   Verified: {user_data['is_verified']}")

            # Extract verification token from console output (in dev mode)
            print(f"\n   [INFO] Check backend console for verification link")
            print(f"   [INFO] In production, this would be sent via email")
        else:
            print(f"   [ERROR] Registration failed: {register_response.status_code}")
            print(f"   Error: {register_response.text}")
            return

        # Test 2: Login before verification (should fail)
        print("\n[2] Testing Login Before Verification (should fail)...")
        login_response = await client.post(
            f"{BASE_URL}/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )

        if login_response.status_code == 403:
            print(f"   [OK] Correctly blocked: Email not verified")
        else:
            print(f"   [WARN] Expected 403, got: {login_response.status_code}")

        # Test 3: Resend Verification
        print("\n[3] Testing Resend Verification...")
        resend_response = await client.post(
            f"{BASE_URL}/resend-verification",
            json={"email": TEST_EMAIL}
        )

        if resend_response.status_code == 200:
            print(f"   [OK] Verification email resent")
            print(f"   [INFO] Check backend console for new verification link")
        else:
            print(f"   [ERROR] Resend failed: {resend_response.status_code}")

        # Test 4: Manual verification (requires token from console)
        print("\n[4] Email Verification...")
        print(f"   [INFO] In dev mode, check backend console for verification link")
        print(f"   [INFO] Copy the token from: http://localhost:3001/auth/verify-email?token=TOKEN")

        verification_token = input("\n   Enter verification token (or press Enter to skip): ").strip()

        if verification_token:
            verify_response = await client.post(
                f"{BASE_URL}/verify-email",
                json={"token": verification_token}
            )

            if verify_response.status_code == 200:
                print(f"   [OK] Email verified successfully!")

                # Test 5: Login after verification
                print("\n[5] Testing Login After Verification...")
                login_response = await client.post(
                    f"{BASE_URL}/login",
                    json={
                        "email": TEST_EMAIL,
                        "password": TEST_PASSWORD
                    }
                )

                if login_response.status_code == 200:
                    login_data = login_response.json()
                    access_token = login_data["access_token"]
                    print(f"   [OK] Login successful!")
                    print(f"   Token: {access_token[:50]}...")

                    # Test 6: Get current user
                    print("\n[6] Testing Get Current User...")
                    cookies = login_response.cookies
                    me_response = await client.get(
                        f"{BASE_URL}/me",
                        cookies=cookies
                    )

                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print(f"   [OK] User data retrieved!")
                        print(f"   Name: {user_data['full_name']}")
                        print(f"   Email: {user_data['email']}")
                        print(f"   Verified: {user_data['is_verified']}")
                    else:
                        print(f"   [ERROR] Get user failed: {me_response.status_code}")

                    # Test 7: Logout
                    print("\n[7] Testing Logout...")
                    logout_response = await client.post(
                        f"{BASE_URL}/logout",
                        cookies=cookies
                    )

                    if logout_response.status_code == 200:
                        print(f"   [OK] Logout successful!")
                    else:
                        print(f"   [ERROR] Logout failed: {logout_response.status_code}")

                else:
                    print(f"   [ERROR] Login failed: {login_response.status_code}")
            else:
                print(f"   [ERROR] Verification failed: {verify_response.status_code}")
                print(f"   Error: {verify_response.text}")
        else:
            print(f"   [SKIP] Skipping verification and login tests")

        print("\n" + "="*80)
        print("AUTHENTICATION FLOW TEST COMPLETE")
        print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
