"""Complete authentication flow test"""
import requests
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_signup():
    """Test user registration"""
    print_section("TEST 1: User Registration (Signup)")

    # Generate unique email
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_{timestamp}@example.com"
    test_password = "TestPass123!"
    test_name = "Test User"

    print(f"Registering new user:")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    print(f"  Name: {test_name}")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "full_name": test_name
            }
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            print("[SUCCESS] User registered successfully!")
            print(f"  User ID: {data['id']}")
            print(f"  Email: {data['email']}")
            print(f"  Verified: {data['is_verified']}")
            print(f"  Created: {data['created_at']}")
            return test_email, test_password, data['id']
        else:
            print(f"[FAIL] Registration failed")
            print(f"  Error: {response.json()}")
            return None, None, None

    except Exception as e:
        print(f"[ERROR] {e}")
        return None, None, None

def test_login_unverified(email, password):
    """Test login with unverified account"""
    print_section("TEST 2: Login (Unverified Account)")

    print(f"Attempting to login:")
    print(f"  Email: {email}")
    print(f"  Expected: Should fail (email not verified)")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 403:
            error = response.json()
            print("[EXPECTED] Login blocked correctly!")
            print(f"  Message: {error['detail']}")
            return True
        else:
            print(f"[UNEXPECTED] Got status {response.status_code}")
            print(f"  Response: {response.json()}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def verify_user_manual(email):
    """Manually verify user via database"""
    print_section("TEST 3: Email Verification")

    print(f"Verifying user: {email}")

    from sqlmodel import Session, select
    from app.database import engine
    from app.models import User
    from datetime import datetime

    try:
        with Session(engine) as session:
            result = session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if not user:
                print(f"[ERROR] User not found")
                return False

            user.is_verified = True
            user.is_active = True
            user.verification_token = None
            user.updated_at = datetime.utcnow()

            session.add(user)
            session.commit()

            print(f"[SUCCESS] User verified!")
            print(f"  is_verified: {user.is_verified}")
            print(f"  is_active: {user.is_active}")
            return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_login_verified(email, password):
    """Test login with verified account"""
    print_section("TEST 4: Login (Verified Account)")

    print(f"Attempting to login:")
    print(f"  Email: {email}")
    print(f"  Expected: Should succeed")

    try:
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Login successful!")
            print(f"  User ID: {data['user']['id']}")
            print(f"  Email: {data['user']['email']}")
            print(f"  Token Type: {data['token_type']}")
            print(f"  Access Token: {data['access_token'][:50]}...")

            # Check cookies
            cookies = session.cookies.get_dict()
            if 'access_token' in cookies:
                print(f"  Cookie Set: YES")
            else:
                print(f"  Cookie Set: NO (checking response)")

            return True, data['access_token']
        else:
            print(f"[FAIL] Login failed")
            print(f"  Error: {response.json()}")
            return False, None

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_login_wrong_password(email):
    """Test login with wrong password"""
    print_section("TEST 5: Login (Wrong Password)")

    print(f"Attempting to login with wrong password:")
    print(f"  Email: {email}")
    print(f"  Expected: Should fail")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!"
            }
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 401:
            error = response.json()
            print("[EXPECTED] Login blocked correctly!")
            print(f"  Message: {error['detail']}")
            return True
        else:
            print(f"[UNEXPECTED] Got status {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_duplicate_signup(email):
    """Test signup with existing email"""
    print_section("TEST 6: Duplicate Email Registration")

    print(f"Attempting to register existing email:")
    print(f"  Email: {email}")
    print(f"  Expected: Should fail")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": "AnotherPass123!",
                "full_name": "Another User"
            }
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 400:
            error = response.json()
            print("[EXPECTED] Registration blocked correctly!")
            print(f"  Message: {error['detail']}")
            return True
        else:
            print(f"[UNEXPECTED] Got status {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  AUTHENTICATION FLOW TEST SUITE")
    print("="*60)

    results = {
        "passed": 0,
        "failed": 0
    }

    # Test 1: Signup
    email, password, user_id = test_signup()
    if email:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n[CRITICAL] Cannot continue without successful signup")
        return

    # Test 2: Login (unverified)
    if test_login_unverified(email, password):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 3: Verify user
    if verify_user_manual(email):
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n[CRITICAL] Cannot continue without verification")
        return

    # Test 4: Login (verified)
    success, token = test_login_verified(email, password)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 5: Wrong password
    if test_login_wrong_password(email):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 6: Duplicate signup
    if test_duplicate_signup(email):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Final results
    print_section("TEST RESULTS")
    total = results["passed"] + results["failed"]
    print(f"Total Tests: {total}")
    print(f"Passed: {results['passed']} ({results['passed']/total*100:.1f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/total*100:.1f}%)")

    if results["failed"] == 0:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n[WARNING] {results['failed']} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
