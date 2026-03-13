"""
Pytest configuration and fixtures.
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, AsyncSessionLocal
from app.models import Base


@pytest.fixture(autouse=True)
async def clean_db():
    """
    Clean database before each test.
    Truncates all tables to ensure test isolation.
    """
    async with engine.begin() as conn:
        # Drop all tables and recreate them
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
