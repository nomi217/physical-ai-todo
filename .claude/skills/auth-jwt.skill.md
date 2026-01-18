# JWT Authentication Skill

## Purpose
Generate JWT token creation, validation, and refresh functionality for FastAPI applications.

## When to Use
- Implementing user authentication
- Creating login/logout systems
- Protecting API endpoints with tokens
- Managing user sessions

## Inputs Required
- **Secret Key**: JWT secret (from environment variables)
- **Token Expiration**: Access token lifetime (default: 7 days)
- **Algorithm**: JWT signing algorithm (default: HS256)
- **User Model**: SQLModel User class

## Process

### 1. Install Dependencies
```bash
pip install python-jose[cryptography]==3.3.0
```

### 2. Create JWT Utilities
```python
# backend/app/auth/jwt.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # Use strong secret in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Payload data (usually {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token for long-term authentication

    Args:
        data: Payload data (usually {"sub": user_id})

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def decode_token(token: str) -> Optional[int]:
    """
    Decode token and extract user ID

    Args:
        token: JWT token string

    Returns:
        User ID (int) or None if invalid
    """
    payload = verify_token(token)
    if not payload:
        return None

    user_id: int = payload.get("sub")
    return user_id

def is_token_expired(token: str) -> bool:
    """
    Check if token is expired

    Args:
        token: JWT token string

    Returns:
        True if expired, False otherwise
    """
    payload = verify_token(token)
    if not payload:
        return True

    exp = payload.get("exp")
    if not exp:
        return True

    return datetime.utcnow() > datetime.fromtimestamp(exp)
```

### 3. Create Auth Dependencies
```python
# backend/app/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional

from app.database import get_session
from app.models import User
from app.auth.jwt import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Raises:
        HTTPException: 401 if token is invalid or user not found
        HTTPException: 403 if user is inactive
    """
    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    (convenience wrapper)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_optional_user(
    request: Request,
    session: Session = Depends(get_session)
) -> Optional[User]:
    """
    Dependency to get user if token is provided, None otherwise
    (for optional authentication)
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        return None

    user_id: int = payload.get("sub")
    if not user_id:
        return None

    user = session.get(User, user_id)
    return user
```

### 4. Login Route with Token Generation
```python
# backend/app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import UserLogin, Token
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.password import verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Login user and return JWT tokens

    Args:
        user_data: Email and password
        response: FastAPI response for setting cookies
        session: Database session

    Returns:
        Access token and refresh token
    """
    # Find user by email
    statement = select(User).where(User.email == user_data.email)
    user = session.execute(statement).scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # Set httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Use HTTPS in production
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30  # 30 days
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token_endpoint(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Refresh access token using refresh token

    Args:
        request: FastAPI request with refresh token cookie
        response: FastAPI response for setting new cookies
        session: Database session

    Returns:
        New access token
    """
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id: int = payload.get("sub")
    user = session.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new access token
    new_access_token = create_access_token(data={"sub": user.id})

    # Set new cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(response: Response):
    """
    Logout user by clearing authentication cookies
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}
```

### 5. Environment Variables
```bash
# .env
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-256-bits
```

## Security Best Practices
- Use strong secret keys (256+ bits, randomly generated)
- Store secrets in environment variables, never hardcode
- Use HTTPS in production (secure cookies)
- Set httpOnly flag on cookies to prevent XSS
- Implement token refresh mechanism
- Add token blacklisting for logout
- Limit token expiration times
- Validate token type (access vs refresh)
- Log authentication events for auditing

## Testing
```python
# Test token creation
def test_create_token():
    token = create_access_token(data={"sub": 123})
    assert token is not None

    payload = verify_token(token)
    assert payload["sub"] == 123
    assert payload["type"] == "access"

# Test expired token
def test_expired_token():
    from datetime import timedelta

    token = create_access_token(
        data={"sub": 123},
        expires_delta=timedelta(seconds=-1)  # Expired
    )

    assert is_token_expired(token) == True
```

## Output
- Complete JWT authentication system
- Token creation and verification
- Refresh token mechanism
- Secure cookie handling
- Protected route dependencies
