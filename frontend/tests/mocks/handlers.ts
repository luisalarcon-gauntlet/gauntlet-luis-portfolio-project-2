import { http, HttpResponse } from "msw";
import type { Repository } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Mock repositories data
const mockRepos: Repository[] = [
  {
    id: 123456789,
    name: "test-repo-1",
    full_name: "luisalarcon-gauntlet/test-repo-1",
    description: "Test repository 1 description",
    html_url: "https://github.com/luisalarcon-gauntlet/test-repo-1",
    homepage: null,
    primary_language: "TypeScript",
    topics: ["nextjs", "fastapi", "testing"],
    stargazers_count: 10,
    forks_count: 2,
    is_pinned: false,
    updated_at: "2024-01-15T10:00:00Z",
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 987654321,
    name: "test-repo-2",
    full_name: "luisalarcon-gauntlet/test-repo-2",
    description: null, // Test null description
    html_url: "https://github.com/luisalarcon-gauntlet/test-repo-2",
    homepage: null,
    primary_language: "Python",
    topics: [], // Test empty topics
    stargazers_count: 5,
    forks_count: 1,
    is_pinned: true,
    updated_at: "2024-01-20T15:30:00Z",
    created_at: "2024-01-10T00:00:00Z",
  },
];

export const handlers = [
  // GET /repos
  http.get(`${API_BASE_URL}/repos`, () => {
    return HttpResponse.json({
      data: {
        repos: mockRepos,
        total_count: mockRepos.length,
        cached: true,
        cache_generated_at: new Date().toISOString(),
        cache_expires_at: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
      },
      error: null,
    });
  }),

  // GET /api/health
  http.get(`${API_BASE_URL}/api/health`, () => {
    return HttpResponse.json({
      data: {
        status: "ok",
        database: "connected",
        timestamp: new Date().toISOString(),
      },
      error: null,
    });
  }),
];
