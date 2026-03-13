# Database Schema (Agent 2)

## Summary

Agent 2 created the complete database schema for the portfolio project using Alembic migrations and SQLAlchemy models. The schema includes tables for caching GitHub repository data, tracking cache metadata, storing user accounts for authentication, and caching GitHub profile information. All tables follow project conventions: UUID primary keys, timezone-aware timestamps, and proper indexes.

## What Was Built

### Alembic Migration Setup

- **Alembic configuration** (`db/alembic.ini`) - Database migration tool configuration
- **Migration environment** (`db/migrations/env.py`) - Alembic environment setup
- **Migration versions directory** (`db/migrations/versions/`) - All migration files

### Migration Files

#### 001: Create Repositories Table

**File**: `db/migrations/versions/001_create_repositories_table.py`

Created `repositories` table with:
- **Primary key**: `id` (UUID, auto-generated)
- **GitHub fields**: `github_id` (unique), `name`, `full_name` (unique), `description`, `html_url`, `homepage`
- **Language and topics**: `primary_language`, `topics` (PostgreSQL array)
- **Stats**: `stargazers_count`, `forks_count`, `is_fork`, `is_pinned`
- **Timestamps**: `github_pushed_at`, `github_updated_at`, `created_at`, `updated_at`
- **Constraints**: Unique on `github_id` and `full_name`

#### 002: Create Cache Metadata Table

**File**: `db/migrations/versions/002_create_cache_metadata_table.py`

Created `cache_metadata` table with:
- **Primary key**: `id` (UUID, auto-generated)
- **Cache tracking**: `cache_key` (unique), `fetched_at`, `expires_at`
- **Response metadata**: `http_status`, `record_count`
- **Timestamps**: `created_at`, `updated_at`
- **Constraint**: Unique on `cache_key`

#### 003: Create Indexes

**File**: `db/migrations/versions/003_create_indexes.py`

Created composite index for repository sorting:
- **Index name**: `idx_repositories_sort`
- **Table**: `repositories`
- **Columns**: `is_pinned` (DESC), `github_pushed_at` (DESC)
- **Purpose**: Optimize queries for projects grid sorting (pinned first, then by most recently pushed)

#### 004: Create Users Table

**File**: `db/migrations/versions/004_create_users_table.py`

Created `users` table with:
- **Primary key**: `id` (UUID, auto-generated)
- **Authentication**: `email` (unique, indexed), `hashed_password`
- **Timestamps**: `created_at`, `updated_at`
- **Index**: `ix_users_email` on `email` column for fast login lookups

#### 005: Create Profiles Table

**File**: `db/migrations/versions/005_create_profiles_table.py`

Created `profiles` table with:
- **Primary key**: `id` (UUID, auto-generated)
- **GitHub profile fields**: `login` (unique), `name`, `bio`, `avatar_url`, `html_url`
- **Stats**: `public_repos`, `followers`, `following`, `location`
- **Timestamps**: `created_at`, `updated_at`
- **Constraint**: Unique on `login`

### SQLAlchemy Models

#### Base Model Classes

**File**: `backend/app/models/base.py`

Created base classes for all models:
- **`Base`**: SQLAlchemy declarative base (all models inherit from this)
- **`UUIDMixin`**: Adds UUID primary key column named `id`
- **`TimestampMixin`**: Adds `created_at` and `updated_at` columns (timezone-aware)

#### Repository Model

**File**: `backend/app/models/repository.py`

SQLAlchemy model for `repositories` table:
- Inherits from `Base`, `UUIDMixin`, `TimestampMixin`
- Maps all columns from migration 001
- Uses PostgreSQL `ARRAY` type for `topics` field
- Includes relationships and query helpers

#### Cache Metadata Model

**File**: `backend/app/models/cache_metadata.py`

SQLAlchemy model for `cache_metadata` table:
- Inherits from `Base`, `UUIDMixin`, `TimestampMixin`
- Maps all columns from migration 002
- Provides methods for checking cache validity

#### User Model

**File**: `backend/app/models/user.py`

SQLAlchemy model for `users` table:
- Inherits from `Base`, `UUIDMixin`, `TimestampMixin`
- Maps all columns from migration 004
- Used by authentication system (Agent 3)

#### Profile Model

**File**: `backend/app/models/profile.py`

SQLAlchemy model for `profiles` table:
- Inherits from `Base`, `UUIDMixin`, `TimestampMixin`
- Maps all columns from migration 005
- Used for caching GitHub user profile data

### Database Session Management

**File**: `backend/app/db/session.py`

Created async database session management:
- **`AsyncSessionLocal`**: Async session factory using `async_sessionmaker`
- **`get_db()`**: FastAPI dependency that yields database session
- **Connection handling**: Automatic commit on success, rollback on exception
- **Engine configuration**: Uses `postgresql+asyncpg://` driver

## Key Decisions Made

### 1. UUID Primary Keys

**Decision**: All tables use UUID primary keys instead of auto-increment integers.

**Why**:
- Per project database rules: "All tables must use UUID primary keys generated server-side"
- Better for distributed systems (no ID conflicts)
- More secure (non-sequential IDs)
- Generated server-side via `gen_random_uuid()` in migrations

### 2. Structured Cache Tables

**Decision**: Store cached data in normalized tables (`repositories`, `profiles`) rather than JSONB blobs.

**Why**:
- Easier to query and sort (e.g., by `updated_at`, `is_pinned`)
- Better type safety with SQLAlchemy models
- Supports indexes for performance
- Follows database design best practices
- Allows relational queries (e.g., join repositories with cache metadata)

### 3. Separate Cache Metadata Table

**Decision**: Create `cache_metadata` table separate from cached data tables.

