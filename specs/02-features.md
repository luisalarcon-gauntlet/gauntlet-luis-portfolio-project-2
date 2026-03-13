# Features Spec — Luis Alarcon Personal Portfolio
**Version:** 1.0 | **Program:** Gauntlet AI | **Stack:** Next.js + FastAPI + Postgres + Docker

---

## Feature 1: Hero Section

**Description:**
The landing section of the portfolio. Displays Luis's name, professional title, a one-line bio, and direct links to his GitHub and LinkedIn profiles. This is the first thing a hiring partner sees — it must be clean, minimal, and immediately communicate who Luis is.

**Happy Path:**
1. User opens the portfolio URL in a browser.
2. The page loads and the Hero Section is visible above the fold without scrolling.
3. User sees the name "Luis Alarcon" rendered prominently.
4. User sees the title "Full-Stack & AI Engineer" directly below the name.
5. User sees a one-line bio describing Luis (Gauntlet AI program, Austin TX).
6. User sees two icon/text links: one for GitHub (`github.com/luisalarcon-gauntlet`) and one for LinkedIn.
7. User clicks the GitHub link and is taken to Luis's GitHub profile in a new tab.
8. User clicks the LinkedIn link and is taken to Luis's LinkedIn profile in a new tab.

**Acceptance Criteria:**
- [ ] Name "Luis Alarcon" is visible on page load without scrolling on a 1280px desktop viewport.
- [ ] Title displayed is exactly "Full-Stack & AI Engineer".
- [ ] One-line bio is present and references the Gauntlet AI program and Austin, TX.
- [ ] GitHub link href points to `https://github.com/luisalarcon-gauntlet` and opens in a new tab.
- [ ] LinkedIn link is present and opens in a new tab.
- [ ] Hero Section is fully responsive — all elements visible and readable on a 375px mobile viewport.
- [ ] Dark theme is applied — background is dark, text is light-colored.
- [ ] Hero Section renders with no JavaScript errors in the browser console.

**Deferred:**
- Animated entrance effects or typewriter text.
- Profile photo or avatar.
- Resume download link in the Hero (covered in About Section).
- Custom tagline CMS or editable content.

---

## Feature 2: GitHub Repositories Fetch & Cache (Backend)

**Description:**
A FastAPI backend service that fetches all public repositories from the GitHub API for the username `luisalarcon-gauntlet`, caches the response in Postgres to avoid hitting the 60 req/hour unauthenticated rate limit, and exposes a single JSON endpoint that the frontend consumes. Cache is refreshed on a time-based interval. This is the core data layer for the Projects Grid.

**Happy Path:**
1. Frontend makes a GET request to `/api/repos` on the FastAPI backend.
2. Backend checks the Postgres cache for a stored response.
3. If the cache is empty or expired, backend makes a single request to `https://api.github.com/users/luisalarcon-gauntlet/repos?per_page=100` and to `https://api.github.com/users/luisalarcon-gauntlet` for pinned/starred data.
4. Backend stores the raw response in Postgres with a timestamp.
5. Backend processes the response: extracts `name`, `description`, `language`, `topics`, `stargazers_count`, `updated_at`, and `html_url` for each repo.
6. Backend returns a JSON array of processed repo objects to the frontend.
7. On a subsequent request within the cache TTL, backend reads directly from Postgres and returns the cached data without calling GitHub API.

**Acceptance Criteria:**
- [ ] `GET /api/repos` returns HTTP 200 with a JSON array.
- [ ] Each repo object in the response contains: `name`, `description`, `language`, `topics`, `stargazers_count`, `updated_at`, `html_url`.
- [ ] A Postgres table named `github_cache` exists with columns: `id`, `data` (JSONB), `cached_at` (TIMESTAMP).
- [ ] If a valid cache entry exists (within TTL), the GitHub API is NOT called — verified by checking `cached_at` timestamp remains unchanged on repeated requests.
- [ ] Cache TTL is set to 60 minutes (configurable via environment variable `CACHE_TTL_MINUTES`).
- [ ] If cache is stale, a fresh GitHub API call is made and `cached_at` is updated.
- [ ] The endpoint returns repos for username `luisalarcon-gauntlet` only (hardcoded in config).
- [ ] Backend runs in Docker and is reachable from the Next.js container at `http://backend:8000`.
- [ ] `/api/repos` responds in under 500ms when serving from cache.

