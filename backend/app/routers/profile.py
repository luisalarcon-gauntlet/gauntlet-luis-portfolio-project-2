"""
Router for profile endpoint.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.services import github_service

router = APIRouter(prefix="/profile", tags=["profile"])


def success(data):
    """Helper function for success response."""
    return {"data": data, "error": None}


@router.get("", response_model=dict)
async def get_profile(db: AsyncSession = Depends(get_db)):
    """
    Get GitHub profile data for the configured user.
    Returns cached data if available and fresh, otherwise fetches from GitHub.
    """
    cache_key = "profile"

    # Check if cache is valid
    is_valid = await github_service.is_cache_valid(db, cache_key)
    if is_valid:
        # Return cached profile
        profile = await github_service.get_profile_from_cache(db)
        if profile:
            cache_meta = await github_service.get_cache_metadata(db, cache_key)
            return success({
                "profile": {
                    "login": profile.login,
                    "name": profile.name,
                    "bio": profile.bio,
                    "avatar_url": profile.avatar_url,
                    "html_url": profile.html_url,
                    "public_repos": profile.public_repos,
                    "followers": profile.followers,
                    "following": profile.following,
                    "location": profile.location,
                },
                "cached": True,
                "cache_generated_at": cache_meta.fetched_at.isoformat(),
                "cache_expires_at": cache_meta.expires_at.isoformat(),
            })

    # Fetch from GitHub API
    try:
        profile_data = await github_service.fetch_profile_from_github()
        await github_service.store_profile_in_cache(db, profile_data)
        cache_meta = await github_service.get_cache_metadata(db, cache_key)

        return success({
            "profile": {
                "login": profile_data.get("login", ""),
                "name": profile_data.get("name"),
                "bio": profile_data.get("bio"),
                "avatar_url": profile_data.get("avatar_url", ""),
                "html_url": profile_data.get("html_url", ""),
                "public_repos": profile_data.get("public_repos", 0),
                "followers": profile_data.get("followers", 0),
                "following": profile_data.get("following", 0),
                "location": profile_data.get("location"),
            },
            "cached": False,
            "cache_generated_at": cache_meta.fetched_at.isoformat() if cache_meta else datetime.now().isoformat(),
            "cache_expires_at": cache_meta.expires_at.isoformat() if cache_meta else (datetime.now() + timedelta(minutes=settings.cache_ttl_minutes)).isoformat(),
        })
    except Exception as e:
        # If GitHub API fails and we have no cache, return error
        profile = await github_service.get_profile_from_cache(db)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"GitHub API request failed and no cached data is available: {str(e)}",
            )

        # Return stale cache if available
        cache_meta = await github_service.get_cache_metadata(db, cache_key)
        return success({
            "profile": {
                "login": profile.login,
                "name": profile.name,
                "bio": profile.bio,
                "avatar_url": profile.avatar_url,
                "html_url": profile.html_url,
                "public_repos": profile.public_repos,
                "followers": profile.followers,
                "following": profile.following,
                "location": profile.location,
            },
            "cached": True,
            "cache_generated_at": cache_meta.fetched_at.isoformat() if cache_meta else datetime.now().isoformat(),
            "cache_expires_at": cache_meta.expires_at.isoformat() if cache_meta else datetime.now().isoformat(),
        })
