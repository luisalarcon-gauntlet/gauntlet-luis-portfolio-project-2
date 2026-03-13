# Agent Execution Plan: Luis Alarcon Personal Portfolio

---

## Agent 1: Environment & Infrastructure

### What It Builds
The complete monorepo scaffolding with Docker containers for the Next.js frontend, FastAPI backend, and Postgres database. Sets up docker-compose networking, environment variable structure, and verifies all three services start and communicate.

### Step-by-Step Instructions

1. **Create monorepo directory structure:**
   ```
   portfolio/
   ├── docker-compose.yml
   ├── .env.example
   ├── frontend/
   │   ├── Dockerfile
   │   └── (Next.js app scaffold)
   ├── backend/
   │   ├── Dockerfile
   │   └── (FastAPI app scaffold)
   └── README.md
   ```

2. **Write `docker-compose.yml`** with three services:
   - `db`: postgres:15-alpine, port 5432, volume `pgdata`, env vars `POSTGRES_DB=portfolio`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
   - `backend`: FastAPI, port 8000, depends_on `db`, mounts `./backend`, env vars for `DATABASE_URL`, `GITHUB_USERNAME=luisalarcon-gauntlet`, optional `GITHUB_TOKEN`
   - `frontend`: Next.js, port 3000, depends_on `backend`, env var `NEXT_PUBLIC_API_URL=http://localhost:8000`

3. **Write `backend/Dockerfile`:**
   - Base: `python:3.11-slim`
   - Install dependencies from `requirements.txt`
   - `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]`

4. **Write `frontend/Dockerfile`:**
   - Base: `node:20-alpine`
   - Install deps, expose port 3000
   - `CMD ["npm", "run", "dev"]` for dev stage

5. **Scaffold minimal FastAPI `backend/main.py`:**
   ```python
   from fastapi import FastAPI
   app = FastAPI()

   @app.get("/health")
   def health():
       return {"status": "ok"}
   ```

6. **Scaffold minimal Next.js app** using `create-next-app` with TypeScript, App Router, Tailwind CSS:
   - `frontend/app/page.tsx` returns `<h1>Portfolio</h1>`

7. **Write `backend/requirements.txt`:**
   ```
   fastapi
   uvicorn[standard]
   psycopg2-binary
   httpx
   python-dotenv
   ```

8. **Write `.env.example`:**
   ```
   POSTGRES_USER=luis
   POSTGRES_PASSWORD=password
   POSTGRES_DB=portfolio
   DATABASE_URL=postgresql://luis:password@db:5432/portfolio
   GITHUB_USERNAME=luisalarcon-gauntlet
   GITHUB_TOKEN=
   ```

9. **Copy `.env.example` to `.env`** and fill in local values.

10. **Run `docker-compose up --build`** and confirm all three containers start without errors.

### Verification Checklist
- [ ] `docker-compose up --build` completes with no exit errors on any container
- [ ] `curl http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] `curl http://localhost:3000` returns an HTML page with "Portfolio"
- [ ] `docker exec <db_container> psql -U luis -d portfolio -c "\l"` shows `portfolio` database
- [ ] Backend container resolves `db` hostname (verify with `docker exec backend ping db`)
- [ ] `.env` is in `.gitignore`

### Handoff Condition
All three services (`db`, `backend`, `frontend`) start successfully via `docker-compose up` and respond to basic health checks. Directory structure is in place for Agent 2 to add migrations.

---

## Agent 2: Database Schema & Migrations

### What It Builds
The Postgres schema for caching GitHub API responses. Creates the `repositories` table and `cache_metadata` table. Implements a raw SQL migration script run on backend startup. No ORM — raw psycopg2 for simplicity.

### Step-by-Step Instructions

1. **Create `backend/db.py`** — database connection module:
   ```python
   import psycopg2
   import os

   def get_connection():
       return psycopg2.connect(os.environ["DATABASE_URL"])
   ```

