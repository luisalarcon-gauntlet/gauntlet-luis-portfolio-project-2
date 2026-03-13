# Project Brief: Luis Alarcon Personal Portfolio
**Version:** 1.0 | **Program:** Gauntlet AI

---

## Overview

This project is a personal portfolio website for Luis Alarcon, a full-stack and AI engineer in the Gauntlet AI program in Austin, TX. The site automatically fetches all public GitHub repositories from the `luisalarcon-gauntlet` account via the GitHub API and displays them in a clean, dark-themed grid — no manual updates ever needed. A FastAPI backend proxies and caches GitHub API responses in Postgres to stay within the 60 req/hour unauthenticated rate limit. The result is a living resume that hiring partners can visit at any time and immediately see Luis's most recent work, tech stack, and contact information.

---

## Goals

- Automatically pull and display all public repos from `github.com/luisalarcon-gauntlet` without manual intervention
- Cache GitHub API responses in Postgres to avoid hitting the 60 req/hour unauthenticated rate limit
- Present projects sorted by most recently updated, with pinned repos surfaced first
- Deliver a fast, SEO-friendly, mobile-responsive site with a dark theme that reflects Luis's personal brand
- Keep the system simple enough that deployment is a single `docker-compose up` with zero ongoing maintenance

---

## Users

**Hiring Partners and Recruiters**
- Receive Luis's portfolio link and spend a short amount of time on the page
- Need to immediately see what Luis has built and what technologies he uses
- Need visible links to GitHub, LinkedIn, and a downloadable resume
- Do not log in, do not submit forms — purely read-only consumers of the site

---

## Scope

The following is explicitly in scope for v1:

- **Hero Section:** Name, title (Full-Stack & AI Engineer), one-line bio, GitHub link, LinkedIn link
- **Projects Grid:** All public repos fetched from the GitHub API, each card showing repo name, description, primary language, topic tags, star count, last updated date, and a link to the repo; sorted by most recently updated with pinned repos first
- **About Section:** Short paragraph about Luis covering the Gauntlet AI program, background, and Austin TX location; link to resume download
- **Contact Section:** Email link plus GitHub and LinkedIn social links; no contact form
- **GitHub API Integration:** Backend fetches repos for `luisalarcon-gauntlet` and stores responses in Postgres as a cache layer
- **Caching Layer:** FastAPI reads from Postgres cache and only calls GitHub API when cache is stale, preventing rate limit exhaustion
- **Fully Dockerized Monorepo:** Frontend, backend, and database all run via `docker-compose up`
- **Responsive Dark Theme:** Works on mobile and desktop; dark color scheme throughout

---

## Out of Scope

The following is explicitly deferred from v1:

- Authentication or any admin panel for managing content
- Blog or writing section
- Analytics (page views, visitor tracking, etc.)
- Custom domain setup or DNS configuration
- Complex error states or fallback UI beyond the happy path
- Pinned repo detection via GitHub GraphQL API (v1 uses REST only; pinned ordering handled via heuristic if not available)
- Contact form with email delivery

---

## Constraints

- **GitHub API rate limit:** Unauthenticated requests are capped at 60/hour for the GitHub REST API — all API calls must be served from the Postgres cache; the backend only hits GitHub when the cached data is older than a defined TTL (e.g., 1 hour)
- **Fixed GitHub username:** The integration is hardcoded to `luisalarcon-gauntlet`; no dynamic user input
- **Happy path only:** No complex error handling, retry logic, or degraded-state UI in this version
- **No authentication:** JWT is in the default stack but is explicitly not needed here — there is no login, no protected routes, and no admin functionality; JWT is omitted entirely
- **Simplicity over polish:** Functional and clean; no over-engineered component systems or unnecessary dependencies

---

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Next.js 14 + React (App Router, TypeScript) | SEO-friendly; deployable to Vercel or Docker |
| Backend | FastAPI (Python) | Proxies GitHub API, manages cache reads/writes |
| Database | Postgres | Stores cached GitHub API responses with timestamps |
| Infrastructure | Docker + docker-compose | Monorepo; single `docker-compose up` starts all three services |
| Auth | **None** | Explicitly omitted — no login or protected routes in this project |

**Deviation from defaults:** JWT authentication is removed entirely. The PDF explicitly excludes authentication from v1, and there are no protected routes or user sessions of any kind.

---

## Key Decisions

**1. FastAPI as a caching proxy, not just a pass-through**
The GitHub unauthenticated API allows only 60 requests/hour. Calling the API directly from the Next.js frontend on every page load would exhaust this limit almost immediately. The FastAPI backend sits between the frontend and GitHub, writes responses to Postgres with a timestamp, and serves cached data for all subsequent requests until the TTL expires. This is the central architectural constraint driving the backend's existence.

**2. Postgres for cache storage instead of Redis**
Redis would be a natural fit for a cache, but it adds another service and operational dependency. Since the cache TTL is measured in hours (not milliseconds), Postgres is fully sufficient. A single `github_cache` table with a `fetched_at` timestamp keeps the stack minimal and the infrastructure to exactly three containers.

**3. No authentication layer**
The default stack includes JWT, but this site is entirely public. Adding JWT would mean building login flows, token refresh, and protected route middleware for zero user-facing benefit. It is omitted entirely to keep the codebase as small as possible.

**4. Next.js App Router with server components for SEO**
Hiring partners may find the portfolio via search engines. Using Next.js App Router with server-side data fetching ensures the projects grid is rendered with real content in the initial HTML, making it fully crawlable without client-side JavaScript.

**5. Pinned repos sorted first via REST API heuristic**
GitHub's pinned repository feature is only available through the GraphQL API. To avoid adding a second API integration in v1, the backend fetches all public repos via REST and uses star count as a proxy sort signal alongside `updated_at` for ordering. Full pinned-repo support via GraphQL is deferred to a future version.

**6. Monorepo with docker-compose for zero-friction deployment**
Frontend, backend, and database live in a single repository. `docker-compose up` brings up all three services with correct networking and environment variables. This eliminates cross-repo dependency management and makes the entire project runnable on any machine with Docker installed.