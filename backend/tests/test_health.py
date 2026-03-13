"""
Tests for health check endpoint.
"""
import pytest
from httpx import AsyncClient

from app.main import app

# ---------------------------------------------------------------------------
# FEATURE: GET /health — returns health status with database connection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_endpoint_returns_status_with_database():
    """
    When GET /health is called, the response must be a JSON object with
    data containing status (ok), database (connected), and timestamp.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["error"] is None

    health_data = data["data"]
    assert "status" in health_data
    assert "database" in health_data
    assert "timestamp" in health_data
    assert health_data["status"] == "ok"
    assert health_data["database"] == "connected"


# ---------------------------------------------------------------------------
# NOT COVERED IN THIS FILE — intentional v1 exclusions
# ---------------------------------------------------------------------------
# - Database connection failure handling
# - Health check performance under load
# - Detailed database health metrics
# ---------------------------------------------------------------------------
