/**
 * All backend API calls live here, nowhere else.
 * Per frontend rules: No fetch() calls outside of this file.
 */

import type {
  Repository,
  RepoDetail,
  Profile,
  APIResponse,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Generic API fetch function with envelope handling
 */
async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ error: `API error ${res.status}: ${path}` }));
    throw new Error(errorData.error || `API error ${res.status}: ${path}`);
  }

  return res.json() as Promise<T>;
}

/**
 * API fetch with authentication token
 */
async function apiFetchWithAuth<T>(
  path: string,
  token: string,
  options?: RequestInit
): Promise<T> {
  return apiFetch<T>(path, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...options?.headers,
    },
  });
}

// Auth Endpoints
export async function registerUser(
  email: string,
  password: string
): Promise<APIResponse<{ id: string; email: string; created_at: string }>> {
  return apiFetch<APIResponse<{ id: string; email: string; created_at: string }>>(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }
  );
}

export async function loginUser(
  email: string,
  password: string
): Promise<APIResponse<{ access_token: string; token_type: string; expires_in: number }>> {
  return apiFetch<APIResponse<{ access_token: string; token_type: string; expires_in: number }>>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }
  );
}

// Repository Endpoints
export async function getRepositories(
  refresh?: boolean
): Promise<APIResponse<{
  repos: Repository[];
  total_count: number;
  cached: boolean;
  cache_generated_at: string;
  cache_expires_at: string;
}>> {
  const queryParam = refresh ? "?refresh=true" : "";
  return apiFetch<APIResponse<{
    repos: Repository[];
    total_count: number;
    cached: boolean;
    cache_generated_at: string;
    cache_expires_at: string;
  }>>(`/repos${queryParam}`);
}

export async function getRepository(
  repoName: string
): Promise<APIResponse<{
  repo: RepoDetail;
  cached: boolean;
  cache_generated_at: string;
}>> {
  return apiFetch<APIResponse<{
    repo: RepoDetail;
    cached: boolean;
    cache_generated_at: string;
  }>>(`/repos/${repoName}`);
}

// Profile Endpoint
export async function getProfile(): Promise<APIResponse<{
  profile: Profile;
  cached: boolean;
  cache_generated_at: string;
  cache_expires_at: string;
}>> {
  return apiFetch<APIResponse<{
    profile: Profile;
    cached: boolean;
    cache_generated_at: string;
    cache_expires_at: string;
  }>>("/profile");
}

// Cache Refresh Endpoint (Protected)
export async function refreshCache(
  token: string
): Promise<APIResponse<{
  refreshed: boolean;
  repos_cached: number;
  profile_cached: boolean;
  cache_generated_at: string;
  cache_expires_at: string;
}>> {
  return apiFetchWithAuth<APIResponse<{
    refreshed: boolean;
    repos_cached: number;
    profile_cached: boolean;
    cache_generated_at: string;
    cache_expires_at: string;
  }>>("/cache/refresh", token, {
    method: "POST",
  });
}

// Health Endpoint
export async function getHealth(): Promise<APIResponse<{
  status: string;
  database: string;
  timestamp: string;
}>> {
  return apiFetch<APIResponse<{
    status: string;
    database: string;
    timestamp: string;
  }>>("/api/health");
}
