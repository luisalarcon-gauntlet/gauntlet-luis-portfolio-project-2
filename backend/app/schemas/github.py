"""
Pydantic schemas for GitHub-related endpoints.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RepoSchema(BaseModel):
    """Schema for a single repository."""

    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    homepage: Optional[str] = None
    primary_language: Optional[str] = None
    topics: List[str] = []
    stargazers_count: int = 0
    forks_count: int = 0
    is_pinned: bool = False
    updated_at: str  # ISO 8601 string
    created_at: str  # ISO 8601 string


class RepoDetailSchema(RepoSchema):
    """Schema for detailed repository view (includes open_issues_count)."""

    open_issues_count: int = 0


class ReposListResponse(BaseModel):
    """Response schema for GET /repos."""

    repos: List[RepoSchema]
    total_count: int
    cached: bool
    cache_generated_at: str  # ISO 8601 string
    cache_expires_at: str  # ISO 8601 string


class RepoDetailResponse(BaseModel):
    """Response schema for GET /repos/{repo_name}."""

    repo: RepoDetailSchema
    cached: bool
    cache_generated_at: str  # ISO 8601 string


class ProfileSchema(BaseModel):
    """Schema for GitHub profile data."""

    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: str
    html_url: str
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    location: Optional[str] = None


class ProfileResponse(BaseModel):
    """Response schema for GET /profile."""

    profile: ProfileSchema
    cached: bool
    cache_generated_at: str  # ISO 8601 string
    cache_expires_at: str  # ISO 8601 string


class CacheRefreshResponse(BaseModel):
    """Response schema for POST /cache/refresh."""

    refreshed: bool
    repos_cached: int
    profile_cached: bool
    cache_generated_at: str  # ISO 8601 string
    cache_expires_at: str  # ISO 8601 string
