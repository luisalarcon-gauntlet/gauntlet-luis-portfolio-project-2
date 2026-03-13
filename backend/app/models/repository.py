"""
Repository model for caching GitHub repository data.
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY

from app.models.base import Base, TimestampMixin, UUIDMixin


class Repository(Base, UUIDMixin, TimestampMixin):
    """
    Cached representation of a public GitHub repository.
    Stores data fetched from the GitHub API to avoid rate limits.
    """

    __tablename__ = "repositories"

    github_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    html_url = Column(Text, nullable=False)
    homepage = Column(Text, nullable=True)
    primary_language = Column(String(100), nullable=True)
    topics = Column(ARRAY(String), nullable=False, default=list)
    stargazers_count = Column(Integer, nullable=False, default=0)
    forks_count = Column(Integer, nullable=False, default=0)
    is_fork = Column(Boolean, nullable=False, default=False)
    is_pinned = Column(Boolean, nullable=False, default=False)
    github_pushed_at = Column(DateTime(timezone=True), nullable=True)
    github_updated_at = Column(DateTime(timezone=True), nullable=False)
