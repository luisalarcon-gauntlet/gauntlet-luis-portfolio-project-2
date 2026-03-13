# Authentication Layer (Agent 3)

## Summary

Agent 3 implemented a complete authentication layer for the portfolio backend, including user registration, login, and JWT-based route protection. The implementation follows TDD principles, with all tests written before implementation code. All endpoints return data in the standard envelope format `{"data": {}, "error": null}` as specified in the API contracts. While authentication is not required for v1 (the portfolio is public), it was implemented to provide a foundation for future admin features and to demonstrate the complete auth flow.

## What Was Built

### Core Authentication Components

#### 1. User Model

**File**: `backend/app/models/user.py`

SQLAlchemy model with:
- UUID primary key (`id`)
- Email field (unique, indexed for fast lookups)
- Hashed password field (`hashed_password`)
- Timestamps (`created_at`, `updated_at`)
- Inherits from `Base`, `UUIDMixin`, `TimestampMixin` per project conventions

#### 2. Auth Schemas

**File**: `backend/app/schemas/auth.py`

Pydantic schemas for request/response validation:
- **`UserRegister`**: Registration request with email and password
- **`UserLogin`**: Login request with email and password
- **`TokenResponse`**: Login response with `access_token`, `token_type`, `expires_in`
- **`UserPublic`**: Public user data (explicitly excludes password fields)

#### 3. Auth Service

**File**: `backend/app/services/auth_service.py`

Business logic for authentication:
- **`hash_password()`**: Uses bcrypt via passlib for secure password hashing
- **`verify_password()`**: Verifies plain password against hashed password
- **`create_access_token()`**: Creates JWT with user ID, expiration, and issued-at time
- **`decode_jwt_token()`**: Validates and decodes JWT tokens

#### 4. JWT Dependency

**File**: `backend/app/dependencies.py`

FastAPI dependency for protected routes:
- **`get_current_user()`**: Extracts token from Authorization header using OAuth2PasswordBearer
- Validates token and fetches user from database
- Returns 401 with envelope format if token is missing or invalid
- Used as `Depends(get_current_user)` in protected route decorators

#### 5. Auth Router

**File**: `backend/app/routers/auth.py`

API endpoints:
- **`POST /auth/register`**: Creates new user account, returns user data without password
- **`POST /auth/login`**: Authenticates user, returns JWT access token
- Both endpoints use standard envelope format for responses

#### 6. Database Migration

**File**: `db/migrations/versions/004_create_users_table.py`

Creates `users` table with:
- UUID primary key
- Email (unique, indexed)
- Hashed password
- Timestamps (`created_at`, `updated_at`)

### Configuration Updates

#### Config

**File**: `backend/app/core/config.py`

Added JWT settings:
- `secret_key` (required, from `SECRET_KEY` env var)
- `algorithm` (default: "HS256")
- `access_token_expire_minutes` (default: 30)

#### Dependencies

**File**: `backend/requirements.txt`

Added:
- `python-jose[cryptography]==3.3.0` for JWT encoding/decoding
- `passlib[bcrypt]==1.7.4` for password hashing
- `pytest==8.3.3` and `pytest-asyncio==0.23.7` for testing

#### Environment

**File**: `.env.example`

Added:
- `SECRET_KEY` - JWT signing key
- `ALGORITHM` - JWT algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)

### Error Handling

**File**: `backend/app/main.py`

Added HTTPException handler to wrap all HTTPException responses in envelope format:
```python
{"data": null, "error": "error message"}
```

### Testing

**File**: `backend/tests/test_auth.py`

Comprehensive TDD tests:
- `test_register_endpoint_returns_user_data_without_password()` - Registration test
- `test_login_endpoint_returns_jwt_token()` - Login test
- `test_protected_route_returns_401_without_token()` - JWT protection test

**File**: `backend/tests/conftest.py`

Test database setup and cleanup:
- Database cleanup fixture for test isolation
- Drops and recreates tables before each test

### Protected Route Example

**File**: `backend/app/main.py`

Added `POST /cache/refresh` endpoint as a demonstration of protected route:
- Requires JWT token in Authorization header
- Returns 401 if token is missing or invalid
- Uses `Depends(get_current_user)` dependency

## Key Decisions Made

### 1. JWT Token Storage

**Decision**: Tokens are stored in memory only (React context), never in localStorage or cookies.

**Why**: 
- Per frontend rules: "JWT Stored in Memory Only — Never localStorage or Cookies"
- Security best practice - tokens are lost on page refresh, which is intentional for this project's security posture
- Reduces risk of XSS attacks (tokens not accessible to JavaScript if stored server-side)
- Intentional design choice for this project's security model

### 2. Password Hashing

**Decision**: Used bcrypt via passlib library.

**Why**: 
- Industry standard for password hashing
- Per API design rules: "Use passlib with bcrypt as the hashing scheme. Never use hashlib or MD5/SHA for passwords."
- Bcrypt is computationally expensive, making brute-force attacks impractical
- Salt is automatically handled by bcrypt

### 3. Token Expiration

**Decision**: Set to 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

**Why**:
- Balance between security and usability
- Short enough to limit exposure if token is compromised
- Long enough to avoid frequent re-authentication during normal use
- Per API design rules: default 30 minutes

### 4. Error Response Format

**Decision**: All errors use envelope format `{"data": null, "error": "message"}`.

**Why**:
- Per API design rules: "Every endpoint MUST return a consistent envelope shape. No exceptions."
- Ensures consistent API contract across all endpoints
- Makes error handling predictable for frontend
- Matches success response format

