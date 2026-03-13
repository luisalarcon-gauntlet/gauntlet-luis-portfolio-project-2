"""
Authentication router - register and login endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def success(data) -> dict:
    """Helper to return success response envelope."""
    return {"data": data, "error": None}


@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    Returns user data (id, email, created_at) without password.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    # Create new user
    hashed = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return success(
        {
            "id": str(new_user.id),
            "email": new_user.email,
            "created_at": new_user.created_at.isoformat(),
        }
    )


@router.post("/login", response_model=dict)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Create access token
    access_token = create_access_token(str(user.id))
    expires_in = settings.access_token_expire_minutes * 60  # Convert to seconds

    return success(
        {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expires_in,
        }
    )
