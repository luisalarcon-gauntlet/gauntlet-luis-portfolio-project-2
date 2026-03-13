# Auth Layer Implementation Summary

## Overview
This document summarizes the authentication layer implementation for the Luis Alarcon Portfolio project. The implementation follows TDD principles and includes user registration, login, and JWT-based route protection.

## What Was Implemented

### 1. Dependencies Added
- `python-jose[cryptography]==3.3.0` - JWT encoding/decoding
- `passlib[bcrypt]==1.7.4` - Password hashing
- `pytest==8.3.3` - Testing framework
- `pytest-asyncio==0.23.7` - Async test support

### 2. Configuration Updates
- Added JWT settings to `backend/app/core/config.py`:
  - `secret_key` - JWT signing key (from env var `SECRET_KEY`)
  - `algorithm` - JWT algorithm (default: "HS256")
  - `access_token_expire_minutes` - Token expiration (default: 30 minutes)
- Updated `.env.example` with auth configuration

### 3. Database Model
- Created `User` model (`backend/app/models/user.py`):
  - UUID primary key
  - Email (unique, indexed)
  - Hashed password
  - Timestamps (created_at, updated_at)
- Created Alembic migration `004_create_users_table.py`

### 4. Schemas
Created Pydantic schemas in `backend/app/schemas/auth.py`:
- `UserRegister` - Registration request
- `UserLogin` - Login request
- `TokenResponse` - Login response (access_token, token_type, expires_in)
- `UserPublic` - Public user data (no password fields)

### 5. Auth Service
Implemented `backend/app/services/auth_service.py`:
- `hash_password()` - Bcrypt password hashing
- `verify_password()` - Password verification
- `create_access_token()` - JWT token creation
- `decode_jwt_token()` - JWT token validation

### 6. Dependencies
Created `backend/app/dependencies.py`:
- `get_current_user()` - JWT authentication dependency
  - Extracts token from Authorization header
  - Validates token and fetches user from database
  - Returns 401 if token is missing or invalid

### 7. Auth Router
Implemented `backend/app/routers/auth.py`:
- `POST /auth/register` - User registration
  - Validates email uniqueness
  - Hashes password before storage
  - Returns user data (id, email, created_at) without password
- `POST /auth/login` - User authentication
  - Verifies email and password
  - Returns JWT access token with expiration

### 8. Protected Routes
- Added `POST /cache/refresh` endpoint in `main.py` as a test protected route
- Protected using `Depends(get_current_user)`
- Returns 401 if no valid token is provided

### 9. Error Handling
- Added HTTPException handler in `main.py` to return errors in envelope format:
  ```json
  {"data": null, "error": "error message"}
  ```

### 10. Tests
Created comprehensive TDD tests in `backend/tests/test_auth.py`:
- `test_register_endpoint_returns_user_data_without_password()` - Registration test
- `test_login_endpoint_returns_jwt_token()` - Login test
- `test_protected_route_returns_401_without_token()` - JWT protection test

Created `backend/tests/conftest.py` for test database setup and cleanup.

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

## Verification Steps

To verify the implementation works correctly:

1. **Run Database Migration:**
   ```bash
   cd db && alembic upgrade head
   ```

2. **Run Tests:**
   ```bash
   cd backend && pytest tests/test_auth.py -v
   ```

3. **Test Registration:**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "secret123"}'
   ```

4. **Test Login:**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "secret123"}'
   ```

5. **Test Protected Route (without token):**
   ```bash
   curl -X POST http://localhost:8000/cache/refresh
   # Should return 401
   ```

6. **Test Protected Route (with token):**
   ```bash
   TOKEN="<token from login>"
   curl -X POST http://localhost:8000/cache/refresh \
     -H "Authorization: Bearer $TOKEN"
   # Should return 200
   ```

## Files Created/Modified

### Created:
- `backend/app/models/user.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/dependencies.py`
- `backend/app/routers/auth.py`
- `backend/tests/test_auth.py`
- `backend/tests/conftest.py`
- `db/migrations/versions/004_create_users_table.py`

### Modified:
- `backend/requirements.txt`
- `backend/app/core/config.py`
- `backend/app/main.py`
- `backend/app/models/__init__.py`
- `.env.example`

## Design Decisions

1. **JWT Storage**: Tokens are stored in memory only (as per frontend rules), not in localStorage or cookies
2. **Password Hashing**: Used bcrypt via passlib for industry-standard password security
3. **Error Format**: All errors use the standard envelope format `{"data": null, "error": "message"}`
4. **Token Expiration**: Set to 30 minutes as a balance between security and usability
5. **OAuth2PasswordBearer**: Used FastAPI's built-in security for token extraction, with custom error handling to return 401 instead of 403
6. **Database**: Users table uses UUID primary keys and follows the project's naming conventions

## Next Steps

The auth layer is complete and ready for use. To integrate with the frontend:
1. Update frontend to call `/auth/register` and `/auth/login` endpoints
2. Store JWT tokens in React context (in-memory only, per frontend rules)
3. Include `Authorization: Bearer <token>` header in protected API calls
4. Handle 401 responses by redirecting to login
