"""
Tests for profile endpoint.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app

# ---------------------------------------------------------------------------
# FEATURE: GET /profile — returns GitHub profile with correct shape
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_profile_endpoint_returns_profile_with_correct_shape():
    """
    When GET /profile is called, the response must be a JSON object with
    data containing profile object, cached, cache_generated_at, and
    cache_expires_at. The profile must have login, name, bio, avatar_url,
    html_url, public_repos, followers, following, and location.
    """
    mock_profile = {
        "login": "luisalarcon-gauntlet",
        "name": "Luis Alarcon",
        "bio": "Full-Stack & AI Engineer · Gauntlet AI Program · Austin, TX",
        "avatar_url": "https://avatars.githubusercontent.com/u/000000000?v=4",
        "html_url": "https://github.com/luisalarcon-gauntlet",
        "public_repos": 18,
        "followers": 42,
        "following": 15,
        "location": "Austin, TX",
    }

    with patch(
        "app.services.github_service.fetch_profile_from_github",
        new_callable=AsyncMock,
        return_value=mock_profile,
    ):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/profile")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["error"] is None

    profile_data = data["data"]
    assert "profile" in profile_data
    assert "cached" in profile_data
    assert "cache_generated_at" in profile_data
    assert "cache_expires_at" in profile_data

    profile = profile_data["profile"]
    assert "login" in profile
    assert "name" in profile
    assert "bio" in profile
    assert "avatar_url" in profile
    assert "html_url" in profile
    assert "public_repos" in profile
    assert "followers" in profile
    assert "following" in profile
    assert "location" in profile


# ---------------------------------------------------------------------------
# NOT COVERED IN THIS FILE — intentional v1 exclusions
# ---------------------------------------------------------------------------
# - GitHub API returning 403 / rate-limit exceeded
# - GitHub API returning 500
# - Malformed JSON from GitHub API
# - Cache expiry / TTL enforcement
# - Performance: response time under load
# ---------------------------------------------------------------------------
