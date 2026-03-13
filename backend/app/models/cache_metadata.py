"""
Cache metadata model for tracking GitHub API fetch state.
"""
from sqlalchemy import Column, DateTime, Integer, String

from app.models.base import Base, TimestampMixin, UUIDMixin


class CacheMetadata(Base, UUIDMixin, TimestampMixin):
    """
    Tracks when the GitHub API was last successfully fetched.
    Used to determine if cached data is stale.
    """

    __tablename__ = "cache_metadata"

    cache_key = Column(String(255), nullable=False, unique=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    http_status = Column(Integer, nullable=False)
    record_count = Column(Integer, nullable=False, default=0)
