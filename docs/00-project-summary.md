# Project Summary: Luis Alarcon Personal Portfolio

## Overview

This is a personal portfolio website for Luis Alarcon, a full-stack and AI engineer in the Gauntlet AI program in Austin, TX. The site automatically fetches all public GitHub repositories from the `luisalarcon-gauntlet` account via the GitHub API and displays them in a clean, dark-themed grid. The entire system runs in Docker containers with a single `docker-compose up` command.

## Architecture

### Stack

- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.11), async SQLAlchemy, httpx
- **Database**: PostgreSQL 16.3
- **Infrastructure**: Docker + docker-compose (monorepo)
- **Authentication**: JWT (implemented but not required for v1 public access)

### Service Architecture

The project is organized as a monorepo with three main services:

1. **Frontend** (`frontend/`) - Next.js application serving the portfolio UI
2. **Backend** (`backend/`) - FastAPI application that proxies GitHub API and manages caching
3. **Database** (`db/`) - PostgreSQL database storing cached GitHub API responses

All services communicate via a Docker bridge network (`portfolio_net`).

## Key Features

### 1. Hero Section
- Displays name, title ("Full-Stack & AI Engineer"), and bio
- Links to GitHub and LinkedIn profiles
- Full-viewport-height section with dark theme

### 2. Projects Grid
- Automatically fetches all public repos from `luisalarcon-gauntlet` GitHub account
- Displays each repo as a card with:
  - Name, description, primary language
  - Topic tags, star count
  - Last updated date (human-readable)
  - Link to GitHub repository
- Sorted by pinned repos first, then by most recently updated
- Responsive grid: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)

### 3. About Section
- Short bio paragraph referencing Gauntlet AI program and Austin, TX
- Download resume link

### 4. Contact Section
- Email mailto link
- GitHub and LinkedIn social links
- Footer with copyright

## Core Design Decisions

### 1. FastAPI as Caching Proxy

**Decision**: FastAPI backend sits between frontend and GitHub API, caching responses in Postgres.

**Why**: GitHub's unauthenticated API rate limit is 60 requests/hour. Without caching, the frontend would exhaust this limit almost immediately. The backend checks Postgres cache first and only calls GitHub API when cache is stale (60-minute TTL).

### 2. Postgres for Cache Storage

**Decision**: Use Postgres tables instead of Redis for caching.

**Why**: 
- Cache TTL is measured in hours (not milliseconds), so Postgres is fully sufficient
- Reduces infrastructure complexity (one less service)
- Keeps the stack to exactly three containers
- Cache data is structured (repositories, profiles) and benefits from relational queries

### 3. Structured Cache Tables

**Decision**: Store cached data in normalized tables (`repositories`, `profiles`) rather than JSONB blobs.

**Why**:
- Easier to query and sort (e.g., by `updated_at`, `is_pinned`)
- Better type safety with SQLAlchemy models
- Supports indexes for performance
- Follows database design best practices

### 4. UUID Primary Keys

**Decision**: All tables use UUID primary keys instead of auto-increment integers.

**Why**:
- Per project database rules: "All tables must use UUID primary keys generated server-side"
- Better for distributed systems (no ID conflicts)
- More secure (non-sequential IDs)

### 5. Authentication Layer (Implemented but Not Required)

**Decision**: JWT authentication was implemented even though v1 doesn't require it.

**Why**:
- Provides foundation for future admin features
- Demonstrates complete auth flow (register → login → protected routes)
- Enables protected endpoints like `/cache/refresh` for manual cache updates
- Frontend stores tokens in memory only (per security rules)

### 6. Next.js App Router

**Decision**: Use Next.js 14 App Router with TypeScript.

**Why**:
- SEO-friendly server-side rendering
- Modern React patterns
- Built-in routing and layout support
- Deployable to Vercel or Docker

### 7. Dark Theme Only

**Decision**: Single dark theme, no light/dark toggle.

**Why**:
- Matches Luis's personal brand
- Simpler implementation (no theme switching logic)
- Consistent visual identity
- Per project rules: "Dark theme is default, no toggle switch"

### 8. Single-Page Layout

**Decision**: All sections on one page with anchor navigation.

**Why**:
- Simpler routing (no need for multiple pages)
- Better UX for portfolio (all content visible)
- Smooth scroll navigation between sections
- Per project rules: "Single-page layout. No routing needed beyond `/` in v1"

## Database Schema

### Tables

