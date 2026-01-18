"""Debug script to test authentication"""
import sys
from sqlmodel import Session, select
from app.database import engine
from app.models import User
from app.auth.password import hash_password, verify_password

def main():
    print("=== Authentication Debug Script ===\n")

    # Test 1: Database connectivity
    print("1. Testing database connectivity...")
    try:
        with Session(engine) as session:
            result = session.execute(select(User))
            users = result.all()
            print(f"   [OK] Connected! Found {len(users)} user(s) in database\n")

            # List all users
            if users:
                print("2. Existing users:")
                for user_tuple in users:
                    user = user_tuple[0]
                    print(f"   - Email: {user.email}")
                    print(f"     ID: {user.id}")
                    print(f"     Verified: {user.is_verified}")
                    print(f"     Active: {user.is_active}")
                    print(f"     Has password: {bool(user.hashed_password)}")
                    print()
            else:
                print("2. No users found in database\n")

            # Test 3: Password hashing
            print("3. Testing password hashing...")
            test_password = "testpass123"
            hashed = hash_password(test_password)
            print(f"   Password: {test_password}")
            print(f"   Hashed: {hashed[:50]}...")

            # Verify the password
            is_valid = verify_password(test_password, hashed)
            print(f"   Verification: {'[PASS]' if is_valid else '[FAIL]'}")

            # Try wrong password
            is_wrong = verify_password("wrongpassword", hashed)
            print(f"   Wrong password: {'[CORRECTLY REJECTED]' if not is_wrong else '[ERROR - ACCEPTED WRONG PASSWORD]'}")
            print()

            # Test 4: Check if test user can login
            if users:
                print("4. Testing login with first user...")
                user = users[0][0]
                print(f"   Trying to verify password for: {user.email}")
                print(f"   (Note: This will fail if password was set differently)")

    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n=== Debug Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