### 5. OAuth2PasswordBearer Configuration

**Decision**: Set `auto_error=False` and handle missing tokens manually to return 401 instead of 403.

**Why**:
- Per API contract spec: "Unauthorized (missing or invalid JWT): 401"
- OAuth2PasswordBearer defaults to 403, but we need 401 for consistency
- Manual handling allows us to return the correct status code and envelope format
- Better aligns with HTTP status code semantics (401 = authentication required)

### 6. User ID in JWT

**Decision**: Store user UUID as string in JWT `sub` claim.

**Why**:
- Per API design rules: "Store only non-sensitive claims in the token payload: sub (user id), exp, iat"
- UUID is non-sensitive and sufficient to identify the user
- Stored as string for JSON compatibility
- Standard JWT claim name (`sub` = subject)

### 7. Database Schema

**Decision**: Users table uses UUID primary key, email is unique and indexed.

**Why**:
- Per database rules: "All tables must use UUID primary keys generated server-side"
- Email uniqueness is required for authentication
- Index on email ensures fast login lookups
- Consistent with other tables in the project

### 8. Test Database Setup

**Decision**: Use conftest.py to drop and recreate tables before each test.

**Why**:
- Ensures test isolation - each test starts with a clean database
- Per TDD rules: "Tests run against the real Postgres container"
- Simple and effective for test reliability
- No test data pollution between tests

### 9. Protected Route Example

**Decision**: Added `POST /cache/refresh` as a protected route example.

**Why**:
- Provides a concrete example of how to protect routes
- Matches the API contract spec which includes this endpoint
- Useful for testing JWT middleware
- Demonstrates real-world use case (admin cache refresh)

### 10. No Password in Responses

**Decision**: Explicitly exclude password and hashed_password from all response schemas.

**Why**:
- Per API design rules: "Never return the hashed_password field in any API response under any circumstances"
- Security best practice - passwords should never leave the server
- `UserPublic` schema explicitly omits password fields
- Prevents accidental password exposure

## What Was Skipped/Deferred

Per the TDD rules and API contract spec, the following are intentionally not implemented in v1:

- **Duplicate email registration handling** - Returns 409, but not tested
- **Invalid email format validation** - Relies on Pydantic EmailStr
- **Password strength requirements** - No minimum length or complexity rules
- **Login with wrong password** - Returns 401, but not tested
- **Login with non-existent email** - Returns 401, but not tested
- **Token expiration handling** - Tokens expire, but refresh flow not implemented
- **Token refresh endpoint** - No refresh token mechanism
- **Password reset flow** - No password reset functionality
- **Email verification** - No email verification required
- **Rate limiting on auth endpoints** - No rate limiting implemented
- **Account lockout after failed attempts** - No lockout mechanism

These are documented in the test file's "NOT COVERED" section.

## Problems Encountered and Resolved

### Problem 1: OAuth2PasswordBearer Status Code

**Issue**: OAuth2PasswordBearer defaults to returning 403 (Forbidden) for missing tokens, but API contract requires 401 (Unauthorized).

**Resolution**: Set `auto_error=False` on OAuth2PasswordBearer and manually check for token presence. If missing, raise HTTPException with status 401 and envelope format. This ensures consistent error responses.

### Problem 2: Password Hashing Library

**Issue**: Needed to choose between `passlib` and `bcrypt` directly.

**Resolution**: Used `passlib[bcrypt]` as it provides a higher-level API and is recommended by FastAPI documentation. It handles salt generation and verification automatically.

### Problem 3: JWT Library Choice

**Issue**: Needed to choose between `python-jose` and `PyJWT`.

**Resolution**: Used `python-jose[cryptography]` as it's recommended by FastAPI documentation and provides good integration with FastAPI's security utilities.

### Problem 4: Token Expiration Format

**Issue**: Needed to determine how to represent token expiration in response.

**Resolution**: Return `expires_in` as integer seconds (e.g., 1800 for 30 minutes) in the login response. This is a standard OAuth2 format and makes it easy for frontend to calculate expiration time.

## API Endpoints

### POST /auth/register

**Request:**
```json
{
  "email": "user@example.com",
  "password": "supersecret123"
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "error": null
}
```

### POST /auth/login

**Request:**
```json
{
  "email": "user@example.com",
  "password": "supersecret123"
}
```

**Response (200):**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "error": null
}
```

### POST /cache/refresh (Protected)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "data": {
    "refreshed": true
  },
  "error": null
}
```

**Response (401 - No Token):**
```json
{
  "data": null,
  "error": "Invalid or missing authorization token."
}
```

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt before storage
2. **JWT Tokens**: Tokens are signed with HS256 algorithm
3. **Token Expiration**: Tokens expire after 30 minutes (configurable)
4. **No Password Exposure**: Passwords and hashed passwords never appear in API responses
5. **Secure Token Claims**: JWT payload contains only user ID, expiration, and issued-at time
6. **In-Memory Token Storage**: Frontend stores tokens in React state only (not localStorage)

## Next Steps

The auth layer is complete and ready for use. To integrate with the frontend:
1. Update frontend to call `/auth/register` and `/auth/login` endpoints
2. Store JWT tokens in React context (in-memory only, per frontend rules)
3. Include `Authorization: Bearer <token>` header in protected API calls
4. Handle 401 responses by redirecting to login

This was implemented by Agent 5 in the frontend UI work.