**Deferred:**
- GitHub OAuth token for higher rate limits.
- Webhook-based cache invalidation on GitHub push events.
- Pagination for repos beyond 100.
- Per-repo detailed data fetch (README content, contributors).
- Error response handling when GitHub API is unreachable.

---

## Feature 3: Projects Grid

**Description:**
The main content section of the portfolio. Fetches repo data from the FastAPI backend and renders all public repositories as cards in a responsive grid. Pinned repos appear first; all others are sorted by most recently updated. Each card gives a hiring partner enough context to understand the project at a glance.

**Happy Path:**
1. User scrolls to or arrives at the Projects section of the page.
2. Frontend sends a GET request to the FastAPI `/api/repos` endpoint (via Next.js server-side fetch or client fetch).
3. A loading state is shown while data is being fetched.
4. Repos are received as a JSON array.
5. Repos are sorted: pinned repos first, then remaining repos ordered by `updated_at` descending.
6. Each repo is rendered as a card in a responsive grid layout.
7. Each card displays:
   - Repository name (styled as a heading)
   - Description text (or a blank/placeholder if null)
   - Primary language badge (e.g., "Python", "TypeScript")
   - Topic tags as small pill badges
   - Star count with a star icon
   - Last updated date (human-readable, e.g., "Updated 3 days ago")
   - A "View on GitHub" link that opens the repo in a new tab
8. User clicks "View on GitHub" and is taken to the correct repo URL on GitHub.

**Acceptance Criteria:**
- [ ] Projects section renders all public repos returned by `/api/repos`.
- [ ] Repos are sorted by `updated_at` descending (most recently updated first).
- [ ] A loading indicator is visible while the fetch is in progress.
- [ ] Each card displays: name, description, language, topics, star count, last updated date, and GitHub link.
- [ ] "View on GitHub" link opens `html_url` in a new tab.
- [ ] If `description` is null, the card renders without breaking layout.
- [ ] If `topics` is an empty array, no tag badges are shown (no broken UI).
- [ ] Grid is responsive: 3 columns on desktop (≥1024px), 2 columns on tablet (≥768px), 1 column on mobile (≤767px).
- [ ] Dark theme applied to all cards — consistent with overall site theme.
- [ ] Language badge displays the correct primary language from the API response.
- [ ] Last updated date is human-readable (relative format preferred, e.g., "3 days ago").
- [ ] Section renders with no JavaScript errors in the browser console.

**Deferred:**
- Filtering or searching repos by language or tag.
- Pinned repos detection via GitHub GraphQL API (v1 treats all repos equally sorted by date; pinned ordering deferred unless trivially available in REST response).
- Pagination or "load more" functionality.
- Repo preview images or Open Graph images.
- Fork/watch counts.
- Animated card hover effects beyond basic CSS.

---

## Feature 4: About Section

**Description:**
A static section providing a short paragraph about Luis — his background in full-stack and AI engineering, his participation in the Gauntlet AI program, and his location in Austin, TX. Includes a link to download his resume. This gives hiring partners the human context behind the projects.

**Happy Path:**
1. User scrolls down past the Projects Grid.
2. User sees the "About" section with a heading.
3. User reads a short paragraph about Luis: Gauntlet AI program, full-stack and AI engineering background, based in Austin TX.
4. User sees a "Download Resume" link or button.
5. User clicks "Download Resume" and the resume file (PDF) begins downloading or opens in a new tab.

**Acceptance Criteria:**
- [ ] About section is visible on the page below the Projects Grid.
- [ ] Section contains a heading labeled "About" or "About Me".
- [ ] Paragraph text references: Gauntlet AI program, full-stack engineering, AI engineering, Austin TX.
- [ ] A "Download Resume" link is present and functional.
- [ ] Resume link points to a publicly accessible PDF file (served as a static asset or external URL).
- [ ] Section is responsive — readable on both 375px mobile and 1280px desktop.
- [ ] Dark theme is consistent with the rest of the page.

**Deferred:**
- CMS-editable bio text.
- Skills list or technology icons.
- Work history timeline.
- Profile photo in this section.

---

## Feature 5: Contact Section

**Description:**
A minimal footer-adjacent section that provides direct ways to reach Luis. Displays an email link and social profile links (GitHub, LinkedIn). No contact form — hiring partners click directly to their preferred channel.

