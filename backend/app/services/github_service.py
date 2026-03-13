"""
GitHub API service for fetching and caching repository data.
"""
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cache_metadata import CacheMetadata
from app.models.repository import Repository


async def fetch_repos_from_github() -> List[dict]:
    """
    Fetch all public repositories from GitHub API.
    Returns raw repository data as a list of dictionaries.
    """
    headers = {}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    url = f"https://api.github.com/users/{settings.github_username}/repos"
    params = {"per_page": 100, "sort": "updated"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_profile_from_github() -> dict:
    """
    Fetch GitHub profile data from GitHub API.
    Returns raw profile data as a dictionary.
    """
    headers = {}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    url = f"https://api.github.com/users/{settings.github_username}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_repo_from_github(repo_name: str) -> dict:
    """
    Fetch a single repository from GitHub API by name.
    Returns raw repository data as a dictionary.
    """
    headers = {}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    url = f"https://api.github.com/repos/{settings.github_username}/{repo_name}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def is_cache_valid(session: AsyncSession, cache_key: str) -> bool:
    """
    Check if cache entry exists and is still valid (within TTL).
    Returns True if cache is valid, False otherwise.
    """
    stmt = select(CacheMetadata).where(CacheMetadata.cache_key == cache_key)
    result = await session.execute(stmt)
    cache_meta = result.scalar_one_or_none()

    if cache_meta is None:
        return False

    now = datetime.now(cache_meta.expires_at.tzinfo)
    return now < cache_meta.expires_at


async def get_cache_metadata(
    session: AsyncSession, cache_key: str
) -> Optional[CacheMetadata]:
    """Get cache metadata for a given cache key."""
    stmt = select(CacheMetadata).where(CacheMetadata.cache_key == cache_key)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def store_repos_in_cache(
    session: AsyncSession, repos_data: List[dict]
) -> None:
    """
    Store repository data in the database cache.
    Upserts repositories and updates cache metadata.
    """
    from sqlalchemy import delete
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    # Clear existing repos for this user
    delete_stmt = delete(Repository).where(
        Repository.full_name.like(f"{settings.github_username}/%")
    )
    await session.execute(delete_stmt)

    # Insert/update repositories
    for repo_data in repos_data:
        # Check if repo is pinned (this would come from GraphQL, but for now we'll use a simple heuristic)
        # In v1, we'll just sort by updated_at, so is_pinned defaults to False
        is_pinned = False

        repo_dict = {
            "github_id": repo_data["id"],
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description"),
            "html_url": repo_data["html_url"],
            "homepage": repo_data.get("homepage"),
            "primary_language": repo_data.get("language"),
            "topics": repo_data.get("topics", []),
            "stargazers_count": repo_data.get("stargazers_count", 0),
            "forks_count": repo_data.get("forks_count", 0),
            "is_fork": repo_data.get("fork", False),
            "is_pinned": is_pinned,
            "github_pushed_at": (
                datetime.fromisoformat(repo_data["pushed_at"].replace("Z", "+00:00"))
                if repo_data.get("pushed_at")
                else None
            ),
            "github_updated_at": datetime.fromisoformat(
                repo_data["updated_at"].replace("Z", "+00:00")
            ),
        }

        stmt = (
            pg_insert(Repository)
            .values(**repo_dict)
            .on_conflict_do_update(
                index_elements=["github_id"],
                set_={
                    "name": repo_dict["name"],
                    "full_name": repo_dict["full_name"],
                    "description": repo_dict["description"],
                    "html_url": repo_dict["html_url"],
                    "homepage": repo_dict["homepage"],
                    "primary_language": repo_dict["primary_language"],
                    "topics": repo_dict["topics"],
                    "stargazers_count": repo_dict["stargazers_count"],
                    "forks_count": repo_dict["forks_count"],
                    "is_fork": repo_dict["is_fork"],
                    "is_pinned": repo_dict["is_pinned"],
                    "github_pushed_at": repo_dict["github_pushed_at"],
                    "github_updated_at": repo_dict["github_updated_at"],
                    "updated_at": datetime.now(),
                },
            )
        )
        await session.execute(stmt)

    # Update cache metadata
    now = datetime.now()
    expires_at = now + timedelta(minutes=settings.cache_ttl_minutes)

    cache_meta_stmt = (
        pg_insert(CacheMetadata)
        .values(
            cache_key="repos",
            fetched_at=now,
            expires_at=expires_at,
            http_status=200,
            record_count=len(repos_data),
        )
        .on_conflict_do_update(
            index_elements=["cache_key"],
            set_={
                "fetched_at": now,
                "expires_at": expires_at,
                "http_status": 200,
                "record_count": len(repos_data),
                "updated_at": now,
            },
        )
    )
    await session.execute(cache_meta_stmt)
    await session.commit()


async def get_repos_from_cache(session: AsyncSession) -> List[Repository]:
    """
    Retrieve all cached repositories from the database.
    Returns repositories sorted by is_pinned (desc) then updated_at (desc).
    """
    stmt = (
        select(Repository)
        .where(Repository.full_name.like(f"{settings.github_username}/%"))
        .order_by(Repository.is_pinned.desc(), Repository.github_updated_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_repo_from_cache(
    session: AsyncSession, repo_name: str
) -> Optional[Repository]:
    """Retrieve a single cached repository by name."""
    full_name = f"{settings.github_username}/{repo_name}"
    stmt = select(Repository).where(Repository.full_name == full_name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def store_profile_in_cache(session: AsyncSession, profile_data: dict) -> None:
    """Store GitHub profile data in the database cache."""
    from sqlalchemy import delete
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from app.models.profile import Profile

    # Clear existing profile for this user
    delete_stmt = delete(Profile).where(Profile.login == settings.github_username)
    await session.execute(delete_stmt)

    # Insert/update profile
    profile_dict = {
        "login": profile_data["login"],
        "name": profile_data.get("name"),
        "bio": profile_data.get("bio"),
        "avatar_url": profile_data.get("avatar_url", ""),
        "html_url": profile_data.get("html_url", ""),
        "public_repos": profile_data.get("public_repos", 0),
        "followers": profile_data.get("followers", 0),
        "following": profile_data.get("following", 0),
        "location": profile_data.get("location"),
    }

    profile_stmt = (
        pg_insert(Profile)
        .values(**profile_dict)
        .on_conflict_do_update(
            index_elements=["login"],
            set_={
                "name": profile_dict["name"],
                "bio": profile_dict["bio"],
                "avatar_url": profile_dict["avatar_url"],
                "html_url": profile_dict["html_url"],
                "public_repos": profile_dict["public_repos"],
                "followers": profile_dict["followers"],
                "following": profile_dict["following"],
                "location": profile_dict["location"],
                "updated_at": datetime.now(),
            },
        )
    )
    await session.execute(profile_stmt)

    # Update cache metadata
    now = datetime.now()
    expires_at = now + timedelta(minutes=settings.cache_ttl_minutes)

    cache_meta_stmt = (
        pg_insert(CacheMetadata)
        .values(
            cache_key="profile",
            fetched_at=now,
            expires_at=expires_at,
            http_status=200,
            record_count=1,
        )
        .on_conflict_do_update(
            index_elements=["cache_key"],
            set_={
                "fetched_at": now,
                "expires_at": expires_at,
                "http_status": 200,
                "record_count": 1,
                "updated_at": now,
            },
        )
    )
    await session.execute(cache_meta_stmt)
    await session.commit()


async def get_profile_from_cache(session: AsyncSession) -> Optional[Profile]:
    """Retrieve cached profile from the database."""
    from app.models.profile import Profile

    stmt = select(Profile).where(Profile.login == settings.github_username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
