"""
Pydantic schemas for authentication endpoints.
"""
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema for login endpoint."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserPublic(BaseModel):
    """Public user schema - never includes password."""

    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