**Happy Path:**
1. User scrolls to the bottom of the page.
2. User sees the Contact section with a heading.
3. User sees Luis's email address as a clickable `mailto:` link.
4. User sees a GitHub icon/link pointing to `github.com/luisalarcon-gauntlet`.
5. User sees a LinkedIn icon/link.
6. User clicks the email link — their default mail client opens a new email addressed to Luis.
7. User clicks the GitHub link — opens Luis's GitHub profile in a new tab.
8. User clicks the LinkedIn link — opens Luis's LinkedIn profile in a new tab.

**Acceptance Criteria:**
- [ ] Contact section is visible at or near the bottom of the page.
- [ ] Section contains a heading labeled "Contact" or "Get in Touch".
- [ ] Email is rendered as a `mailto:` anchor tag and opens the system mail client on click.
- [ ] GitHub link href is `https://github.com/luisalarcon-gauntlet` and opens in a new tab.
- [ ] LinkedIn link is present and opens in a new tab.
- [ ] No contact form exists in v1.
- [ ] Section is responsive on both mobile and desktop viewports.
- [ ] Dark theme is consistent with the rest of the page.

**Deferred:**
- Contact form with backend email sending.
- Copy-to-clipboard for email address.
- Twitter/X or other social links.
- reCAPTCHA or spam protection.

---

## Feature 6: Dockerized Monorepo & Infrastructure

**Description:**
The entire application — Next.js frontend, FastAPI backend, and Postgres database — runs as a single monorepo with Docker and docker-compose. A single `docker-compose up` command starts all services. This ensures consistent local development and a deployable artifact with no manual environment setup.

**Happy Path:**
1. Developer clones the repository.
2. Developer creates a `.env` file with required environment variables (`GITHUB_USERNAME`, `CACHE_TTL_MINUTES`, `DATABASE_URL`).
3. Developer runs `docker-compose up --build`.
4. Docker builds the `frontend` container (Next.js on port 3000).
5. Docker builds the `backend` container (FastAPI on port 8000).
6. Docker starts the `db` container (Postgres on port 5432).
7. Backend waits for Postgres to be healthy before starting (healthcheck dependency).
8. Backend runs database migrations to create the `github_cache` table.
9. Developer opens `http://localhost:3000` and sees the full portfolio page with live data.
10. Developer hits `http://localhost:8000/api/repos` and receives a JSON response.

**Acceptance Criteria:**
- [ ] Repository contains a `docker-compose.yml` at the root defining three services: `frontend`, `backend`, `db`.
- [ ] `docker-compose up --build` starts all three services with no manual steps.
- [ ] Frontend is accessible at `http://localhost:3000`.
- [ ] Backend is accessible at `http://localhost:8000`.
- [ ] Backend `/api/repos` returns valid JSON after containers start.
- [ ] Postgres `github_cache` table is created automatically on first backend startup (via migration or init script).
- [ ] Frontend container can reach backend container by service name (`http://backend:8000`).
- [ ] Backend container can reach Postgres container by service name (`db`).
- [ ] `docker-compose down` stops all services cleanly.
- [ ] All secrets and config are passed via environment variables — no hardcoded credentials in code.
- [ ] A `README.md` documents the single `docker-compose up --build` command to run the project.

**Deferred:**
- Production Docker build optimizations (multi-stage builds).
- CI/CD pipeline configuration.
- Vercel deployment configuration.
- Health check endpoints on the backend (`/health`).
- Docker volume persistence configuration beyond Postgres data.

---

## Priority Build Order

Agents build features in the following sequence. Each feature must be verified with `docker-compose up` before proceeding to the next.

| Priority | Feature | Reason |
|----------|---------|--------|
| 1 | **Feature 6 — Dockerized Monorepo & Infrastructure** | Foundation. All other features depend on containers being wired up. Postgres, FastAPI skeleton, and Next.js skeleton must exist before any feature code is written. |
| 2 | **Feature 2 — GitHub Repositories Fetch & Cache (Backend)** | Core data pipeline. The Projects Grid cannot function without this. Build the FastAPI endpoint, Postgres cache table, and GitHub API integration first. Verify `/api/repos` returns valid JSON. |
| 3 | **Feature 3 — Projects Grid** | Highest-value visible feature for hiring partners. Once the backend is live, connect the frontend and render repo cards. This is the primary reason the site exists. |
| 4 | **Feature 1 — Hero Section** | First impression for every visitor. Static content — fast to build. Unblocked once the Next.js container is running. |
| 5 | **Feature 4 — About Section** | Static content. Adds human context. Build after Hero so page structure is established. |
| 6 | **Feature 5 — Contact Section** | Static content. Simplest feature. Build last to complete the page top-to-bottom. |