1. **repositories** - Cached GitHub repository data
   - Primary key: `id` (UUID)
   - Unique constraints: `github_id`, `full_name`
   - Fields: name, description, language, topics, stars, forks, timestamps
   - Index on `(is_pinned, github_pushed_at)` for sorting

2. **cache_metadata** - TTL tracking for cache entries
   - Primary key: `id` (UUID)
   - Unique constraint: `cache_key`
   - Tracks: `fetched_at`, `expires_at`, `http_status`, `record_count`

3. **users** - User accounts for authentication
   - Primary key: `id` (UUID)
   - Unique constraint: `email` (indexed)
   - Fields: email, hashed_password (bcrypt)

4. **profiles** - Cached GitHub user profile data
   - Primary key: `id` (UUID)
   - Unique constraint: `login`
   - Fields: name, bio, avatar_url, html_url, stats (repos, followers, following)

All tables include `created_at` and `updated_at` timestamps (timezone-aware).

## API Endpoints

### Public Endpoints

- `GET /api/health` - Health check with database status
- `GET /repos` - List all cached repositories
- `GET /repos/{repo_name}` - Get single repository by name
- `GET /profile` - Get GitHub user profile

### Protected Endpoints (Require JWT)

- `POST /cache/refresh` - Manually refresh cache from GitHub API

### Authentication Endpoints

- `POST /auth/register` - Create new user account
- `POST /auth/login` - Authenticate and receive JWT token

All endpoints return data in standard envelope format: `{"data": {}, "error": null}`

## Caching Strategy

### Cache Flow

1. **First Request**: Cache miss → Fetch from GitHub API → Store in Postgres → Return data
2. **Subsequent Requests**: Cache hit (if within TTL) → Return from Postgres (no GitHub API call)
3. **Stale Cache**: Cache expired → Fetch from GitHub API → Update Postgres → Return fresh data
4. **GitHub API Failure**: Return stale cache if available (graceful degradation)

### Cache TTL

- Default: 60 minutes (configurable via `CACHE_TTL_MINUTES` env var)
- Tracks `fetched_at` and `expires_at` in `cache_metadata` table
- Each cache entry has its own expiration timestamp

### Cache Keys

- `repos:luisalarcon-gauntlet` - Repository list cache
- `profile:luisalarcon-gauntlet` - Profile cache

## Docker Configuration

### Services

1. **db** (PostgreSQL)
   - Image: `postgres:16.3-alpine`
   - Port: 5432 (internal only)
   - Volume: `postgres_data` for persistence
   - Health check: `pg_isready`

2. **backend** (FastAPI)
   - Build: `./backend/Dockerfile`
   - Port: 8000 (exposed to host)
   - Depends on: `db` (waits for health check)
   - Health check: `curl http://localhost:8000/api/health`

3. **frontend** (Next.js)
   - Build: `./frontend/Dockerfile`
   - Port: 3000 (exposed to host)
   - Depends on: `backend` (waits for health check)
   - Health check: `curl http://localhost:3000/`

### Startup Order

1. `db` starts and becomes healthy
2. `backend` starts (waits for `db` health check)
3. `frontend` starts (waits for `backend` health check)

### Network

All services communicate via `portfolio_net` bridge network:
- Frontend → Backend: `http://backend:8000`
- Backend → Database: `postgresql+asyncpg://postgres:password@db:5432/dbname`

## Environment Variables

### Required

- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `DATABASE_URL` - Full database connection string
- `SECRET_KEY` - JWT signing key
- `GITHUB_USERNAME` - GitHub username (default: `luisalarcon-gauntlet`)
- `NEXT_PUBLIC_API_URL` - Backend API URL for frontend

### Optional

- `GITHUB_TOKEN` - GitHub API token (for higher rate limits)
- `CACHE_TTL_MINUTES` - Cache TTL in minutes (default: 60)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT expiration (default: 30)

## Testing Strategy

### Backend Integration Tests

- Use real FastAPI app and real PostgreSQL database
- Make real GitHub API calls (no mocks)
- Verify cache hit/miss behavior
- Test database state changes

### Frontend Integration Tests

- Use React Testing Library
- Mock API calls with MSW (Mock Service Worker)
- Test component rendering and user interactions
- Verify all acceptance criteria

### Test Coverage

- **Total Acceptance Criteria**: 50
- **Covered by Integration Tests**: 42 (84%)
- **Requires E2E/Docker Verification**: 8 (16%)

