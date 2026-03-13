"""
FastAPI application entry point.
Minimal scaffold for Agent 1 - Environment & Infrastructure.
"""
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.routers import auth, profile, repos
from app.services import github_service

app = FastAPI(
    title="Luis Alarcon Portfolio API",
    description="Backend API for portfolio website",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(repos.router)
app.include_router(profile.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTPException handler returning standard envelope format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler returning standard envelope format."""
    return JSONResponse(
        status_code=500,
        content={"data": None, "error": "An internal server error occurred"},
    )


@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    Returns standard API response envelope with database status.
    """
    # Check database connection
    try:
        await db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        database_status = "disconnected"

    return {
        "data": {
            "status": "ok",
            "database": database_status,
            "timestamp": datetime.now().isoformat(),
        },
        "error": None,
    }


@app.post("/cache/refresh")
async def refresh_cache(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Protected endpoint for cache refresh.
    Requires JWT authentication.
    Manually triggers a full cache refresh from GitHub API.
    """
    try:
        # Fetch repos and profile from GitHub
        repos_data = await github_service.fetch_repos_from_github()
        profile_data = await github_service.fetch_profile_from_github()

        # Store in cache
        await github_service.store_repos_in_cache(db, repos_data)
        await github_service.store_profile_in_cache(db, profile_data)

        # Get cache metadata
        repos_cache_meta = await github_service.get_cache_metadata(db, "repos")
        profile_cache_meta = await github_service.get_cache_metadata(db, "profile")

        return {
            "data": {
                "refreshed": True,
                "repos_cached": len(repos_data),
                "profile_cached": True,
                "cache_generated_at": repos_cache_meta.fetched_at.isoformat() if repos_cache_meta else datetime.now().isoformat(),
                "cache_expires_at": repos_cache_meta.expires_at.isoformat() if repos_cache_meta else (datetime.now() + timedelta(minutes=settings.cache_ttl_minutes)).isoformat(),
            },
            "error": None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cache refresh failed: {str(e)}",
        )
