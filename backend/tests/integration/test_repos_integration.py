"""
Integration tests for GitHub Repositories Fetch & Cache feature.
Tests the full flow: API call → DB state change → correct response.
No mocks - tests against real FastAPI app and real database.
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.repository import Repository
from app.models.cache_metadata import CacheMetadata
from app.db.session import get_db


# ---------------------------------------------------------------------------
# FEATURE 2: GitHub Repositories Fetch & Cache (Backend)
# Integration test covering full happy path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repos_endpoint_fetches_from_github_and_caches_in_db():
    """
    Acceptance Criteria:
    - GET /repos returns HTTP 200 with a JSON array
    - Each repo object contains: name, description, language, topics, 
      stargazers_count, updated_at, html_url
    - Postgres table exists with cache data
    - Cache TTL is set to 60 minutes
    - The endpoint returns repos for username luisalarcon-gauntlet only
    
    Test flow:
    1. Make GET /repos request (cache miss - should fetch from GitHub)
    2. Verify response is 200 with correct structure
    3. Verify database has cache entry with correct data
    4. Verify cache metadata exists with correct TTL
    5. Make second GET /repos request (cache hit - should use DB)
    6. Verify second response uses cached data (cached_at unchanged)
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First request - should fetch from GitHub and cache
        response1 = await client.get("/repos")
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert "data" in data1
        assert data1["error"] is None
        
        repos_data = data1["data"]
        assert "repos" in repos_data
        assert "total_count" in repos_data
        assert "cached" in repos_data
        assert "cache_generated_at" in repos_data
        assert "cache_expires_at" in repos_data
        
        # Verify repos array structure
        repos = repos_data["repos"]
        assert isinstance(repos, list)
        assert len(repos) > 0
        
        # Verify first repo has all required fields
        first_repo = repos[0]
        assert "name" in first_repo
        assert "description" in first_repo  # Can be null
        assert "primary_language" in first_repo  # Can be null
        assert "topics" in first_repo
        assert isinstance(first_repo["topics"], list)
        assert "stargazers_count" in first_repo
        assert "updated_at" in first_repo
        assert "html_url" in first_repo
        
        # Verify all repos are for luisalarcon-gauntlet
        for repo in repos:
            assert repo["full_name"].startswith("luisalarcon-gauntlet/")
        
        # Verify database has cache entry
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            # Check repositories table
            stmt = select(Repository)
            result = await session.execute(stmt)
            db_repos = list(result.scalars().all())
            assert len(db_repos) > 0
            
            # Verify cache metadata exists
            stmt = select(CacheMetadata).where(CacheMetadata.cache_key == "repos")
            result = await session.execute(stmt)
            cache_meta = result.scalar_one_or_none()
            assert cache_meta is not None
            assert cache_meta.cache_key == "repos"
            
            # Verify TTL is 60 minutes (within 1 minute tolerance)
            expected_expires = cache_meta.fetched_at + timedelta(minutes=60)
            time_diff = abs((cache_meta.expires_at - expected_expires).total_seconds())
            assert time_diff < 60, f"TTL should be 60 minutes, got {time_diff} seconds difference"
            
            # Store cache timestamp for comparison
            first_cache_timestamp = cache_meta.fetched_at
        
        # Second request - should use cache (cached_at unchanged)
        response2 = await client.get("/repos")
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["data"]["cached"] is True, "Second request should use cache"
        
        # Verify cache timestamp was not updated
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            stmt = select(CacheMetadata).where(CacheMetadata.cache_key == "repos")
            result = await session.execute(stmt)
            cache_meta2 = result.scalar_one_or_none()
            assert cache_meta2 is not None
            # Cache timestamp should be the same (within 1 second tolerance for test execution)
            time_diff = abs((cache_meta2.fetched_at - first_cache_timestamp).total_seconds())
            assert time_diff < 2, "Cache should not be refreshed on second request"


@pytest.mark.asyncio
async def test_repos_endpoint_responds_quickly_when_serving_from_cache():
    """
    Acceptance Criteria:
    - /repos responds in under 500ms when serving from cache
    
    Test flow:
    1. Make first request to populate cache
    2. Make second request and measure response time
    3. Verify response time is under 500ms
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First request to populate cache
        await client.get("/repos")
        
        # Second request - should use cache
        import time
        start_time = time.time()
        response = await client.get("/repos")
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        assert response.status_code == 200
        assert elapsed_time < 500, f"Cache response took {elapsed_time}ms, should be < 500ms"
        assert response.json()["data"]["cached"] is True


@pytest.mark.asyncio
async def test_repos_endpoint_refreshes_cache_when_stale():
    """
    Acceptance Criteria:
    - If cache is stale, a fresh GitHub API call is made and cached_at is updated
    
    Test flow:
    1. Make request to populate cache
    2. Manually expire cache by updating expires_at to past
    3. Make request with refresh=true
    4. Verify cache was refreshed (new fetched_at timestamp)
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First request to populate cache
        await client.get("/repos")
        
        # Get initial cache timestamp
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            stmt = select(CacheMetadata).where(CacheMetadata.cache_key == "repos")
            result = await session.execute(stmt)
            cache_meta = result.scalar_one_or_none()
            assert cache_meta is not None
            initial_timestamp = cache_meta.fetched_at
            
            # Manually expire cache
            cache_meta.expires_at = datetime.now() - timedelta(minutes=1)
            await session.commit()
        
        # Request with refresh=true should force refresh
        response = await client.get("/repos?refresh=true")
        
        assert response.status_code == 200
        assert response.json()["data"]["cached"] is False, "Refresh should fetch from GitHub"
        
        # Verify cache was updated
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            stmt = select(CacheMetadata).where(CacheMetadata.cache_key == "repos")
            result = await session.execute(stmt)
            cache_meta2 = result.scalar_one_or_none()
            assert cache_meta2 is not None
            # New timestamp should be more recent
            assert cache_meta2.fetched_at > initial_timestamp, "Cache should be refreshed with new timestamp"


# ---------------------------------------------------------------------------
# NOT COVERED IN THIS FILE — intentional v1 exclusions
# ---------------------------------------------------------------------------
# - GitHub API rate limit handling (60 req/hour)
# - GitHub API returning 4xx or 5xx errors
# - Network timeout between backend and GitHub API
# - Postgres connection failure scenarios
# - Concurrent requests hitting cache simultaneously (race conditions)
# - Cache invalidation via webhooks
# - Pagination for repos beyond 100
# - Performance testing under load
# ---------------------------------------------------------------------------