## What Was Deferred (v1)

The following features were explicitly deferred from v1:

- **Pinned repo detection via GraphQL** - Uses REST API with heuristic sorting
- **Mobile-specific layouts** - Responsive CSS via Tailwind breakpoints is sufficient
- **Animations and transitions** - Static renders only, simple hover states
- **Accessibility audit** - Semantic HTML and alt text baseline only
- **Dark mode toggle** - Dark theme is default, no toggle switch
- **Analytics** - No tracking scripts or analytics integrations
- **Blog or writing section** - Not in scope
- **Custom domain setup** - Deployment targeting Vercel default domain
- **Complex error recovery** - Basic error messages, no retry logic
- **Contact form** - Email link only, no form submission

## How to Run

### Prerequisites

- Docker and docker-compose installed
- `.env` file created from `.env.example`

### Start All Services

```bash
docker-compose up --build
```

This single command:
1. Builds all Docker images
2. Starts PostgreSQL database
3. Runs Alembic migrations automatically
4. Starts FastAPI backend
5. Starts Next.js frontend

### Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **Repos Endpoint**: http://localhost:8000/repos

### Verify Health

```bash
# Check all services are healthy
docker-compose ps

# Test backend health
curl http://localhost:8000/api/health

# Test repos endpoint
curl http://localhost:8000/repos
```

## Development Workflow

### Agent 1: Environment Setup
- Created monorepo structure
- Set up Dockerfiles and docker-compose.yml
- Created minimal FastAPI and Next.js scaffolds

### Agent 2: Database Schema
- Created Alembic migrations
- Defined SQLAlchemy models
- Set up database connection and session management

### Agent 3: Authentication
- Implemented JWT authentication
- Created user registration and login endpoints
- Added protected route dependency

### Agent 4: Backend API
- Implemented GitHub API integration
- Created caching logic with Postgres
- Built all feature endpoints (repos, profile, cache refresh)

### Agent 5: Frontend UI
- Built all UI components (Hero, Projects, About, Contact)
- Integrated with backend API
- Implemented auth flow (register, login, protected page)

### Agent 6: Integration Tests
- Wrote comprehensive integration tests
- Verified all acceptance criteria
- Documented test coverage

### Agent 7: Code Review
- Removed unused imports and dead code
- Standardized import order
- Ensured naming consistency

## Project Structure

```
/
├── frontend/              # Next.js application
│   ├── app/              # App Router pages and layouts
│   ├── components/       # React components
│   ├── lib/             # API client
│   ├── context/         # Auth context
│   ├── types/           # TypeScript types
│   └── tests/           # Integration tests
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py      # FastAPI app and routes
│   │   ├── routers/     # API route handlers
│   │   ├── services/    # Business logic
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── db/          # Database session
│   │   ├── core/        # Configuration
│   │   └── dependencies.py
│   └── tests/           # Integration tests
├── db/                   # Database migrations
│   └── migrations/
│       └── versions/    # Alembic migration files
├── docs/                 # Documentation
├── docker-compose.yml    # Service orchestration
├── .env.example         # Environment variable template
└── agent.md             # Agent execution guide
```

## Key Files

- `docker-compose.yml` - Service definitions and networking
- `backend/Dockerfile` - Multi-stage FastAPI build
- `frontend/Dockerfile` - Multi-stage Next.js build
- `backend/app/main.py` - FastAPI application entry point
- `frontend/app/page.tsx` - Portfolio home page
- `db/migrations/` - Alembic migration files
- `.cursor/rules/` - Project coding rules and conventions

## Security Considerations

1. **JWT Tokens**: Stored in memory only (React state), never in localStorage or cookies
2. **Passwords**: Hashed with bcrypt before storage
3. **Database**: Non-root users in Docker containers
4. **Secrets**: All passed via environment variables, never hardcoded
5. **CORS**: Configured for frontend origin only

## Performance

- **Cache Response Time**: < 500ms when serving from cache
- **GitHub API Calls**: Minimized via 60-minute cache TTL
- **Database Queries**: Indexed for fast sorting and lookups
- **Frontend**: Next.js standalone build for minimal bundle size

## Future Enhancements (Post-v1)

- Pinned repo detection via GitHub GraphQL API
- Dark/light mode toggle
- Contact form with email delivery
- Analytics integration
- Blog or writing section
- Custom domain configuration
- Advanced error recovery and retry logic
- Rate limiting on backend endpoints
- Webhook-based cache invalidation
