# agent.md — luis-portfolio-project

> **Every Cursor coding agent MUST read this file completely before writing a single line of code.**
> This file is the law. When in doubt, re-read this file.

---

## 0. Project Identity

**Project:** `{{PROJECT_NAME}}` (pipeline substitution: `luis-portfolio-project`)
**Description:** Personal portfolio website for Luis Alarcon — a full-stack & AI engineer in the Gauntlet AI program (Austin, TX). The site auto-fetches all public GitHub repos from `luisalarcon-gauntlet`, displays them in a clean dark-themed grid, and serves as a living resume for hiring partners. No auth, no blog, no admin panel — v1 only.

---

## 1. Read These Spec Files First — In This Order

Before touching any code, read every file in this sequence. Do not skip. Do not reorder.

1. `docs/project-brief.md` — Full product brief, goals, user, features, constraints
2. `docs/technical-requirements.md` — Stack decisions, API contracts, caching strategy, data models
3. `docs/features/hero-section.md` — Hero layout, copy, links spec
4. `docs/features/projects-grid.md` — GitHub API fetch logic, card fields, sort/pin rules
5. `docs/features/about-section.md` — About copy, resume download link
6. `docs/features/contact-section.md` — Email + social links spec
7. `docs/api/github-proxy.md` — FastAPI endpoint specs, caching TTL, Postgres schema
8. `docs/infrastructure/docker-compose.md` — Service topology, ports, env vars, health checks

If any of these files do not exist yet, **stop and create them** from the project brief content before proceeding. Never infer architecture from memory — derive it from the specs.

---

## 2. Read All Cursor Rules

After reading the spec files, read every file inside `.cursor/rules/` before writing any code.

```
.cursor/rules/
├── code-style.md
├── testing.md
├── docker.md
├── api-conventions.md
├── frontend-conventions.md
└── git.md
```

If a `.cursor/rules/` file conflicts with this `agent.md`, **this file wins.**
If a rule is ambiguous, default to: **simplicity over cleverness.**

---

## 3. Read Previous Agents' PR Descriptions

Before starting any feature or task:

1. Open the repository's pull request history.
2. Read **every merged PR description** from oldest to newest.
3. Note what was built, what decisions were made, what was explicitly deferred.
4. **Do not re-implement what is already merged.**
5. **Do not re-open decisions that were explicitly closed in a prior PR.**

If you are the first agent (no prior PRs), note that in your own PR description under `## Prior Work`.

---

## 4. The Stack — No Exceptions

This is the stack. Do not introduce anything outside this list without an explicit instruction in the task spec.

| Layer | Technology |
|---|---|
| Frontend | Next.js 14+ (App Router, TypeScript) |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL 15+ |
| Containerization | Docker + docker-compose (monorepo) |
| Auth | JWT only — **not needed for v1** |
| Styling | Tailwind CSS (dark theme) |
| HTTP Client (FE) | `fetch` (native) — no axios |
| HTTP Client (BE) | `httpx` — no requests |
| ORM | SQLAlchemy (async) + Alembic for migrations |
| Package Manager (FE) | `npm` |
| Package Manager (BE) | `pip` + `requirements.txt` |

**Monorepo structure:**
```
/
├── frontend/          # Next.js app
├── backend/           # FastAPI app
├── docker-compose.yml
├── .env.example
└── agent.md           # this file
```

No microservices. No additional services beyond `frontend`, `backend`, `db`.

---

## 5. AI TDD Cycle — Follow This Strictly

Every feature must be built in this exact loop. Do not skip steps. Do not reorder steps.

```
1. READ   → Read the spec for the feature you are about to build
2. TEST   → Write the failing test(s) first — backend unit, integration, or FE component test
3. BUILD  → Write the minimum code to make the tests pass
4. VERIFY → Run the full test suite — all tests must pass
5. DOCKER → Run `docker-compose up --build` — all services must start healthy
6. CHECK  → Manually verify the feature behaves as specified
7. COMMIT → Commit with a descriptive message (see Section 8)
8. REPEAT → Move to the next feature only after all prior steps are green
```

