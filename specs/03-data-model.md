# Data Model Spec — Luis Alarcon Personal Portfolio

## Overview

The database serves a single purpose: cache GitHub API responses to avoid the 60 req/hour unauthenticated rate limit. No user auth, no admin, no blog. Two tables are sufficient.

---

## Tables

### 1. `repositories`

Caches public repo data fetched from the GitHub API for `luisalarcon-gauntlet`.

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | UUID | NOT NULL | Primary key |
| `github_id` | INTEGER | NOT NULL | GitHub's own numeric repo ID (unique) |
| `name` | VARCHAR(255) | NOT NULL | Repository name (e.g. `my-project`) |
| `full_name` | VARCHAR(255) | NOT NULL | Full repo path (e.g. `luisalarcon-gauntlet/my-project`) |
| `description` | TEXT | NULL | Repo description from GitHub |
| `html_url` | TEXT | NOT NULL | Link to the GitHub repo page |
| `homepage` | TEXT | NULL | Optional live demo URL if set in GitHub |
| `primary_language` | VARCHAR(100) | NULL | Primary language reported by GitHub |
| `topics` | TEXT[] | NOT NULL | Array of topic/tag strings from GitHub |
| `stargazers_count` | INTEGER | NOT NULL | Star count |
| `forks_count` | INTEGER | NOT NULL | Fork count |
| `is_fork` | BOOLEAN | NOT NULL | Whether this repo is a fork |
| `is_pinned` | BOOLEAN | NOT NULL | Whether this repo is in the pinned list (see `pinned_repositories` join) |
| `github_pushed_at` | TIMESTAMPTZ | NULL | Last push timestamp from GitHub (`pushed_at`) |
| `github_updated_at` | TIMESTAMPTZ | NOT NULL | Last updated timestamp from GitHub (`updated_at`) |
| `created_at` | TIMESTAMPTZ | NOT NULL | Row creation timestamp (managed by DB) |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Row last updated timestamp (managed by DB) |

**Constraints:**
- `UNIQUE (github_id)`
- `UNIQUE (full_name)`

---

### 2. `cache_metadata`

Tracks when the GitHub API was last successfully fetched so the backend knows whether the cache is stale.

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | UUID | NOT NULL | Primary key |
| `cache_key` | VARCHAR(255) | NOT NULL | Identifier for what was cached (e.g. `github_repos`, `github_pinned`) |
| `fetched_at` | TIMESTAMPTZ | NOT NULL | When the GitHub API was last successfully called |
| `expires_at` | TIMESTAMPTZ | NOT NULL | When this cache entry should be considered stale |
| `http_status` | INTEGER | NOT NULL | HTTP status code of the last GitHub API response |
| `record_count` | INTEGER | NOT NULL | Number of repo records stored in that fetch |
| `created_at` | TIMESTAMPTZ | NOT NULL | Row creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Row last updated timestamp |

**Constraints:**
- `UNIQUE (cache_key)`

---

## Relationships

This schema is intentionally flat. There are no foreign keys between these two tables — they serve independent purposes.

| Relationship | Type | Description |
|---|---|---|
| `repositories` ↔ `cache_metadata` | None (logical only) | `cache_metadata` tracks fetch state; `repositories` holds the fetched data. No FK needed. |

---

## Indexes

```sql
-- Fast lookup by GitHub's own ID during upsert
CREATE UNIQUE INDEX idx_repositories_github_id ON repositories(github_id);

-- Sort order for the projects grid: pinned first, then by last pushed
CREATE INDEX idx_repositories_sort ON repositories(is_pinned DESC, github_pushed_at DESC);

-- Cache key lookup on every request
CREATE UNIQUE INDEX idx_cache_metadata_cache_key ON cache_metadata(cache_key);
```

---

## ASCII Entity Relationship Diagram

```
┌──────────────────────────────────────────────┐
│                 repositories                 │
├──────────────────────────────────────────────┤
│ id                UUID        PK             │
│ github_id         INTEGER     UNIQUE         │
│ name              VARCHAR(255)               │
│ full_name         VARCHAR(255) UNIQUE        │
│ description       TEXT                       │
│ html_url          TEXT                       │
│ homepage          TEXT                       │
│ primary_language  VARCHAR(100)               │
│ topics            TEXT[]                     │
│ stargazers_count  INTEGER                    │
│ forks_count       INTEGER                    │
│ is_fork           BOOLEAN                    │
│ is_pinned         BOOLEAN                    │
│ github_pushed_at  TIMESTAMPTZ                │
│ github_updated_at TIMESTAMPTZ                │
│ created_at        TIMESTAMPTZ                │
│ updated_at        TIMESTAMPTZ                │
└──────────────────────────────────────────────┘

         (no foreign key — logically related)

┌──────────────────────────────────────────────┐
│               cache_metadata                 │
├──────────────────────────────────────────────┤
│ id            UUID        PK                 │
│ cache_key     VARCHAR(255) UNIQUE            │
│ fetched_at    TIMESTAMPTZ                    │
│ expires_at    TIMESTAMPTZ                    │
│ http_status   INTEGER                        │
│ record_count  INTEGER                        │
│ created_at    TIMESTAMPTZ                    │
│ updated_at    TIMESTAMPTZ                    │
└──────────────────────────────────────────────┘
```

---

## Migration Order

No circular dependencies. Run in this order:

| Step | Migration File | Reason |
|---|---|---|
| 1 | `001_create_repositories.sql` | No dependencies — standalone table |
| 2 | `002_create_cache_metadata.sql` | No dependencies — standalone table |
| 3 | `003_create_indexes.sql` | Indexes depend on both tables existing |

---

## Seed Data Description

Minimal seed data for happy path testing in local Docker environment. The goal is to verify the frontend renders correctly without making live GitHub API calls during development.

### `cache_metadata` seed (1 row)

Insert one row with `cache_key = 'github_repos'` where `fetched_at` is set to `NOW()` and `expires_at` is set to `NOW() + interval '1 hour'`. Set `http_status = 200` and `record_count = 3` to match the seeded repos below.

### `repositories` seed (3 rows)

Insert three realistic fake repos that mimic what the GitHub API returns for `luisalarcon-gauntlet`:

| Field | Repo 1 | Repo 2 | Repo 3 |
|---|---|---|---|
| `github_id` | `100000001` | `100000002` | `100000003` |
| `name` | `ai-chat-app` | `portfolio-site` | `fastapi-starter` |
| `full_name` | `luisalarcon-gauntlet/ai-chat-app` | `luisalarcon-gauntlet/portfolio-site` | `luisalarcon-gauntlet/fastapi-starter` |
| `description` | `LLM-powered chat app with RAG` | `Personal portfolio — this site` | `FastAPI boilerplate with Docker` |
| `primary_language` | `Python` | `TypeScript` | `Python` |
| `topics` | `{ai, langchain, fastapi}` | `{nextjs, react, typescript}` | `{fastapi, docker, postgres}` |
| `stargazers_count` | `12` | `5` | `8` |
| `is_fork` | `false` | `false` | `false` |
| `is_pinned` | `true` | `true` | `false` |
| `github_pushed_at` | `NOW() - interval '2 days'` | `NOW() - interval '5 days'` | `NOW() - interval '10 days'` |

This seed data exercises:
- The pinned-first sort order (`is_pinned DESC`)
- The date sort within non-pinned repos (`github_pushed_at DESC`)
- Topic tag rendering (array of strings)
- The cache staleness check in the backend on startup