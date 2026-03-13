"""
Base model classes for SQLAlchemy.
All models must inherit from Base, UUIDMixin, and TimestampMixin.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy declarative base. All models inherit from this."""
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at columns to any model.
    Both are timezone-aware. updated_at refreshes automatically on UPDATE.
    """

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """
    Adds a UUID primary key column named `id`.
    Use alongside TimestampMixin on every model.
    """

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
