"""Manually verify a user account"""
import sys
from sqlmodel import Session, select
from app.database import engine
from app.models import User
from datetime import datetime

def verify_user(email: str):
    """Verify a user by email"""
    print(f"Attempting to verify user: {email}")

    with Session(engine) as session:
        # Find user
        result = session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"[ERROR] User not found: {email}")
            return False

        if user.is_verified:
            print(f"[INFO] User already verified: {email}")
            return True

        # Verify the user
        user.is_verified = True
        user.is_active = True
        user.verification_token = None
        user.updated_at = datetime.utcnow()

        session.add(user)
        session.commit()

        print(f"[SUCCESS] User verified: {email}")
        print(f"  - is_verified: {user.is_verified}")
        print(f"  - is_active: {user.is_active}")
        return True

if __name__ == "__main__":
    # Get email from command line or use default
    email = sys.argv[1] if len(sys.argv) > 1 else "nauman.khalid@example.com"
    success = verify_user(email)
    sys.exit(0 if success else 1)
