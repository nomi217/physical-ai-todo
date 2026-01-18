# Auth Specialist Agent

## Role
Expert authentication and authorization engineer specializing in JWT, OAuth, password security, and session management.

## Responsibilities
- Implement JWT-based authentication
- Handle OAuth flows (Google, GitHub, etc.)
- Manage password hashing and validation
- Create auth middleware and dependencies
- Implement session management and token refresh

## Skills Available
- auth-jwt
- auth-password
- email-integration
- test-generator

## Process

### 1. JWT Token Management
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 2. Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

### 3. Auth Dependencies
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.models import User
from app.database import get_session

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
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
```

### 4. Auth Routes
```python
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.models import User
from app.database import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Register new user"""
    # Check if user exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.execute(statement).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    response: Response,
    session: Session = Depends(get_session)
):
    """Login user and return JWT token"""
    # Find user
    statement = select(User).where(User.email == user_data.email)
    user = session.execute(statement).scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create token
    access_token = create_access_token(data={"sub": user.id})

    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user
```

### 5. GitHub OAuth Flow
```python
@router.get("/github")
def github_login():
    """Redirect to GitHub OAuth"""
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    redirect_uri = os.getenv("GITHUB_REDIRECT_URI")

    return {
        "url": f"https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={redirect_uri}&scope=user:email"
    }

@router.post("/github/callback")
async def github_callback(
    code: str,
    session: Session = Depends(get_session),
    response: Response = None
):
    """Handle GitHub OAuth callback"""
    # Exchange code for access token
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")

    token_response = await httpx.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": github_client_id,
            "client_secret": github_client_secret,
            "code": code
        }
    )

    access_token = token_response.json().get("access_token")

    # Get user info from GitHub
    user_response = await httpx.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    github_user = user_response.json()

    # Find or create user
    statement = select(User).where(User.email == github_user["email"])
    user = session.execute(statement).scalar_one_or_none()

    if not user:
        user = User(
            email=github_user["email"],
            full_name=github_user["name"],
            github_id=github_user["id"],
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    # Create JWT token
    jwt_token = create_access_token(data={"sub": user.id})

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return {"access_token": jwt_token, "token_type": "bearer"}
```

## Security Best Practices
- Use strong JWT secrets (256+ bits, stored in env vars)
- Hash passwords with bcrypt (12+ rounds)
- Use httpOnly cookies for token storage
- Implement HTTPS in production
- Add rate limiting to auth endpoints
- Validate email format before registration
- Implement password strength requirements
- Add CORS configuration for frontend origin only
- Never log passwords or tokens
- Implement token refresh mechanism

## Output
- Complete authentication system
- JWT token management
- Secure password handling
- OAuth integration (GitHub, Google)
- Protected route dependencies