If any step fails, **do not advance.** Return to step 3 and fix. See Section 7 for retry rules.

---

## 6. Project-Specific Implementation Rules

These rules are derived directly from the project brief. They are not suggestions.

### GitHub API + Caching
- The FastAPI backend **must** proxy all GitHub API calls. The frontend never calls GitHub directly.
- GitHub username is hardcoded as `luisalarcon-gauntlet` in backend config (env var: `GITHUB_USERNAME`).
- All GitHub API responses **must be cached in Postgres** with a TTL of **60 minutes** to respect the 60 req/hour unauthenticated rate limit.
- Cache table: `github_cache` with columns `(key TEXT PRIMARY KEY, data JSONB, fetched_at TIMESTAMPTZ)`.
- On cache hit (age < 60 min): return cached data. On cache miss: fetch from GitHub, store, return.
- No GitHub token is required for v1. If a `GITHUB_TOKEN` env var is present, use it. If not, proceed unauthenticated.

### Projects Grid
- Fetch all public repos via `GET https://api.github.com/users/luisalarcon-gauntlet/repos?per_page=100`.
- Sort: pinned repos first, then remaining sorted by `pushed_at` descending.
- Pinned repos: fetch via GitHub GraphQL API or hardcode the pinned list as a fallback env var `PINNED_REPOS` (comma-separated repo names).
- Each card displays: repo name, description, primary language, topic tags, star count, last updated date, link to repo.
- Missing fields (null description, no topics) render as empty — no placeholder text, no error states.

### Frontend
- Dark theme only. Background: `#0a0a0a` or equivalent. No light mode toggle in v1.
- Sections in order: Hero → Projects Grid → About → Contact.
- Single-page layout. No routing needed beyond `/` in v1.
- Mobile-first responsive. Tailwind breakpoints only — no custom media queries.
- No animation libraries. CSS transitions only if needed.

### Backend Endpoints (minimum required)
```
GET  /api/repos          → returns cached repo list
GET  /api/health         → returns {"status": "ok"}
```
No other endpoints are needed for v1.

### Environment Variables
```
# backend/.env
GITHUB_USERNAME=luisalarcon-gauntlet
GITHUB_TOKEN=          # optional
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/portfolio
CACHE_TTL_MINUTES=60

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 7. Docker Is the Source of Truth

**After every feature, run:**
```bash
docker-compose up --build
```

All three services must be healthy:
- `db` — PostgreSQL accepting connections
- `backend` — FastAPI running on port `8000`, `/api/health` returns 200
- `frontend` — Next.js running on port `3000`, page loads without error

**The feature is not done until `docker-compose up --build` passes cleanly.**

Health check requirements in `docker-compose.yml`:
- `db`: `pg_isready`
- `backend`: `curl -f http://localhost:8000/api/health`
- `frontend`: `curl -f http://localhost:3000`

If `docker-compose up --build` fails for any reason, fix it before moving on. See Section 8.

---

## 8. Retry Protocol — Never Move On While Broken

If any of the following fail, you **must retry until fixed.** There is no "note it and move on."

- A test fails → fix the code, re-run all tests
- `docker-compose up --build` fails → fix the Docker/config issue, re-run
- A service fails its health check → fix it, re-run
- A linter or type check fails → fix it, re-run
- The `/api/repos` endpoint returns an error → fix it, re-run
- The frontend shows a blank page or console error → fix it, re-run

**Retry loop:**
```
FAIL → diagnose → fix → re-run → FAIL → diagnose → fix → re-run → ...
```

Continue until green. Do not partially complete a feature. Do not create a PR while anything is broken.

If you are stuck after 3 retry attempts on the same failure:
1. Write a detailed description of the failure and what you tried.
2. Output it as a `DEBUG_NOTE` comment block at the top of the relevant file.
3. Try a fundamentally different approach — not the same fix again.

---

## 9. What to Include in the PR Description

Every PR you open must include all of the following sections. Incomplete PR descriptions will be rejected.

