"""Authentication dependencies for FastAPI"""
from fastapi import Depends, HTTPException, status, Cookie, Header
from sqlmodel import Session, select
from typing import Optional

from app.database import get_session
from app.models import User
from app.auth.jwt import decode_access_token


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT cookie or Authorization header"""
    # Try to get token from Authorization header first (for API calls)
    token = access_token
    if not token and authorization:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    # Get user from database
    result = session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user. Please verify your email.",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (verified email)"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address",
        )
    return current_user
