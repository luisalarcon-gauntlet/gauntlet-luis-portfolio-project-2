"""
Tests for cache refresh endpoint.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app

# ---------------------------------------------------------------------------
# FEATURE: POST /cache/refresh — protected endpoint that refreshes cache
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_refresh_endpoint_returns_refresh_data_with_token():
    """
    When POST /cache/refresh is called with a valid JWT token,
    the response must be a JSON object with data containing refreshed,
    repos_cached, profile_cached, cache_generated_at, and cache_expires_at.
    """
    # First register and login to get a token
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "supersecret123",
            },
        )

        login_response = await client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "supersecret123",
            },
        )

    token_data = login_response.json()["data"]
    token = token_data["access_token"]

    mock_repos = [
        {
            "id": 123456789,
            "name": "test-repo",
            "full_name": "luisalarcon-gauntlet/test-repo",
            "description": "Test repository",
            "html_url": "https://github.com/luisalarcon-gauntlet/test-repo",
            "homepage": None,
            "language": "Python",
            "topics": ["test"],
            "stargazers_count": 5,
            "forks_count": 2,
            "fork": False,
            "pushed_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_profile = {
        "login": "luisalarcon-gauntlet",
        "name": "Luis Alarcon",
        "bio": "Test bio",
        "avatar_url": "https://avatars.githubusercontent.com/u/000000000?v=4",
        "html_url": "https://github.com/luisalarcon-gauntlet",
        "public_repos": 1,
        "followers": 0,
        "following": 0,
        "location": "Austin, TX",
    }

    with patch(
        "app.services.github_service.fetch_repos_from_github",
        new_callable=AsyncMock,
        return_value=mock_repos,
    ), patch(
        "app.services.github_service.fetch_profile_from_github",
        new_callable=AsyncMock,
        return_value=mock_profile,
    ):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/cache/refresh",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["error"] is None

    refresh_data = data["data"]
    assert "refreshed" in refresh_data
    assert "repos_cached" in refresh_data
    assert "profile_cached" in refresh_data
    assert "cache_generated_at" in refresh_data
    assert "cache_expires_at" in refresh_data
    assert refresh_data["refreshed"] is True
    assert refresh_data["profile_cached"] is True
    assert isinstance(refresh_data["repos_cached"], int)


@pytest.mark.asyncio
async def test_cache_refresh_endpoint_returns_401_without_token():
    """
    When POST /cache/refresh is called without a token,
    the response must be 401 with an error message.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/cache/refresh")

    assert response.status_code == 401
    data = response.json()
    assert "data" in data
    assert data["data"] is None
    assert "error" in data
    assert data["error"] is not None


# ---------------------------------------------------------------------------
# NOT COVERED IN THIS FILE — intentional v1 exclusions
# ---------------------------------------------------------------------------
# - Invalid token handling (expired, malformed)
# - GitHub API failures during refresh
# - Partial refresh failures (repos succeed, profile fails)
# - Performance: refresh time with many repos
# ---------------------------------------------------------------------------
