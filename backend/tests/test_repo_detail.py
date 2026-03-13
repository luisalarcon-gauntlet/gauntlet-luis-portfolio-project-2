"""
Tests for single repository endpoint.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app

# ---------------------------------------------------------------------------
# FEATURE: GET /repos/{repo_name} — returns single repo with correct shape
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_repo_detail_endpoint_returns_single_repo_with_correct_shape():
    """
    When GET /repos/{repo_name} is called, the response must be a JSON object
    with data containing repo object, cached, and cache_generated_at.
    The repo must have all fields from repos list plus open_issues_count.
    """
    mock_repo = {
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
        "open_issues_count": 1,
        "fork": False,
        "pushed_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
    }

    with patch(
        "app.services.github_service.fetch_repo_from_github",
        new_callable=AsyncMock,
        return_value=mock_repo,
    ):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/repos/test-repo")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["error"] is None

    repo_data = data["data"]
    assert "repo" in repo_data
    assert "cached" in repo_data
    assert "cache_generated_at" in repo_data

    repo = repo_data["repo"]
    assert "id" in repo
    assert "name" in repo
    assert "full_name" in repo
    assert "description" in repo
    assert "html_url" in repo
    assert "homepage" in repo
    assert "primary_language" in repo
    assert "topics" in repo
    assert "stargazers_count" in repo
    assert "forks_count" in repo
    assert "is_pinned" in repo
    assert "updated_at" in repo
    assert "created_at" in repo
    assert "open_issues_count" in repo


# ---------------------------------------------------------------------------
# NOT COVERED IN THIS FILE — intentional v1 exclusions
# ---------------------------------------------------------------------------
# - Repository not found (404 error)
# - GitHub API returning 403 / rate-limit exceeded
# - GitHub API returning 500
# - Malformed JSON from GitHub API
# - Cache expiry / TTL enforcement
# - Performance: response time under load
# ---------------------------------------------------------------------------
