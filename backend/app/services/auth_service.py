"""
Authentication service - JWT and password hashing.
"""
from datetime import timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain text password against a hashed password."""
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    """Create a JWT access token for a user."""
    from datetime import datetime
    
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token. Returns None if invalid."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
