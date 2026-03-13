"""
FastAPI application entry point.
Minimal scaffold for Agent 1 - Environment & Infrastructure.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request

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
