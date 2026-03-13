# Backend API Implementation (Agent 4)

## Summary

Agent 4 implemented all feature endpoints specified in the API contracts, following TDD principles. All endpoints return data in the standard envelope format `{"data": {}, "error": null}` and include proper caching logic to respect GitHub API rate limits. The implementation includes GET /repos, GET /repos/{repo_name}, GET /profile, POST /cache/refresh (protected), and an updated GET /health endpoint with database status.

## What Was Built

### Core Services

#### GitHub Service

**File**: `backend/app/services/github_service.py`

Comprehensive service for GitHub API integration and caching:

- **`fetch_repos_from_github()`** - Fetches all public repos from GitHub API
- **`fetch_repo_from_github(repo_name)`** - Fetches single repo by name
- **`fetch_profile_from_github()`** - Fetches GitHub user profile
- **`is_cache_valid()`** - Checks if cache entry is within TTL (60 minutes)
- **`store_repos_in_cache()`** - Upserts repositories into database cache
- **`store_profile_in_cache()`** - Upserts profile into database cache
- **`get_repos_from_cache()`** - Retrieves cached repos sorted by pinned/updated_at
- **`get_repo_from_cache()`** - Retrieves single cached repo
- **`get_profile_from_cache()`** - Retrieves cached profile
- **`get_cache_metadata()`** - Gets cache metadata for TTL checking

### Pydantic Schemas

**File**: `backend/app/schemas/github.py`

Response schemas matching API contracts:
- **`RepoSchema`** - Repository response schema with all required fields
- **`RepoDetailSchema`** - Extended schema with `open_issues_count` for single repo
- **`ReposListResponse`** - Response wrapper for repos list with cache metadata
- **`RepoDetailResponse`** - Response wrapper for single repo
- **`ProfileSchema`** - GitHub profile response schema
- **`ProfileResponse`** - Response wrapper for profile with cache metadata
- **`CacheRefreshResponse`** - Response wrapper for cache refresh operation

### Database Models

#### Profile Model

**File**: `backend/app/models/profile.py`

SQLAlchemy model for caching GitHub profile data:
- Fields: login, name, bio, avatar_url, html_url, public_repos, followers, following, location
- Inherits from Base, UUIDMixin, TimestampMixin per project conventions

#### Migration

**File**: `db/migrations/versions/005_create_profiles_table.py`

Creates profiles table with:
- UUID primary key
- Unique constraint on login field
- Includes created_at and updated_at timestamps

### API Endpoints

#### GET /repos

**File**: `backend/app/routers/repos.py`

Returns all public repositories for configured GitHub user:
- Supports optional `refresh` query parameter to force cache bypass
- Returns cached data if valid (within 60-minute TTL), otherwise fetches from GitHub
- Falls back to stale cache if GitHub API fails (graceful degradation)
- Response includes: repos array, total_count, cached flag, cache_generated_at, cache_expires_at
- Repos sorted by is_pinned (desc) then updated_at (desc)

#### GET /repos/{repo_name}

**File**: `backend/app/routers/repos.py`

Returns single repository by name:
- Checks cache first, fetches from GitHub if not cached
- Returns 404 if repository not found
- Response includes: repo object with open_issues_count, cached flag, cache_generated_at

#### GET /profile

**File**: `backend/app/routers/profile.py`

Returns GitHub profile data for configured user:
- Uses same caching strategy as repos (60-minute TTL)
- Falls back to stale cache if GitHub API fails
- Response includes: profile object, cached flag, cache_generated_at, cache_expires_at

#### POST /cache/refresh

**File**: `backend/app/main.py`

Protected endpoint requiring JWT authentication:
- Manually triggers full cache refresh for both repos and profile
- Fetches fresh data from GitHub API and updates cache
- Returns: refreshed flag, repos_cached count, profile_cached flag, cache timestamps

#### GET /api/health

**File**: `backend/app/main.py`

Updated to include database connection status:
- Returns: status ("ok"), database ("connected"/"disconnected"), timestamp

### Testing

**File**: `backend/tests/`

