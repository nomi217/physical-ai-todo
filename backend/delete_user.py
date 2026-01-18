"""Delete a user from the database"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.database import engine
from sqlmodel import Session, select
from app.models import User

email = "nauman.khalid@example.com"

# Connect to database
with Session(engine) as session:
    # Find user
    result = session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        print(f"Found user: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Is Verified: {user.is_verified}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Created: {user.created_at}")
        
        # Delete user
        session.delete(user)
        session.commit()
        print("\n✅ User deleted successfully!")
    else:
        print(f"❌ User {email} not found in database")
