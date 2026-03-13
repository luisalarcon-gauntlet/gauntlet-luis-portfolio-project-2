"""
GitHub profile model for caching user profile data.
"""
from sqlalchemy import Column, Integer, String, Text

from app.models.base import Base, TimestampMixin, UUIDMixin


class Profile(Base, UUIDMixin, TimestampMixin):
    """
    Cached representation of GitHub user profile.
    Stores profile data fetched from the GitHub API.
    """

    __tablename__ = "profiles"

    login = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=False)
    html_url = Column(Text, nullable=False)
    public_repos = Column(Integer, nullable=False, default=0)
    followers = Column(Integer, nullable=False, default=0)
    following = Column(Integer, nullable=False, default=0)
    location = Column(String(255), nullable=True)
