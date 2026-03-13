# UI Flows Spec — Luis Alarcon Personal Portfolio

---

## Page 1: Portfolio Home

**Route:** `/` (app/page.tsx)
**Auth Required:** No
**Purpose:** Single-page portfolio that showcases Luis's hero info, all public GitHub repos, an about section, and contact links — all fetched live from the backend.

---

### User Flow

1. User lands on `/` via a shared link from a hiring partner or recruiter.
2. Browser requests the page; Next.js renders the shell immediately (dark theme, nav visible).
3. `HeroSection` renders statically — no API call needed (content is hardcoded bio/links).
4. `ProjectsGrid` mounts and fires `GET /api/repos` to the FastAPI backend.
5. While the request is in flight, `ProjectsGrid` shows `LoadingSkeleton` cards (3–6 placeholder cards).
6. Backend responds with the cached or freshly fetched GitHub repo list.
7. Repos are rendered as `ProjectCard` components — pinned repos first, then sorted by `updated_at` descending.
8. User scrolls down past projects to `AboutSection` (static content).
9. User scrolls to `ContactSection` (static content with email + social links).
10. User clicks a `ProjectCard` → browser opens the GitHub repo URL in a new tab.
11. User clicks GitHub or LinkedIn link in `HeroSection` or `ContactSection` → opens in new tab.
12. User clicks "Download Resume" in `AboutSection` → triggers file download or opens PDF in new tab.

---

### Components on This Page

| Component | Description |
|---|---|
| `NavBar` | Fixed top bar with Luis's name on the left and anchor links (Projects, About, Contact) on the right. Smooth-scrolls to sections on click. |
| `HeroSection` | Full-viewport-height section with name, title ("Full-Stack & AI Engineer"), one-line bio, and icon links to GitHub and LinkedIn. Hardcoded content — no API call. |
| `ProjectsGrid` | Fetches repos from `GET /api/repos` on mount. Renders a responsive CSS grid of `ProjectCard` components. Owns loading and error states. |
| `LoadingSkeleton` | Pulse-animated placeholder card shown while `GET /api/repos` is in flight. Renders 6 instances inside `ProjectsGrid`. |
| `ProjectCard` | Displays a single repo: name (as a link), description, primary language badge, topic tags, star count, and last updated date. Entire card is clickable — opens repo URL in new tab. |
| `LanguageBadge` | Small colored pill showing the primary programming language. Color mapped from a static language→color lookup table. |
| `TopicTag` | Small outlined pill for each GitHub topic tag on the repo. Renders up to 4 tags, truncates the rest silently. |
| `AboutSection` | Static section with a short paragraph about Luis (Gauntlet AI, Austin TX, background). Contains a "Download Resume" button/link. |
| `ContactSection` | Static section with mailto link, GitHub link, and LinkedIn link displayed as icon+text rows. Footer text with copyright. |
| `ErrorMessage` | Simple dark-themed inline message shown inside `ProjectsGrid` if the API call fails. Displays one sentence and a "Try again" button that retries the fetch. |

---

### API Calls Made

| Trigger | Endpoint | Method | Notes |
|---|---|---|---|
| `ProjectsGrid` mounts | `GET /api/repos` | GET | Fetches all public repos for `luisalarcon-gauntlet`. Returns cached data if available. No query params required. |

---

### On Success Behavior

- `LoadingSkeleton` cards are replaced with real `ProjectCard` components.
- Pinned repos (flagged by backend) render first in the grid.
- Remaining repos render sorted by `updated_at` descending.
- Page is fully interactive — all links and cards are clickable.

---

### On Error Behavior

- `ProjectsGrid` replaces skeleton cards with `ErrorMessage` component.
- Message text: *"Could not load projects. Please try again."*
- "Try again" button re-fires `GET /api/repos`.
- All other sections (`HeroSection`, `AboutSection`, `ContactSection`) remain fully visible and unaffected.

---

## Navigation Structure

```
/  (app/page.tsx)
│
├── #hero          ← HeroSection (anchor)
├── #projects      ← ProjectsGrid (anchor)
├── #about         ← AboutSection (anchor)
└── #contact       ← ContactSection (anchor)
```

All navigation is single-page anchor-based. There are no child routes in v1. The NavBar links use `href="#section-id"` with smooth scroll behavior set globally in CSS.

```
app/
├── layout.tsx          ← Root layout (dark theme, font, metadata)
├── page.tsx            ← Single route — renders all sections in order
└── globals.css         ← Dark theme CSS variables, scroll behavior
```

---

## Shared Components List

| Component | Location | Used By |
|---|---|---|
| `NavBar` | `components/NavBar.tsx` | `app/layout.tsx` |
| `HeroSection` | `components/HeroSection.tsx` | `app/page.tsx` |
| `ProjectsGrid` | `components/ProjectsGrid.tsx` | `app/page.tsx` |
| `LoadingSkeleton` | `components/LoadingSkeleton.tsx` | `ProjectsGrid` |
| `ProjectCard` | `components/ProjectCard.tsx` | `ProjectsGrid` |
| `LanguageBadge` | `components/LanguageBadge.tsx` | `ProjectCard` |
| `TopicTag` | `components/TopicTag.tsx` | `ProjectCard` |
| `AboutSection` | `components/AboutSection.tsx` | `app/page.tsx` |
| `ContactSection` | `components/ContactSection.tsx` | `app/page.tsx` |
| `ErrorMessage` | `components/ErrorMessage.tsx` | `ProjectsGrid` |

---

## Notes on Data Flow

- `ProjectsGrid` uses a `useEffect` + `useState` pattern (no external data-fetching library) to call `GET /api/repos` via the native `fetch` API.
- The FastAPI backend proxies the GitHub API and caches results in Postgres to stay within the 60 req/hour unauthenticated rate limit.
- No auth headers, tokens, or cookies are required on the frontend — all requests to `/api/repos` are unauthenticated public calls to the Next.js-proxied FastAPI service.
- The Next.js API base URL is configured via `NEXT_PUBLIC_API_URL` environment variable set in `docker-compose.yml`.