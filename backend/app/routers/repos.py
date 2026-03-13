"""
Router for repository endpoints.
"""
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.services import github_service

router = APIRouter(prefix="/repos", tags=["repos"])


def success(data):
    """Helper function for success response."""
    return {"data": data, "error": None}


@router.get("", response_model=dict)
async def get_repos(
    refresh: bool = Query(False, description="Force refresh from GitHub API"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all public repositories for the configured GitHub user.
    Returns cached data if available and fresh, otherwise fetches from GitHub.
    """
    cache_key = "repos"

    # Check if cache is valid and refresh is not forced
    if not refresh:
        is_valid = await github_service.is_cache_valid(db, cache_key)
        if is_valid:
            # Return cached repos
            repos = await github_service.get_repos_from_cache(db)
            cache_meta = await github_service.get_cache_metadata(db, cache_key)

            repos_list = []
            for repo in repos:
                repos_list.append({
                    "id": repo.github_id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "html_url": repo.html_url,
                    "homepage": repo.homepage,
                    "primary_language": repo.primary_language,
                    "topics": repo.topics or [],
                    "stargazers_count": repo.stargazers_count,
                    "forks_count": repo.forks_count,
                    "is_pinned": repo.is_pinned,
                    "updated_at": repo.github_updated_at.isoformat(),
                    "created_at": repo.created_at.isoformat(),
                })

            return success({
                "repos": repos_list,
                "total_count": len(repos_list),
                "cached": True,
                "cache_generated_at": cache_meta.fetched_at.isoformat(),
                "cache_expires_at": cache_meta.expires_at.isoformat(),
            })

    # Fetch from GitHub API
    try:
        repos_data = await github_service.fetch_repos_from_github()
        await github_service.store_repos_in_cache(db, repos_data)
        cache_meta = await github_service.get_cache_metadata(db, cache_key)

        repos_list = []
        for repo_data in repos_data:
            repos_list.append({
                "id": repo_data["id"],
                "name": repo_data["name"],
                "full_name": repo_data["full_name"],
                "description": repo_data.get("description"),
                "html_url": repo_data["html_url"],
                "homepage": repo_data.get("homepage"),
                "primary_language": repo_data.get("language"),
                "topics": repo_data.get("topics", []),
                "stargazers_count": repo_data.get("stargazers_count", 0),
                "forks_count": repo_data.get("forks_count", 0),
                "is_pinned": False,  # In v1, we don't detect pinned repos
                "updated_at": repo_data.get("updated_at", ""),
                "created_at": repo_data.get("created_at", ""),
            })

        return success({
            "repos": repos_list,
            "total_count": len(repos_list),
            "cached": False,
            "cache_generated_at": cache_meta.fetched_at.isoformat() if cache_meta else datetime.now().isoformat(),
            "cache_expires_at": cache_meta.expires_at.isoformat() if cache_meta else (datetime.now() + timedelta(minutes=settings.cache_ttl_minutes)).isoformat(),
        })
    except Exception as e:
        # If GitHub API fails and we have no cache, return error
        repos = await github_service.get_repos_from_cache(db)
        if not repos:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"GitHub API request failed and no cached data is available: {str(e)}",
            )

        # Return stale cache if available
        cache_meta = await github_service.get_cache_metadata(db, cache_key)
        repos_list = []
        for repo in repos:
            repos_list.append({
                "id": repo.github_id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "html_url": repo.html_url,
                "homepage": repo.homepage,
                "primary_language": repo.primary_language,
                "topics": repo.topics or [],
                "stargazers_count": repo.stargazers_count,
                "forks_count": repo.forks_count,
                "is_pinned": repo.is_pinned,
                "updated_at": repo.github_updated_at.isoformat(),
                "created_at": repo.created_at.isoformat(),
            })

        return success({
            "repos": repos_list,
            "total_count": len(repos_list),
            "cached": True,
            "cache_generated_at": cache_meta.fetched_at.isoformat() if cache_meta else datetime.now().isoformat(),
            "cache_expires_at": cache_meta.expires_at.isoformat() if cache_meta else datetime.now().isoformat(),
        })


@router.get("/{repo_name}", response_model=dict)
async def get_repo(
    repo_name: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single repository by name.
    Returns cached data if available, otherwise fetches from GitHub.
    """
    # Check cache first
    repo = await github_service.get_repo_from_cache(db, repo_name)
    if repo:
        cache_meta = await github_service.get_cache_metadata(db, "repos")
        return success({
            "repo": {
                "id": repo.github_id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "html_url": repo.html_url,
                "homepage": repo.homepage,
                "primary_language": repo.primary_language,
                "topics": repo.topics or [],
                "stargazers_count": repo.stargazers_count,
                "forks_count": repo.forks_count,
                "open_issues_count": 0,  # Not stored in cache, would need to fetch
                "is_pinned": repo.is_pinned,
                "updated_at": repo.github_updated_at.isoformat(),
                "created_at": repo.created_at.isoformat(),
            },
            "cached": True,
            "cache_generated_at": cache_meta.fetched_at.isoformat() if cache_meta else datetime.now().isoformat(),
        })

    # Fetch from GitHub API
    try:
        repo_data = await github_service.fetch_repo_from_github(repo_name)
        # Store in cache (this will update the repos cache)
        await github_service.store_repos_in_cache(db, [repo_data])
        cache_meta = await github_service.get_cache_metadata(db, "repos")

        return success({
            "repo": {
                "id": repo_data["id"],
                "name": repo_data["name"],
                "full_name": repo_data["full_name"],
                "description": repo_data.get("description"),
                "html_url": repo_data["html_url"],
                "homepage": repo_data.get("homepage"),
                "primary_language": repo_data.get("language"),
                "topics": repo_data.get("topics", []),
                "stargazers_count": repo_data.get("stargazers_count", 0),
                "forks_count": repo_data.get("forks_count", 0),
                "open_issues_count": repo_data.get("open_issues_count", 0),
                "is_pinned": False,
                "updated_at": repo_data.get("updated_at", ""),
                "created_at": repo_data.get("created_at", ""),
            },
            "cached": False,
            "cache_generated_at": cache_meta.fetched_at.isoformat() if cache_meta else datetime.now().isoformat(),
        })
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository '{repo_name}' not found for user {settings.github_username}.",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"GitHub API request failed: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"GitHub API request failed: {str(e)}",
        )
