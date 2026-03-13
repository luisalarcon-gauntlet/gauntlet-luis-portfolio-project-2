"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient

from app.main import app

# ---------------------------------------------------------------------------
# FEATURE: User registration — POST /auth/register
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_endpoint_returns_user_data_without_password():
    """
    When POST /auth/register is called with valid email and password,
    the response must be a JSON object with data containing id, email,
    and created_at. The response must NOT include password or hashed_password.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "supersecret123",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["error"] is None

    user_data = data["data"]
    assert "id" in user_data
    assert "email" in user_data
    assert user_data["email"] == "test@example.com"
    assert "created_at" in user_data
    assert "password" not in user_data
    assert "hashed_password" not in user_data


@pytest.mark.asyncio
async def test_login_endpoint_returns_jwt_token():
    """
    When POST /auth/login is called with valid email and password,
    the response must be a JSON object with data containing access_token,
    token_type (bearer), and expires_in (seconds).
    """
    # First register a user
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "password": "supersecret123",
            },
        )

        # Then login
        response = await client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "supersecret123",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["error"] is None

    token_data = data["data"]
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "expires_in" in token_data
    assert isinstance(token_data["expires_in"], int)
    assert token_data["expires_in"] > 0


@pytest.mark.asyncio
async def test_protected_route_returns_401_without_token():
    """
    When a protected route is called without an Authorization header,
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
# - Duplicate email registration (409 conflict)
# - Invalid email format validation
# - Password strength requirements
# - Login with wrong password
# - Login with non-existent email
# - Token expiration handling
# - Token refresh endpoint
# - Password reset flow
# - Email verification
# - Rate limiting on auth endpoints
# - Account lockout after failed attempts
# ---------------------------------------------------------------------------