```markdown
## Summary
One paragraph. What feature or task was completed. Reference the spec file.

## Prior Work
List the merged PRs you read before starting, or state "First PR — no prior work."

## What Was Built
Bullet list of every file created or modified, with a one-line description of the change.

## Tests Written
List every test file and what each test covers. State the test command used.

## Test Results
Paste the full test output showing all tests passing.

## Docker Verification
Paste the output of `docker-compose up --build` (last 30 lines or the health check summary).
State explicitly: "All three services (db, backend, frontend) are healthy."

## GitHub API Cache Behavior
(Required for any PR touching the backend or caching layer.)
Describe how the cache was tested — cache hit, cache miss, TTL expiry.

## Known Limitations
List anything that is explicitly out of scope per the brief and was not implemented.
Do NOT list bugs or broken things — those must be fixed before opening the PR.

## How to Test Manually
Step-by-step instructions a human can follow to verify the feature in a browser.
```

---

## 10. What This Agent Must NEVER Do

Read this list before every coding session. These are hard stops.

| ❌ NEVER | Why |
|---|---|
| Mock GitHub API responses in production code | The entire value of the app is real data |
| Skip writing tests before writing code | TDD is not optional |
| Use `pass` or `TODO` comments as placeholders in production code | Either implement it or don't include it |
| Add dependencies not listed in Section 4 without explicit task approval | Over-engineering is a bug |
| Call the GitHub API directly from the frontend | Bypasses the cache, risks rate-limiting |
| Hardcode Luis's personal data (email, LinkedIn URL) in source code | Use env vars or a config file |
| Move on while a test is failing | No exceptions |
| Move on while `docker-compose up --build` is broken | No exceptions |
| Open a PR with a broken build | No exceptions |
| Implement features marked "Out of scope for v1" | Auth, blog, analytics, custom domain |
| Use `any` type in TypeScript | Type everything properly |
| Ignore a failing health check | Fix it |
| Create microservices or separate Docker networks | Monorepo, single network |
| Use `setTimeout` or polling to work around caching | Fix the cache properly |
| Write a test that always passes regardless of behavior | Tests must actually assert |

---

## 11. Acceptance Criteria Checklist

Before opening any PR, verify every item on this list:

- [ ] All spec files listed in Section 1 have been read
- [ ] All `.cursor/rules/` files have been read
- [ ] All prior PR descriptions have been read
- [ ] Tests were written before implementation code
- [ ] All tests pass (`pytest` for backend, `npm test` for frontend)
- [ ] No TypeScript errors (`tsc --noEmit` passes)
- [ ] `docker-compose up --build` completes successfully
- [ ] All three services pass their health checks
- [ ] `GET /api/health` returns `{"status": "ok"}`
- [ ] `GET /api/repos` returns a JSON array of repo objects
- [ ] Frontend loads at `http://localhost:3000` with no console errors
- [ ] Projects grid is visible and populated with real repo data
- [ ] GitHub API responses are being cached in Postgres
- [ ] Cache TTL is respected (second request within 60 min hits cache)
- [ ] Dark theme is applied
- [ ] Layout is responsive (test at 375px and 1280px width)
- [ ] PR description contains all sections from Section 9
- [ ] No items from the "NEVER" list in Section 10 were violated

---

## 12. Quick Reference

```bash
# Start everything
docker-compose up --build

# Backend tests
cd backend && pytest -v

# Frontend type check
cd frontend && npx tsc --noEmit

# Frontend tests
cd frontend && npm test

# Check backend health
curl http://localhost:8000/api/health

# Check repos endpoint
curl http://localhost:8000/api/repos

# View Postgres cache
docker exec -it $(docker-compose ps -q db) psql -U postgres -d portfolio -c "SELECT key, fetched_at FROM github_cache;"

# Reset cache (force re-fetch)
docker exec -it $(docker-compose ps -q db) psql -U postgres -d portfolio -c "DELETE FROM github_cache;"
```

---

*This file is version-controlled. If you find it incomplete or incorrect, fix it in your PR and note the change under a `## agent.md Changes` section in your PR description.*