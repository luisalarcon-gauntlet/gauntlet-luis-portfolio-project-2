# Environment Setup (Agent 1)

## Summary

Agent 1 established the complete monorepo infrastructure for the Luis Alarcon Portfolio project. This included creating the folder structure, production-ready Dockerfiles for both frontend and backend services, a comprehensive docker-compose.yml configuration, and minimal application scaffolds. All components were verified to run natively before Docker containerization.

## What Was Built

### Directory Structure

- **`frontend/`** - Next.js 14 application with App Router, TypeScript, and Tailwind CSS
- **`backend/`** - FastAPI application with proper package structure
- **`db/`** - Database migrations and seeds directory (ready for Agent 2)
- **`docs/`** - Documentation directory

### Docker Infrastructure

#### `docker-compose.yml`

Created a comprehensive docker-compose configuration with:

- **Three services**: `db` (PostgreSQL 16.3-alpine), `backend` (FastAPI), `frontend` (Next.js)
- **Health checks** configured for all services with proper intervals and timeouts
- **`depends_on` with `service_healthy` conditions** ensuring proper startup order
- **Explicit bridge network** (`portfolio_net`) for service communication
- **Named volume** (`postgres_data`) for database persistence
- **Environment variable injection** via `env_file` and `environment` blocks
- **Container names** for readable logs: `portfolio_db`, `portfolio_backend`, `portfolio_frontend`
- **Restart policies**: `unless-stopped` for all services

#### `backend/Dockerfile`

Multi-stage build with:

- **Base image**: `python:3.11.10-slim-bookworm` (pinned version, no `latest` tag)
- **Three stages**: 
  - `deps` - Install Python dependencies
  - `builder` - Build stage (if needed)
  - `runner` - Final runtime image
- **Non-root user**: `appuser` in `appgroup`
- **Health check**: `curl -f http://localhost:8000/api/health`
- **Layer optimization**: Dependencies installed before source code copy
- **Security**: No secrets in Dockerfile, all via environment variables

#### `frontend/Dockerfile`

Multi-stage build with:

- **Base image**: `node:20.14.0-alpine3.20` (pinned version)
- **Three stages**:
  - `deps` - Install production dependencies only
  - `builder` - Install all dependencies and build Next.js app
  - `runner` - Copy only built output (standalone mode)
- **Non-root user**: `nextjs` in `nodejs` group
- **Next.js standalone output**: Optimized production build
- **Build args**: `NEXT_PUBLIC_API_URL` passed at build time
- **Health check**: `curl -f http://localhost:3000/`
- **Layer optimization**: Package files copied before source code

#### `.dockerignore` Files

- **`backend/.dockerignore`**: Excludes `.env`, `__pycache__/`, `*.pyc`, `.git/`, etc.
- **`frontend/.dockerignore`**: Excludes `.env`, `node_modules/`, `.next/`, `.git/`, etc.

### Backend Scaffold

#### `backend/app/main.py`

Created FastAPI application with:

- FastAPI app with proper metadata
- `/api/health` endpoint returning standard response envelope: `{"data": {"status": "ok"}, "error": null}`
- CORS middleware configured for `http://localhost:3000`
- Global exception handler returning standard error envelope
- Package structure: `app/routers/`, `app/services/`, `app/models/`, `app/schemas/`, `app/db/`

#### `backend/requirements.txt`

Pinned versions for all dependencies:
- `fastapi==0.115.0`
- `uvicorn[standard]==0.32.0`
- `httpx==0.27.2`
- `sqlalchemy==2.0.36`
- `asyncpg==0.30.0`
- `pydantic==2.9.2`
- `pydantic-settings==2.5.2`
- `python-dotenv==1.0.1`

### Frontend Scaffold

#### `frontend/app/`

- **`layout.tsx`**: Root layout with dark theme (`bg-[#0a0a0a]`), metadata, and HTML structure
- **`page.tsx`**: Minimal home page with "Portfolio" heading
- **`globals.css`**: Tailwind CSS imports

#### Configuration Files

- **`package.json`**: Next.js 14.2.19, React 18.3.1, TypeScript 5.6.2, Tailwind CSS 3.4.14
- **`tsconfig.json`**: Strict TypeScript configuration with path aliases (`@/*`)
- **`next.config.js`**: Standalone output mode for Docker optimization
- **`tailwind.config.ts`**: Dark mode enabled, content paths configured
- **`postcss.config.js`**: Tailwind and Autoprefixer plugins

### Environment Configuration

#### `.env.example`

All required environment variables documented:
- Database: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- Backend: `DATABASE_URL`, `GITHUB_USERNAME`, `GITHUB_TOKEN`, `CACHE_TTL_MINUTES`, `JWT_SECRET`, `ENVIRONMENT`
- Frontend: `NEXT_PUBLIC_API_URL`, `BACKEND_PORT`, `FRONTEND_PORT`

#### `.env`

Copied from `.env.example` with safe development defaults, added to `.gitignore` (not committed)

#### `.gitignore`

Comprehensive ignore patterns for Python, Node.js, environment files, IDE files, and build artifacts

## Key Decisions Made

### 1. Pinned Base Image Versions

**Decision**: Use specific, pinned versions for all base images (e.g., `python:3.11.10-slim-bookworm`, `node:20.14.0-alpine3.20`, `postgres:16.3-alpine`)

**Why**: 
- Ensures reproducible builds across environments
- Prevents unexpected breaking changes from `latest` tags
- Aligns with Docker best practices and security scanning requirements
- Matches the `.cursor/rules/docker.mdc` requirements