**Why**:
- Tracks TTL information (`fetched_at`, `expires_at`) independently
- Supports multiple cache keys (repos, profile, etc.)
- Stores HTTP status and record count for debugging
- Allows checking cache validity without querying large data tables
- Follows separation of concerns principle

### 4. Timezone-Aware Timestamps

**Decision**: All timestamp columns use `TIMESTAMP WITH TIME ZONE`.

**Why**:
- Per project database rules: "Every table must include `created_at` and `updated_at` columns. Both columns are `TIMESTAMP WITH TIME ZONE`"
- Prevents timezone-related bugs
- Ensures consistent timestamp handling across timezones
- Required by `.cursor/rules/db.mdc`

### 5. Composite Index for Sorting

**Decision**: Create composite index on `(is_pinned, github_pushed_at)` with DESC ordering.

**Why**:
- Optimizes the most common query pattern: "get all repos, sorted by pinned first, then by most recently pushed"
- Projects grid needs this exact sort order
- Index supports efficient sorting without full table scan
- PostgreSQL supports index ordering (DESC) for optimal performance

### 6. Array Type for Topics

**Decision**: Use PostgreSQL `ARRAY(String)` type for repository topics.

**Why**:
- Native PostgreSQL array type is efficient
- Easier to query (e.g., "find repos with topic 'python'")
- No need for separate junction table for simple tags
- Matches GitHub API response structure

### 7. Unique Constraints

**Decision**: Add unique constraints on `github_id`, `full_name`, `email`, `login`, `cache_key`.

**Why**:
- Prevents duplicate data from GitHub API
- Ensures data integrity
- Supports upsert operations (ON CONFLICT DO UPDATE)
- Required by `.cursor/rules/db.mdc` naming convention (`uq_<table>_<column>`)

### 8. Async SQLAlchemy

**Decision**: Use async SQLAlchemy (`AsyncSession`) throughout.

**Why**:
- FastAPI is async by default
- Better performance for I/O-bound operations
- Required by `.cursor/rules/db.mdc`
- Uses `asyncpg` driver for PostgreSQL async support

### 9. Alembic for Migrations

**Decision**: Use Alembic for all database schema changes.

**Why**:
- Industry standard for SQLAlchemy projects
- Version-controlled migrations
- Reversible migrations (upgrade/downgrade)
- Required by `.cursor/rules/db.mdc`
- Supports automatic migration generation

### 10. Server-Side Defaults

**Decision**: Use `server_default` for timestamps and UUIDs in migrations.

**Why**:
- Ensures database generates values, not application code
- Consistent behavior across all inserts
- Required by `.cursor/rules/db.mdc`
- Prevents timezone issues with application-generated timestamps

## What Was Skipped/Deferred

1. **Seed data**: No seed scripts created (data comes from GitHub API at runtime)
2. **Database connection pooling**: Uses SQLAlchemy default pooling (sufficient for v1)
3. **Read replicas**: Single database instance (no read/write splitting)
4. **Database backups**: Not implemented (out of scope for v1)
5. **Migration rollback testing**: Migrations are reversible but not tested in CI

## Problems Encountered and Resolved

### Problem 1: Async SQLAlchemy Session Setup

**Issue**: Needed to configure async SQLAlchemy properly for FastAPI.

**Resolution**: Created `AsyncSessionLocal` using `async_sessionmaker` with `create_async_engine` and `postgresql+asyncpg://` driver. Used FastAPI dependency injection pattern for session management.

### Problem 2: Timestamp Timezone Handling

**Issue**: Needed to ensure all timestamps are timezone-aware.

**Resolution**: Used `DateTime(timezone=True)` in all SQLAlchemy column definitions and `TIMESTAMP WITH TIME ZONE` in migrations. Set `server_default=func.now()` to let database handle timezone-aware defaults.

### Problem 3: UUID Generation

**Issue**: Needed to generate UUIDs server-side in migrations.

**Resolution**: Used `server_default=sa.text('gen_random_uuid()')` in migrations to let PostgreSQL generate UUIDs. SQLAlchemy models use `default=uuid.uuid4` as fallback for application-generated UUIDs.

### Problem 4: Array Type for Topics

**Issue**: Needed to store array of strings for repository topics.

**Resolution**: Used PostgreSQL `ARRAY(String)` type with `postgresql.ARRAY(sa.String())` in SQLAlchemy. Set `server_default='{}'` for empty array default.

## Database Schema Overview

### Tables

1. **repositories** - Cached GitHub repository data
   - Primary key: `id` (UUID)
   - Unique: `github_id`, `full_name`
   - Index: `idx_repositories_sort` on `(is_pinned DESC, github_pushed_at DESC)`

2. **cache_metadata** - TTL tracking for cache entries
   - Primary key: `id` (UUID)
   - Unique: `cache_key`
   - Tracks: `fetched_at`, `expires_at`, `http_status`, `record_count`

3. **users** - User accounts for authentication
   - Primary key: `id` (UUID)
   - Unique: `email` (indexed)
   - Fields: `email`, `hashed_password`

4. **profiles** - Cached GitHub user profile data
   - Primary key: `id` (UUID)
   - Unique: `login`
   - Fields: `name`, `bio`, `avatar_url`, `html_url`, stats

All tables include `created_at` and `updated_at` timestamps (timezone-aware).

## Migration Execution

Migrations run automatically on container startup via backend entrypoint script:
```bash
alembic upgrade head
```

This ensures database schema is always up-to-date when backend container starts.

## Next Steps

Database schema is complete and ready for:
- **Agent 3**: Authentication layer (uses `users` table)
- **Agent 4**: Backend API (uses `repositories`, `cache_metadata`, `profiles` tables)
- **Agent 5**: Frontend UI (reads from cached data via API)
