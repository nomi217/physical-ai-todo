"""Authentication routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import secrets
import httpx
import os
from datetime import datetime

from app.database import get_session
from app.models import User
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user
from app.auth.email_service import send_verification_email, send_welcome_email

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


# Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    """Register a new user and send verification email"""

    # Normalize email to lowercase for case-insensitive comparison
    normalized_email = user_data.email.lower()

    # Check if user already exists
    result = session.execute(select(User).where(User.email == normalized_email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create verification token
    verification_token = secrets.token_urlsafe(32)

    # Create new user (AUTO-VERIFIED for hackathon demo)
    new_user = User(
        email=normalized_email,  # Store normalized (lowercase) email
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,  # Auto-activated (email verification disabled)
        is_verified=True,  # Auto-verified (email verification disabled)
        verification_token=verification_token,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Email verification disabled for hackathon demo
    # send_verification_email(
    #     to_email=new_user.email,
    #     verification_token=verification_token,
    #     user_name=new_user.full_name
    # )

    return new_user


@router.post("/login")
def login(
    user_data: UserLogin,
    response: Response,
    session: Session = Depends(get_session)
):
    """Login user and return JWT token in cookie"""

    # Normalize email to lowercase for case-insensitive comparison
    normalized_email = user_data.email.lower()

    # Find user by email
    result = session.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address first"
        )

    # Create access token (sub must be string)
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set cookie (httpOnly for security)
    # NOTE: For localhost development, browser treats localhost:3000 and localhost:8000 as same-site
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="lax",  # Lax allows cookies on same-site requests
        secure=False,  # Must be False for HTTP (development)
        path="/"
        # No domain specified = defaults to request domain (localhost or 127.0.0.1)
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/verify-email")
def verify_email(
    request: VerifyEmailRequest,
    session: Session = Depends(get_session)
):
    """Verify user email with token"""

    # Find user by verification token
    result = session.execute(
        select(User).where(User.verification_token == request.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Verify user
    user.is_verified = True
    user.is_active = True
    user.verification_token = None  # Clear token
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)

    # Send welcome email
    send_welcome_email(to_email=user.email, user_name=user.full_name)

    return {"message": "Email verified successfully", "user": UserResponse.model_validate(user)}


@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user


class ResendVerificationRequest(BaseModel):
    email: EmailStr


@router.post("/resend-verification")
def resend_verification(
    request: ResendVerificationRequest,
    session: Session = Depends(get_session)
):
    """Resend verification email"""

    # Normalize email to lowercase
    normalized_email = request.email.lower()

    result = session.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    if not user:
        # Don't reveal if user exists or not (security)
        return {"message": "If the email exists, a verification link has been sent"}

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Generate new token
    verification_token = secrets.token_urlsafe(32)
    user.verification_token = verification_token
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()

    # Send verification email
    send_verification_email(
        to_email=user.email,
        verification_token=verification_token,
        user_name=user.full_name
    )

    return {"message": "Verification email sent"}


# ============================================================================
# GitHub OAuth Routes
# ============================================================================

@router.get("/github/authorize")
async def github_authorize():
    """Redirect to GitHub OAuth authorization page"""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env"
        )

    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={FRONTEND_URL}/auth/callback/github&"
        f"scope=user:email"
    )

    return RedirectResponse(github_auth_url)


class GitHubCallbackRequest(BaseModel):
    code: str


@router.post("/github/callback")
async def github_callback(
    request: GitHubCallbackRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    """Handle GitHub OAuth callback and create/login user"""
    code = request.code
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured"
        )

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            }
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for access token"
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from GitHub"
            )

        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from GitHub"
            )

        github_user = user_response.json()

        # Get user's primary email from GitHub
        email_response = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )

        if email_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user emails from GitHub"
            )

        emails = email_response.json()
        primary_email = next(
            (e["email"] for e in emails if e["primary"] and e["verified"]),
            None
        )

        if not primary_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verified primary email found on GitHub account"
            )

    # Normalize email to lowercase
    normalized_email = primary_email.lower()

    # Check if user exists
    result = session.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    if user:
        # User exists - login
        if not user.is_verified:
            # Auto-verify GitHub users
            user.is_verified = True
            user.is_active = True
            user.updated_at = datetime.utcnow()
            session.add(user)
            session.commit()
            session.refresh(user)
    else:
        # Create new user
        random_password = secrets.token_urlsafe(32)
        user = User(
            email=normalized_email,  # Use normalized email
            hashed_password=hash_password(random_password),  # Random password for OAuth users
            full_name=github_user.get("name") or github_user.get("login"),
            is_active=True,
            is_verified=True,  # GitHub users are auto-verified
            verification_token=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Send welcome email
        send_welcome_email(to_email=user.email, user_name=user.full_name)

    # Create JWT token
    jwt_token = create_access_token(data={"sub": str(user.id)})

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="lax",
        secure=False  # Set to True in production
    )

    return TokenResponse(
        access_token=jwt_token,
        user=UserResponse.model_validate(user)
    )
