# Password Hashing & Validation Skill

## Purpose
Generate secure password hashing, verification, and validation logic using bcrypt for FastAPI applications.

## When to Use
- Implementing user registration
- Handling password authentication
- Validating password strength
- Implementing password reset functionality

## Inputs Required
- **Hashing Algorithm**: bcrypt (recommended)
- **Salt Rounds**: 12 (minimum 10 for security)
- **Password Requirements**: Min length, complexity rules

## Process

### 1. Install Dependencies
```bash
pip install passlib[bcrypt]==1.7.4
```

### 2. Create Password Utilities
```python
# backend/app/auth/password.py
from passlib.context import CryptContext
import re
from typing import Tuple, List

# Configure password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Higher is more secure but slower
)

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password meets security requirements

    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    # Check for uppercase
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    # Check for lowercase
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    # Check for digit
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number")

    # Check for special character
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        errors.append("Password must contain at least one special character")

    # Check for common weak passwords
    common_passwords = [
        "password", "12345678", "qwerty", "abc123",
        "password123", "admin123", "letmein"
    ]
    if password.lower() in common_passwords:
        errors.append("Password is too common. Please choose a stronger password")

    is_valid = len(errors) == 0
    return is_valid, errors

def generate_password_reset_token(user_id: int, expires_in_minutes: int = 30) -> str:
    """
    Generate password reset token

    Args:
        user_id: User ID
        expires_in_minutes: Token expiration time

    Returns:
        Reset token string
    """
    from datetime import datetime, timedelta
    from app.auth.jwt import create_access_token

    return create_access_token(
        data={"sub": user_id, "type": "password_reset"},
        expires_delta=timedelta(minutes=expires_in_minutes)
    )
```

### 3. Pydantic Schemas with Password Validation
```python
# backend/app/schemas.py
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        from app.auth.password import validate_password_strength

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")

        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength"""
        from app.auth.password import validate_password_strength

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")

        return v

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength"""
        from app.auth.password import validate_password_strength

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")

        return v
```

### 4. Registration Route with Password Hashing
```python
# backend/app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth.password import hash_password

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register new user with password hashing

    Args:
        user_data: User registration data
        session: Database session

    Returns:
        Created user object
    """
    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.execute(statement).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user
```

### 5. Password Change Route
```python
@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Change user password

    Args:
        password_data: Old and new passwords
        current_user: Authenticated user
        session: Database session

    Returns:
        Success message
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password"
        )

    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)

    # Update password
    current_user.hashed_password = new_hashed_password
    current_user.updated_at = datetime.utcnow()

    session.add(current_user)
    session.commit()

    return {"message": "Password changed successfully"}
```

### 6. Password Reset Flow
```python
from app.auth.password import generate_password_reset_token
from app.auth.jwt import verify_token
from app.auth.email_service import send_password_reset_email

@router.post("/forgot-password")
async def forgot_password(
    reset_request: PasswordResetRequest,
    session: Session = Depends(get_session)
):
    """
    Request password reset email

    Args:
        reset_request: Email address
        session: Database session

    Returns:
        Success message (even if user not found for security)
    """
    # Find user
    statement = select(User).where(User.email == reset_request.email)
    user = session.execute(statement).scalar_one_or_none()

    if user:
        # Generate reset token
        reset_token = generate_password_reset_token(user.id)

        # Send email
        await send_password_reset_email(
            email=user.email,
            reset_token=reset_token,
            user_name=user.full_name or "User"
        )

    # Always return success to prevent email enumeration
    return {
        "message": "If the email exists, a password reset link has been sent"
    }

@router.post("/reset-password")
def reset_password(
    reset_data: PasswordReset,
    session: Session = Depends(get_session)
):
    """
    Reset password using token

    Args:
        reset_data: Reset token and new password
        session: Database session

    Returns:
        Success message
    """
    # Verify token
    payload = verify_token(reset_data.token)

    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token"
        )

    user_id: int = payload.get("sub")
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Hash new password
    new_hashed_password = hash_password(reset_data.new_password)

    # Update password
    user.hashed_password = new_hashed_password
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()

    return {"message": "Password reset successfully"}
```

## Frontend Password Validation (React)
```tsx
'use client'
import { useState } from 'react'

interface PasswordStrength {
  score: number  // 0-4
  feedback: string[]
}

export function usePasswordValidation() {
  const [strength, setStrength] = useState<PasswordStrength>({
    score: 0,
    feedback: []
  })

  const validatePassword = (password: string) => {
    const feedback: string[] = []
    let score = 0

    if (password.length >= 8) score++
    else feedback.push("At least 8 characters")

    if (/[A-Z]/.test(password)) score++
    else feedback.push("One uppercase letter")

    if (/[a-z]/.test(password)) score++
    else feedback.push("One lowercase letter")

    if (/\d/.test(password)) score++
    else feedback.push("One number")

    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]/.test(password)) score++
    else feedback.push("One special character")

    setStrength({ score, feedback })
    return score >= 5
  }

  return { strength, validatePassword }
}

// Usage in component
export default function SignUpForm() {
  const [password, setPassword] = useState('')
  const { strength, validatePassword } = usePasswordValidation()

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value
    setPassword(newPassword)
    validatePassword(newPassword)
  }

  const getStrengthColor = () => {
    if (strength.score <= 1) return 'bg-red-500'
    if (strength.score <= 3) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div>
      <input
        type="password"
        value={password}
        onChange={handlePasswordChange}
        placeholder="Password"
      />

      {/* Strength indicator */}
      <div className="flex gap-1 mt-2">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded ${
              i < strength.score ? getStrengthColor() : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Feedback */}
      {strength.feedback.length > 0 && (
        <ul className="text-sm text-red-600 mt-2">
          {strength.feedback.map((item, i) => (
            <li key={i}>• {item}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

## Security Best Practices
- Use bcrypt with 12+ rounds (configurable based on server capabilities)
- Never store passwords in plain text
- Never log passwords (even for debugging)
- Validate password strength on both client and server
- Implement rate limiting on login/registration endpoints
- Use HTTPS for all password transmissions
- Implement account lockout after failed attempts
- Send password reset links, never passwords via email
- Expire password reset tokens after 30 minutes
- Invalidate all sessions after password change

## Testing
```python
def test_password_hashing():
    password = "MySecurePass123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("WrongPassword", hashed) == False

def test_password_validation():
    # Valid password
    is_valid, errors = validate_password_strength("MySecurePass123!")
    assert is_valid == True
    assert len(errors) == 0

    # Weak password
    is_valid, errors = validate_password_strength("weak")
    assert is_valid == False
    assert len(errors) > 0
```

## Output
- Secure password hashing with bcrypt
- Password strength validation
- Password change functionality
- Password reset flow
- Frontend validation components
