"""
Seed script for minimal test data.
Idempotent - safe to run multiple times.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.session import AsyncSessionLocal
from app.models.repository import Repository
from app.models.cache_metadata import CacheMetadata


async def seed_repositories(session) -> None:
    """Seed three test repositories."""
    now = datetime.utcnow()
    
    repos_data = [
        {
            "github_id": 100000001,
            "name": "ai-chat-app",
            "full_name": "luisalarcon-gauntlet/ai-chat-app",
            "description": "LLM-powered chat app with RAG",
            "html_url": "https://github.com/luisalarcon-gauntlet/ai-chat-app",
            "homepage": None,
            "primary_language": "Python",
            "topics": ["ai", "langchain", "fastapi"],
            "stargazers_count": 12,
            "forks_count": 0,
            "is_fork": False,
            "is_pinned": True,
            "github_pushed_at": now - timedelta(days=2),
            "github_updated_at": now - timedelta(days=2),
        },
        {
            "github_id": 100000002,
            "name": "portfolio-site",
            "full_name": "luisalarcon-gauntlet/portfolio-site",
            "description": "Personal portfolio — this site",
            "html_url": "https://github.com/luisalarcon-gauntlet/portfolio-site",
            "homepage": None,
            "primary_language": "TypeScript",
            "topics": ["nextjs", "react", "typescript"],
            "stargazers_count": 5,
            "forks_count": 0,
            "is_fork": False,
            "is_pinned": True,
            "github_pushed_at": now - timedelta(days=5),
            "github_updated_at": now - timedelta(days=5),
        },
        {
            "github_id": 100000003,
            "name": "fastapi-starter",
            "full_name": "luisalarcon-gauntlet/fastapi-starter",
            "description": "FastAPI boilerplate with Docker",
            "html_url": "https://github.com/luisalarcon-gauntlet/fastapi-starter",
            "homepage": None,
            "primary_language": "Python",
            "topics": ["fastapi", "docker", "postgres"],
            "stargazers_count": 8,
            "forks_count": 0,
            "is_fork": False,
            "is_pinned": False,
            "github_pushed_at": now - timedelta(days=10),
            "github_updated_at": now - timedelta(days=10),
        },
    ]
    
    for repo_data in repos_data:
        stmt = (
            pg_insert(Repository)
            .values(**repo_data)
            .on_conflict_do_update(
                index_elements=["github_id"],
                set_={
                    "name": repo_data["name"],
                    "full_name": repo_data["full_name"],
                    "description": repo_data["description"],
                    "html_url": repo_data["html_url"],
                    "homepage": repo_data["homepage"],
                    "primary_language": repo_data["primary_language"],
                    "topics": repo_data["topics"],
                    "stargazers_count": repo_data["stargazers_count"],
                    "forks_count": repo_data["forks_count"],
                    "is_fork": repo_data["is_fork"],
                    "is_pinned": repo_data["is_pinned"],
                    "github_pushed_at": repo_data["github_pushed_at"],
                    "github_updated_at": repo_data["github_updated_at"],
                    "updated_at": func.now(),
                },
            )
        )
        await session.execute(stmt)


async def seed_cache_metadata(session) -> None:
    """Seed cache metadata entry."""
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=1)
    
    cache_data = {
        "cache_key": "github_repos",
        "fetched_at": now,
        "expires_at": expires_at,
        "http_status": 200,
        "record_count": 3,
    }
    
    stmt = (
        pg_insert(CacheMetadata)
        .values(**cache_data)
        .on_conflict_do_update(
            index_elements=["cache_key"],
            set_={
                "fetched_at": cache_data["fetched_at"],
                "expires_at": cache_data["expires_at"],
                "http_status": cache_data["http_status"],
                "record_count": cache_data["record_count"],
                "updated_at": func.now(),
            },
        )
    )
    await session.execute(stmt)


async def run_seeds() -> None:
    """
    Idempotent seed runner. Safe to call on every container startup.
    """
    async with AsyncSessionLocal() as session:
        try:
            await seed_repositories(session)
            await seed_cache_metadata(session)
            await session.commit()
            print("✓ Seed data inserted successfully")
        except Exception as e:
            await session.rollback()
            print(f"✗ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_seeds())