### 2. Multi-Stage Docker Builds

**Decision**: Use three-stage builds for both frontend and backend

**Why**:
- Minimizes final image size by excluding build dependencies
- Separates concerns: dependency installation → build → runtime
- Reduces attack surface in production images
- Follows industry best practices for containerized applications

### 3. Non-Root Users

**Decision**: Run both backend and frontend containers as non-root users (`appuser` and `nextjs`)

**Why**:
- Security best practice: reduces impact of container escape vulnerabilities
- Required by `.cursor/rules/docker.mdc`
- Industry standard for production containers

### 4. Health Checks with Service Dependencies

**Decision**: Use `depends_on` with `condition: service_healthy` for all service dependencies

**Why**:
- Ensures services only start when dependencies are actually ready
- Prevents race conditions during startup
- Required by `.cursor/rules/docker.mdc`
- Provides reliable startup ordering: `db` → `backend` → `frontend`

### 5. Explicit Network Configuration

**Decision**: Create explicit bridge network (`portfolio_net`) instead of using default

**Why**:
- Better isolation and control over service communication
- Makes network topology explicit in configuration
- Easier to debug and understand service relationships
- Required by `.cursor/rules/docker.mdc`

### 6. Next.js Standalone Output

**Decision**: Configure Next.js with `output: "standalone"` in `next.config.js`

**Why**:
- Creates minimal production server with only necessary files
- Reduces Docker image size significantly
- Recommended by Next.js for containerized deployments
- Simplifies Dockerfile COPY operations

### 7. FastAPI Response Envelope

**Decision**: Implement standard response envelope `{"data": {}, "error": null}` from the start

**Why**:
- Consistent API response format across all endpoints
- Required by `.cursor/rules/api-design.mdc`
- Makes error handling predictable for frontend
- Sets foundation for all future API endpoints

### 8. TypeScript Config File Format

**Decision**: Use `next.config.js` instead of `next.config.ts`

**Why**:
- Next.js 14.2.19 does not support TypeScript config files
- Discovered during native verification
- JavaScript config is fully supported and sufficient

### 9. Database URL Format

**Decision**: Use `postgresql+asyncpg://` in `DATABASE_URL` for async SQLAlchemy

**Why**:
- FastAPI uses async SQLAlchemy (`AsyncSession`)
- `asyncpg` is the recommended async PostgreSQL driver
- Required by `.cursor/rules/db.mdc` for async sessions

## What Was Skipped/Deferred

1. **No database schema yet**: Tables will be created by Agent 2 (Database Schema & Migrations)
2. **No GitHub API integration**: Backend only has `/api/health` endpoint; repos endpoint will be added by Agent 4
3. **No frontend components**: Only minimal page scaffold; Hero, Projects, About, Contact sections will be added by later agents
4. **No authentication**: JWT dependencies not added yet (out of scope for v1 per spec, but later implemented by Agent 3)
5. **Next.js security warning**: Version 14.2.19 still shows audit warning; will be addressed in future updates

## Problems Encountered and Resolved

### Problem 1: Next.js Config File Format

**Issue**: Initially attempted to use `next.config.ts` (TypeScript config file)

**Resolution**: Switched to `next.config.js` (JavaScript) as Next.js 14.2.19 does not support TypeScript config files. This was discovered during native verification.

### Problem 2: Database URL Format

**Issue**: Needed to determine correct database URL format for async SQLAlchemy

**Resolution**: Used `postgresql+asyncpg://` format as required by async SQLAlchemy and `.cursor/rules/db.mdc`. This ensures compatibility with `AsyncSession` used throughout the FastAPI application.

### Problem 3: Docker Layer Caching

**Issue**: Needed to optimize Docker builds for faster iteration

**Resolution**: Structured Dockerfiles to copy dependency manifests (`package.json`, `requirements.txt`) before source code, maximizing layer cache hits. Dependencies are installed in separate layers that only rebuild when dependency files change.

## Verification

### Native Backend Test

```bash
cd backend
pip3 install --user -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/api/health
```

**Result**: ✅ Success
- Response: `{"data":{"status":"ok"},"error":null}`
- HTTP Status: 200
- All dependencies installed correctly

### Native Frontend Test

```bash
cd frontend
npm install
npm run dev
curl http://127.0.0.1:3000
```

**Result**: ✅ Success
- HTML page loads with "Portfolio" heading
- Dark theme applied (`bg-[#0a0a0a]`)
- Tailwind CSS working correctly
- Next.js dev server running on port 3000

### Docker Verification (Not Run)

Per instructions, Dockerfiles and docker-compose.yml are deliverables but were **not run in this environment**. They have been written according to all rules in `.cursor/rules/docker.mdc`:

- ✅ Pinned base images (no `latest` tags)
- ✅ Multi-stage builds
- ✅ Non-root users
- ✅ Health checks configured
- ✅ Proper `depends_on` with `service_healthy`
- ✅ Explicit networks and volumes
- ✅ No secrets in Dockerfiles
- ✅ `.dockerignore` files present

## Next Steps

This PR provided the foundation for:
- **Agent 2**: Database schema and migrations (Alembic setup, table creation)
- **Agent 3**: Auth layer (JWT authentication, user registration/login)
- **Agent 4**: Backend API (GitHub API integration, caching logic)
- **Agent 5+**: Frontend components (Hero, Projects Grid, About, Contact)

All infrastructure is in place and ready for the next agent to build upon.
