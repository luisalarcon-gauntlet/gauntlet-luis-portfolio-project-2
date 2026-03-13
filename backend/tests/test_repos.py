"""
Tests for repository endpoints.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app

# ---------------------------------------------------------------------------
# FEATURE: GET /repos — returns cached repos with correct shape
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_repos_endpoint_returns_list_with_correct_shape():
    """
    When GET /repos is called, the response must be a JSON object with
    data containing repos array, total_count, cached, cache_generated_at,
    and cache_expires_at. Each repo must have id, name, full_name,
    description, html_url, homepage, primary_language, topics,
    stargazers_count, forks_count, is_pinned, updated_at, and created_at.
    """
    mock_repos = [
        {
            "id": 123456789,
            "name": "test-repo",
            "full_name": "luisalarcon-gauntlet/test-repo",
            "description": "Test repository",
            "html_url": "https://github.com/luisalarcon-gauntlet/test-repo",
            "homepage": None,
            "language": "Python",
            "topics": ["test", "python"],
            "stargazers_count": 5,
            "forks_count": 2,
            "fork": False,
            "pushed_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]

    with patch(
        "app.services.github_service.fetch_repos_from_github",
        new_callable=AsyncMock,
        return_value=mock_repos,
    ):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/repos")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["error"] is None

    repos_data = data["data"]
    assert "repos" in repos_data
    assert "total_count" in repos_data
    assert "cached" in repos_data
    assert "cache_generated_at" in repos_data
    assert "cache_expires_at" in repos_data

    repos = repos_data["repos"]
    assert isinstance(repos, list)
    assert len(repos) > 0

    first_repo = repos[0]
    assert "id" in first_repo
    assert "name" in first_repo
    assert "full_name" in first_repo
    assert "description" in first_repo
    assert "html_url" in first_repo
    assert "homepage" in first_repo
    assert "primary_language" in first_repo
    assert "topics" in first_repo
    assert "stargazers_count" in first_repo
    assert "forks_count" in first_repo
    assert "is_pinned" in first_repo
    assert "updated_at" in first_repo
    assert "created_at" in first_repo


# ---------------------------------------------------------------------------
# NOT COVERED IN THIS FILE — intentional v1 exclusions
# ---------------------------------------------------------------------------
# - GitHub API returning 403 / rate-limit exceeded
# - GitHub API returning 500
# - Malformed JSON from GitHub API
# - Repos with null description or null language
# - Pagination (> 100 repos)
# - Cache expiry / TTL enforcement (tested in integration)
# - Concurrent requests hitting the cache simultaneously (race condition)
# - Performance: response time under load
# - Security: GitHub token exposure in logs
# - Security: CORS misconfiguration
# - Refresh query parameter behavior
# ---------------------------------------------------------------------------
