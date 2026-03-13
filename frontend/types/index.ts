/**
 * TypeScript types matching the API contracts from specs/04-api-contracts.md
 */

// API Response Envelope
export interface APIResponse<T> {
  data: T | null;
  error: string | null;
}

// Auth Types
export interface UserRegister {
  email: string;
  password: string;
}

export interface UserPublic {
  id: string;
  email: string;
  created_at: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Repository Types
export interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  homepage: string | null;
  primary_language: string | null;
  topics: string[];
  stargazers_count: number;
  forks_count: number;
  is_pinned: boolean;
  updated_at: string;
  created_at: string;
}

export interface ReposListResponse {
  repos: Repository[];
  total_count: number;
  cached: boolean;
  cache_generated_at: string;
  cache_expires_at: string;
}

export interface RepoDetail {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  homepage: string | null;
  primary_language: string | null;
  topics: string[];
  stargazers_count: number;
  forks_count: number;
  open_issues_count: number;
  is_pinned: boolean;
  updated_at: string;
  created_at: string;
}

export interface RepoDetailResponse {
  repo: RepoDetail;
  cached: boolean;
  cache_generated_at: string;
}

// Profile Types
export interface Profile {
  login: string;
  name: string | null;
  bio: string | null;
  avatar_url: string;
  html_url: string;
  public_repos: number;
  followers: number;
  following: number;
  location: string | null;
}

export interface ProfileResponse {
  profile: Profile;
  cached: boolean;
  cache_generated_at: string;
  cache_expires_at: string;
}

// Health Types
export interface HealthResponse {
  status: string;
  database: string;
  timestamp: string;
}
