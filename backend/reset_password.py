"""Reset user password"""
import sys
from sqlmodel import Session, select
from app.database import engine
from app.models import User
from app.auth.password import hash_password
from datetime import datetime

def reset_password(email: str, new_password: str):
    """Reset a user's password"""
    print(f"Resetting password for: {email}")

    with Session(engine) as session:
        # Find user
        result = session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"[ERROR] User not found: {email}")
            return False

        # Hash and set new password
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.utcnow()

        session.add(user)
        session.commit()

        print(f"[SUCCESS] Password reset for: {email}")
        print(f"  New password: {new_password}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reset_password.py <email> <new_password>")
        print("Example: python reset_password.py user@example.com newpassword123")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    if len(password) < 8:
        print("[ERROR] Password must be at least 8 characters")
        sys.exit(1)

    success = reset_password(email, password)
    sys.exit(0 if success else 1)