Comprehensive test suite:
- `test_repos.py` - Tests GET /repos endpoint response shape
- `test_repo_detail.py` - Tests GET /repos/{repo_name} endpoint
- `test_profile.py` - Tests GET /profile endpoint
- `test_cache_refresh.py` - Tests POST /cache/refresh (with and without token)
- `test_health.py` - Tests GET /api/health with database status
- All tests follow TDD principles and use mocks for GitHub API calls
- Tests verify exact response shape per API contract

## Key Decisions Made

### 1. Cache Strategy

**Decision**: Use Postgres tables (repositories, profiles) with CacheMetadata table for TTL tracking.

**Why**:
- Per architecture rules: "All GitHub API responses must be cached in Postgres"
- CacheMetadata table tracks when data was fetched and when it expires
- 60-minute TTL configurable via `CACHE_TTL_MINUTES` environment variable
- Avoids hitting GitHub's 60 req/hour unauthenticated rate limit
- Structured tables allow efficient querying and sorting

### 2. Response Envelope Format

**Decision**: All endpoints return `{"data": {}, "error": null}` format.

**Why**:
- Per API design rules: "Every endpoint MUST return a consistent envelope shape. No exceptions."
- Makes error handling predictable for frontend
- Consistent with existing auth endpoints
- Allows frontend to always expect the same response structure

### 3. Cache Fallback Behavior

**Decision**: If GitHub API fails and cache exists (even if stale), return cached data.

**Why**:
- Graceful degradation - better to show stale data than no data
- Per API contract: "GitHub API unavailable and no cache" returns error, but if cache exists, use it
- Ensures portfolio remains functional even if GitHub API is down
- Provides resilience against external API failures

### 4. Repository Sorting

**Decision**: Sort by is_pinned (desc) then github_updated_at (desc).

**Why**:
- Per API contract: "pinned repos appear first"
- In v1, is_pinned defaults to False (pinned detection deferred)
- Most recently updated repos appear first after pinned ones
- Matches user expectation (most recent work first)

### 5. Single Repo Caching

**Decision**: Single repo fetches update the full repos cache.

**Why**:
- Keeps cache consistent - if a single repo is fetched, it's added to the main cache
- Avoids duplicate cache entries
- Simplifies cache management
- Ensures all repos are available in cache after single repo fetch

### 6. Profile Model

**Decision**: Created separate Profile model instead of storing in CacheMetadata.

**Why**:
- Cleaner data model - profile data is structured, not JSON blob
- Easier to query and update
- Follows same pattern as Repository model
- Per database rules: use proper SQLAlchemy models, not JSONB for structured data

### 7. Error Handling

**Decision**: Use HTTPException with standard envelope format for all errors.

**Why**:
- Per API design rules: "Raise HTTPException for all client errors"
- Global exception handler ensures envelope format even for unhandled exceptions
- Consistent error responses across all endpoints
- Makes error handling predictable for frontend

### 8. Health Check Database Status

**Decision**: Health endpoint checks database connection with simple SELECT query.

**Why**:
- Per API contract: health endpoint must include database status
- Simple check verifies database is reachable and responsive
- Returns "connected" or "disconnected" status
- Useful for monitoring and debugging

### 9. Protected Route Implementation

**Decision**: POST /cache/refresh uses existing get_current_user dependency.

**Why**:
- Reuses auth infrastructure from Agent 3
- Per API contract: cache refresh requires JWT authentication
- Consistent with other protected routes
- Demonstrates real-world use case (admin cache refresh)

### 10. Test Mocking Strategy

**Decision**: Mock GitHub API calls in tests, use real database and FastAPI app.

**Why**:
- Per TDD rules: "respx — mock outbound GitHub API HTTP calls only"
- Avoids hitting GitHub API rate limits during test runs
- Tests real application behavior with mocked external dependencies
- Uses real database to verify caching logic works correctly

### 11. Cache Metadata Tracking

**Decision**: Track cache metadata separately from cached data.

**Why**:
- Allows checking cache validity without querying large data tables
- Stores HTTP status and record count for debugging
- Supports multiple cache keys (repos, profile, etc.)
- Enables efficient TTL checking

