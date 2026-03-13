"""
FastAPI application entry point.
Minimal scaffold for Agent 1 - Environment & Infrastructure.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request, Depends

from app.routers import auth
from app.dependencies import get_current_user
from app.models.user import User

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
async def health():
    """
    Health check endpoint.
    Returns standard API response envelope.
    """
    return {"data": {"status": "ok"}, "error": None}


@app.post("/cache/refresh")
async def refresh_cache(current_user: User = Depends(get_current_user)):
    """
    Protected endpoint for cache refresh.
    Requires JWT authentication.
    """
    return {"data": {"refreshed": True}, "error": None}