2. **Create `backend/migrations/001_initial.sql`** with the following tables:

   **`repositories` table** — stores cached GitHub repo data:
   ```sql
   CREATE TABLE IF NOT EXISTS repositories (
       id BIGINT PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       description TEXT,
       html_url TEXT NOT NULL,
       homepage TEXT,
       primary_language VARCHAR(100),
       topics TEXT[],
       stargazers_count INTEGER DEFAULT 0,
       forks_count INTEGER DEFAULT 0,
       pushed_at TIMESTAMPTZ,
       updated_at TIMESTAMPTZ,
       is_pinned BOOLEAN DEFAULT FALSE,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

   **`cache_metadata` table** — tracks when GitHub was last fetched:
   ```sql
   CREATE TABLE IF NOT EXISTS cache_metadata (
       key VARCHAR(100) PRIMARY KEY,
       last_fetched_at TIMESTAMPTZ NOT NULL,
       etag VARCHAR(255)
   );
   ```

3. **Create `backend/migrate.py`** — reads and executes the SQL file:
   ```python
   import os
   from db import get_connection

   def run_migrations():
       conn = get_connection()
       cur = conn.cursor()
       migration_path = os.path.join(os.path.dirname(__file__), "migrations/001_initial.sql")
       with open(migration_path, "r") as f:
           cur.execute(f.read())
       conn.commit()
       cur.close()
       conn.close()
   ```

4. **Call `run_migrations()` in `backend/main.py`** on app startup using FastAPI's `lifespan` context:
   ```python
   from contextlib import asynccontextmanager
   from migrate import run_migrations

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       run_migrations()
       yield

   app = FastAPI(lifespan=lifespan)
   ```

5. **Rebuild and restart** with `docker-compose up --build`.

6. **Verify schema** by connecting to Postgres and confirming tables exist.

### Verification Checklist
- [ ] `docker-compose up` starts backend without migration errors in logs
- [ ] `docker exec <db_container> psql -U luis -d portfolio -c "\dt"` shows `repositories` and `cache_metadata` tables
- [ ] `repositories` table has columns: `id`, `name`, `description`, `html_url`, `primary_language`, `topics`, `stargazers_count`, `pushed_at`, `is_pinned`
- [ ] `cache_metadata` table has columns: `key`, `last_fetched_at`, `etag`
- [ ] Re-running migrations (restarting backend) does not throw errors (idempotent via `CREATE TABLE IF NOT EXISTS`)
- [ ] Manual insert and select on `repositories` table succeeds

### Handoff Condition
Both tables exist in Postgres, migrations run automatically on backend startup, and the schema matches the spec for caching GitHub API repo data. Agent 3 is skipped per spec (no auth in v1 — out of scope).

---

## Agent 3: Auth Layer

### What It Builds
Per the project spec, authentication is **explicitly out of scope for v1**. There is no admin panel, no login, and no protected routes. This agent installs JWT dependencies as a stub for future use but takes no implementation action.

### Step-by-Step Instructions

1. **Confirm in spec:** "Out of scope for v1: Authentication or admin panel" — no action needed.

2. **Add `python-jose[cryptography]` to `requirements.txt`** as a placeholder for future JWT use — do not implement any routes or middleware.

3. **Add a comment block in `backend/main.py`:**
   ```python
   # Auth: Not implemented in v1 per spec. JWT stub only.
   ```

4. **Document in `README.md`:** "Auth is out of scope for v1. No protected routes exist."

### Verification Checklist
- [ ] No `/auth`, `/login`, or `/token` routes exist in the backend
- [ ] `docker-compose up` still passes the Agent 1 health check
- [ ] `requirements.txt` includes `python-jose[cryptography]` as a future stub
- [ ] No middleware intercepts any existing routes

### Handoff Condition
Confirmed no auth implementation. Backend still healthy. Agent 4 can build all API routes as fully public.

---

## Agent 4: Backend API

### What It Builds
The FastAPI routes that fetch GitHub repositories for `luisalarcon-gauntlet`, cache results in Postgres, serve cached data to the frontend, and implement TTL-based cache invalidation to stay within GitHub's 60 req/hour unauthenticated rate limit.

### Step-by-Step Instructions

1. **Create `backend/github_client.py`** — async HTTP client using `httpx`:
   ```python
   import httpx
   import os

   GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "luisalarcon-gauntlet")
   GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
   BASE_URL = "https://api.github.com"

   def get_headers():
       headers = {"Accept": "application/vnd.github+json"}
       if GITHUB_TOKEN:
           headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
       return headers

   async def fetch_repos():
       async with httpx.AsyncClient() as client:
           response = await client.get(
               f"{BASE_URL}/users/{GITHUB_USERNAME}/repos",
               params={"per_page": 100, "sort": "updated"},
               headers=get_headers()
           )
           response.raise_for_status()
           return response.json()

   async def fetch_pinned_repos():
       # GitHub pinned repos require GraphQL API
       # For v1: mark top 6 by stars as "pinned" — happy path only
       return []
   ```

2. **Create `backend/cache.py`** — read/write cache logic with 1-hour TTL:
   ```python
   from db import get_connection
   from datetime import datetime, timezone, timedelta

   CACHE_TTL_MINUTES = 55  # Under the 60 req/hour limit

   def get_cached_repos():
       conn = get_connection()
       cur = conn.cursor()
       # Check if cache is still valid
       cur.execute("SELECT last_fetched_at FROM cache_metadata WHERE key = 'github_repos'")
       row = cur.fetchone()
       if row:
           last_fetched = row[0]
           if datetime.now(timezone.utc) - last_fetched < timedelta(minutes=CACHE_TTL_MINUTES):
               cur.execute("SELECT id, name, description, html_url, homepage, primary_language, topics, stargazers_count, forks_count, pushed_at, updated_at, is_pinned FROM repositories ORDER BY is_pinned DESC, pushed_at DESC NULLS LAST")
               repos = cur.fetchall()
               cur.close()
               conn.close()
               return repos  # cache hit
       cur.close()
       conn.close()
       return None  # cache miss

   def save_repos_to_cache(repos: list):
       conn = get_connection()
       cur = conn.cursor()
       # Upsert each repo
       for repo in repos:
           cur.execute("""
               INSERT INTO repositories (id, name, description, html_url, homepage, primary_language, topics, stargazers_count, forks_count, pushed_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO UPDATE SET
                   name = EXCLUDED.name,
                   description = EXCLUDED.description,
                   primary_language = EXCLUDED.primary_language,
                   topics = EXCLUDED.topics,
                   stargazers_count = EXCLUDED.stargazers_count,
                   forks_count = EXCLUDED.forks_count,
                   pushed_at = EXCLUDED.pushed_at,
                   updated_at = EXCLUDED.updated_at
           """, (
               repo["id"], repo["name"], repo.get("description"),
               repo["html_url"], repo.get("homepage"),
               repo.get("language"), repo.get("topics", []),
               repo["stargazers_count"], repo["forks_count"],
               repo.get("pushed_at"), repo.get("updated_at")
           ))
       # Update cache metadata
       cur.execute("""
           INSERT INTO cache_metadata (key, last_fetched_at)
           VALUES ('github_repos', NOW())
           ON CONFLICT (key) DO UPDATE SET last_fetched_at = NOW()
       """)
       conn.commit()
       cur.close()
       conn.close()
   ```

3. **Create `backend/routers/repos.py`** — the repos endpoint:
   ```python
   from fastapi import APIRouter
   from cache import get_cached_repos, save_repos_to_cache
   from github_client import fetch_repos

   router = APIRouter(prefix="/api", tags=["repos"])

   @router.get("/repos")
   async def get_repos():
       cached = get_cached_repos()
       if cached:
           return {"source": "cache", "repos": format_repos(cached)}
       raw = await fetch_repos()
       save_repos_to_cache(raw)
       return {"source": "github", "repos": format_from_raw(raw)}

   def format_repos(rows):
       keys = ["id","name","description","html_url","homepage","primary_language","topics","stargazers_count","forks_count","pushed_at","updated_at","is_pinned"]
       return [dict(zip(keys, row)) for row in rows]

   def format_from_raw(repos):
       return [
           {
               "id": r["id"],
               "name": r["name"],
               "description": r.get("description"),
               "html_url": r["html_url"],
               "homepage": r.get("homepage"),
               "primary_language": r.get("language"),
               "topics": r.get("topics", []),
               "stargazers_count": r["stargazers_count"],
               "forks_count": r["forks_count"],
               "pushed_at": r.get("pushed_at"),
               "updated_at": r.get("updated_at"),
               "is_pinned": False
           }
           for r in sorted(repos, key=lambda x: x.get("pushed_at", ""), reverse=True)
       ]
   ```

4. **Register router in `backend/main.py`:**
   ```python
   from routers import repos
   app.include_router(repos.router)
   ```

5. **Add CORS middleware** to allow requests from `http://localhost:3000`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["GET"], allow_headers=["*"])
   ```

6. **Rebuild:** `docker-compose up --build`

### Verification Checklist
- [ ] `GET http://localhost:8000/api/repos` returns a JSON object with `source` and `repos` array
- [ ] `repos` array contains items with fields: `name`, `description`, `html_url`, `primary_language`, `topics`, `stargazers_count`, `pushed_at`
- [ ] Second call to `GET /api/repos` returns `"source": "cache"` (within TTL window)
- [ ] Repos are sorted by `pushed_at` descending in the response
- [ ] `docker exec <db_container> psql -U luis -d portfolio -c "SELECT COUNT(*) FROM repositories"` shows > 0 rows after first API call
- [ ] `cache_metadata` table has a row with `key = 'github_repos'`
- [ ] `GET http://localhost:8000/health