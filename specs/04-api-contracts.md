# API Contracts Spec — Luis Alarcon Personal Portfolio

## Base URL

```
http://localhost:8000
```

All responses follow this envelope:

```json
{ "data": {}, "error": null }
{ "data": null, "error": "message" }
```

---

## Auth Endpoints

### POST /auth/register

**Description:** Register a new user account. Included per stack standard; not exposed in the portfolio UI but available for future admin use.

**Auth required:** No

**Request body:**
```json
{
  "email": "luis@example.com",
  "password": "supersecret123"
}
```

**Response `200`:**
```json
{
  "data": {
    "id": 1,
    "email": "luis@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "error": null
}
```

---

### POST /auth/login

**Description:** Authenticate a user and return a JWT access token.

**Auth required:** No

**Request body:**
```json
{
  "email": "luis@example.com",
  "password": "supersecret123"
}
```

**Response `200`:**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "error": null
}
```

---

## Feature Endpoints

### GET /repos

**Description:** Returns all public repositories for `luisalarcon-gauntlet`. Responses are served from the Postgres cache if the cache is fresh (TTL: 60 minutes) to avoid hitting the GitHub API unauthenticated rate limit of 60 req/hour. If the cache is stale or empty, the backend fetches fresh data from the GitHub API, stores it, and returns it. Repos are sorted by most recently updated; pinned repos appear first.

**Auth required:** No

**Request body:** None

**Query params (optional):**

| Param | Type | Description |
|---|---|---|
| `refresh` | `boolean` | Force a cache bypass and re-fetch from GitHub. Default: `false`. |

**Response `200`:**
```json
{
  "data": {
    "repos": [
      {
        "id": 123456789,
        "name": "ai-code-reviewer",
        "full_name": "luisalarcon-gauntlet/ai-code-reviewer",
        "description": "Automated AI-powered code review tool built with GPT-4 and FastAPI.",
        "html_url": "https://github.com/luisalarcon-gauntlet/ai-code-reviewer",
        "homepage": "https://ai-code-reviewer.vercel.app",
        "primary_language": "Python",
        "topics": ["ai", "fastapi", "openai", "python"],
        "stargazers_count": 14,
        "forks_count": 3,
        "is_pinned": true,
        "updated_at": "2024-01-14T08:22:00Z",
        "created_at": "2023-11-01T12:00:00Z"
      },
      {
        "id": 987654321,
        "name": "nextjs-portfolio",
        "full_name": "luisalarcon-gauntlet/nextjs-portfolio",
        "description": "Personal portfolio website built with Next.js and FastAPI.",
        "html_url": "https://github.com/luisalarcon-gauntlet/nextjs-portfolio",
        "homepage": null,
        "primary_language": "TypeScript",
        "topics": ["nextjs", "react", "portfolio", "typescript"],
        "stargazers_count": 7,
        "forks_count": 1,
        "is_pinned": false,
        "updated_at": "2024-01-10T15:45:00Z",
        "created_at": "2023-12-05T09:30:00Z"
      }
    ],
    "total_count": 2,
    "cached": true,
    "cache_generated_at": "2024-01-15T09:00:00Z",
    "cache_expires_at": "2024-01-15T10:00:00Z"
  },
  "error": null
}
```

---

### GET /repos/{repo_name}

**Description:** Returns details for a single public repository by name. Served from cache if available; otherwise fetches from GitHub API and stores the result.

**Auth required:** No

**Request body:** None

**Path params:**

| Param | Type | Description |
|---|---|---|
| `repo_name` | `string` | The repository name, e.g. `ai-code-reviewer` |

**Response `200`:**
```json
{
  "data": {
    "repo": {
      "id": 123456789,
      "name": "ai-code-reviewer",
      "full_name": "luisalarcon-gauntlet/ai-code-reviewer",
      "description": "Automated AI-powered code review tool built with GPT-4 and FastAPI.",
      "html_url": "https://github.com/luisalarcon-gauntlet/ai-code-reviewer",
      "homepage": "https://ai-code-reviewer.vercel.app",
      "primary_language": "Python",
      "topics": ["ai", "fastapi", "openai", "python"],
      "stargazers_count": 14,
      "forks_count": 3,
      "open_issues_count": 2,
      "is_pinned": true,
      "updated_at": "2024-01-14T08:22:00Z",
      "created_at": "2023-11-01T12:00:00Z"
    },
    "cached": true,
    "cache_generated_at": "2024-01-15T09:00:00Z"
  },
  "error": null
}
```

---

### GET /profile

**Description:** Returns Luis's GitHub profile metadata — display name, bio, avatar URL, follower count, and public repo count. Served from Postgres cache (TTL: 60 minutes). Used to populate the Hero section.

**Auth required:** No

**Request body:** None

**Response `200`:**
```json
{
  "data": {
    "profile": {
      "login": "luisalarcon-gauntlet",
      "name": "Luis Alarcon",
      "bio": "Full-Stack & AI Engineer · Gauntlet AI Program · Austin, TX",
      "avatar_url": "https://avatars.githubusercontent.com/u/000000000?v=4",
      "html_url": "https://github.com/luisalarcon-gauntlet",
      "public_repos": 18,
      "followers": 42,
      "following": 15,
      "location": "Austin, TX"
    },
    "cached": true,
    "cache_generated_at": "2024-01-15T09:00:00Z",
    "cache_expires_at": "2024-01-15T10:00:00Z"
  },
  "error": null
}
```

---

### POST /cache/refresh

**Description:** Manually triggers a full cache refresh — clears existing cached repos and profile from Postgres and re-fetches all data from the GitHub API. Intended for future admin use when immediate updates are needed without waiting for the TTL to expire.

**Auth required:** Yes (JWT Bearer token)

**Request headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request body:** None

**Response `200`:**
```json
{
  "data": {
    "refreshed": true,
    "repos_cached": 18,
    "profile_cached": true,
    "cache_generated_at": "2024-01-15T10:55:00Z",
    "cache_expires_at": "2024-01-15T11:55:00Z"
  },
  "error": null
}
```

---

### GET /health

**Description:** Health check endpoint. Confirms the API is running and the Postgres connection is alive. Used by Docker health checks and any uptime monitoring.

**Auth required:** No

**Request body:** None

**Response `200`:**
```json
{
  "data": {
    "status": "ok",
    "database": "connected",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "error": null
}
```

---

## Error Response Examples

**Repo not found:**
```json
{
  "data": null,
  "error": "Repository 'nonexistent-repo' not found for user luisalarcon-gauntlet."
}
```

**GitHub API unavailable and no cache:**
```json
{
  "data": null,
  "error": "GitHub API request failed and no cached data is available."
}
```

**Unauthorized (missing or invalid JWT):**
```json
{
  "data": null,
  "error": "Invalid or missing authorization token."
}
```

---

## Cache Strategy Summary

| Resource | Postgres Table | TTL | Trigger |
|---|---|---|---|
| All repos list | `cached_repos` | 60 minutes | `GET /repos` on stale cache |
| Single repo | `cached_repos` | 60 minutes | `GET /repos/{repo_name}` on miss |
| GitHub profile | `cached_profile` | 60 minutes | `GET /profile` on stale cache |
| Manual refresh | Both tables | Reset TTL | `POST /cache/refresh` |