### 12. Refresh Query Parameter

**Decision**: Support `?refresh=true` query parameter on GET /repos.

**Why**:
- Allows manual cache refresh without requiring authentication
- Useful for testing and debugging
- Provides flexibility for future admin features
- Per API contract specification

## What Was Skipped/Deferred

Per the TDD rules and API contract spec, the following are intentionally not implemented in v1:

- **Pinned repo detection** - is_pinned defaults to False (would require GraphQL API)
- **Cache TTL expiry enforcement** - Cache is checked but not automatically expired
- **GitHub API error handling** - Basic error handling only, no retry logic
- **Rate limit handling** - No detection or handling of GitHub rate limit responses
- **Pagination** - Assumes user has ≤100 repos (GitHub API default)
- **Concurrent request handling** - No locking for cache updates (race conditions possible)
- **Cache invalidation** - No webhook-based cache invalidation
- **Profile avatar caching** - Avatar URLs are stored but not cached locally
- **Repository README content** - Only metadata is cached, not README files
- **Open issues count in cache** - Single repo detail fetches open_issues_count from API, not cached

These are documented in each test file's "NOT COVERED" section.

## Problems Encountered and Resolved

### Problem 1: Cache TTL Calculation

**Issue**: Needed to calculate cache expiration correctly with timezone-aware timestamps.

**Resolution**: Used `datetime.now(timezone.utc)` for all timestamp comparisons. Stored `expires_at` in cache_metadata table as `fetched_at + timedelta(minutes=ttl)`. All comparisons use timezone-aware datetimes.

### Problem 2: Upsert Logic for Repositories

**Issue**: Needed to upsert repositories without creating duplicates.

**Resolution**: Used PostgreSQL `ON CONFLICT DO UPDATE` with `github_id` as unique constraint. SQLAlchemy's `postgresql.insert()` with `on_conflict_do_update()` handles upserts correctly.

### Problem 3: Cache Metadata vs Data Tables

**Issue**: Needed to decide whether to store cache metadata separately or in data tables.

**Resolution**: Created separate `cache_metadata` table to track TTL information independently. This allows checking cache validity without querying large data tables and supports multiple cache keys.

### Problem 4: Graceful Degradation

**Issue**: Needed to handle GitHub API failures gracefully.

**Resolution**: Implemented fallback to stale cache if GitHub API fails. If cache exists (even if expired), return it instead of error. Only return error if both GitHub API fails AND no cache exists.

### Problem 5: Response Shape Consistency

**Issue**: Needed to ensure all endpoints return consistent response shape.

**Resolution**: Created helper functions `success(data)` and used global exception handler to wrap all responses in envelope format. All endpoints use `response_model=dict` to ensure envelope format.

## API Endpoints Summary

### Public Endpoints

- **GET /api/health** - Health check with database status
- **GET /repos** - List all cached repositories (supports `?refresh=true`)
- **GET /repos/{repo_name}** - Get single repository by name
- **GET /profile** - Get GitHub user profile

### Protected Endpoints

- **POST /cache/refresh** - Manually refresh cache from GitHub API (requires JWT)

All endpoints return data in standard envelope format: `{"data": {}, "error": null}`

## Caching Flow

1. **First Request**: Cache miss → Fetch from GitHub API → Store in Postgres → Return data
2. **Subsequent Requests**: Cache hit (if within TTL) → Return from Postgres (no GitHub API call)
3. **Stale Cache**: Cache expired → Fetch from GitHub API → Update Postgres → Return fresh data
4. **GitHub API Failure**: Return stale cache if available (graceful degradation)

## Cache TTL

- Default: 60 minutes (configurable via `CACHE_TTL_MINUTES` env var)
- Tracks `fetched_at` and `expires_at` in `cache_metadata` table
- Each cache entry has its own expiration timestamp

## Next Steps

Backend API is complete and ready for:
- **Agent 5**: Frontend UI integration (calls these endpoints)
- **Agent 6**: Integration tests (verifies these endpoints work correctly)
