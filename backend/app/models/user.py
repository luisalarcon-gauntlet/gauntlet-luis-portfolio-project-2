"""
User model for authentication.
"""
from sqlalchemy import Column, String

from app.models.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model for authentication.
    Stores email and hashed password.
    """

    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
