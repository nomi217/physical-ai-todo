"""
Check current user from browser cookies
"""
import os
from dotenv import load_dotenv
from app.auth.jwt import decode_access_token

load_dotenv()

# You'll need to paste your access_token cookie value here
token = input("Paste your access_token cookie value (from browser DevTools > Application > Cookies): ")

if token:
    payload = decode_access_token(token)
    if payload:
        print(f"\n✅ Token is valid!")
        print(f"User ID (sub): {payload.get('sub')}")
        print(f"Expiry (exp): {payload.get('exp')}")

        # Check if this matches task 13's owner
        from sqlmodel import create_engine, Session, select
        from app.models import Task, User

        engine = create_engine(os.getenv('DATABASE_URL'))
        with Session(engine) as session:
            # Get user
            user_id = int(payload.get('sub'))
            user = session.get(User, user_id)
            if user:
                print(f"\n👤 Signed in as:")
                print(f"   Email: {user.email}")
                print(f"   Name: {user.full_name or 'N/A'}")
                print(f"   User ID: {user.id}")

            # Get task 13
            task = session.get(Task, 13)
            if task:
                print(f"\n📝 Task 'Buy milk' (ID 13):")
                print(f"   Owner User ID: {task.user_id}")

                # Get owner
                owner = session.get(User, task.user_id)
                if owner:
                    print(f"   Owner Email: {owner.email}")

                # Check permission
                if user_id == task.user_id:
                    print(f"\n✅ PERMISSION: You CAN delete this task")
                else:
                    print(f"\n❌ PERMISSION DENIED: This task belongs to user {task.user_id}, not you!")
    else:
        print("❌ Token is invalid or expired")
else:
    print("No token provided")
