# YogaFlow API Contract - Batch 0

**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api/v1`
**Status:** ✅ Ready for Frontend Integration

## Overview

This document defines the authentication API contract for YogaFlow MVP. The backend provides JWT-based authentication with the following security features:

- **Password Hashing:** Bcrypt with work factor 12
- **Token Type:** JWT (HS256)
- **Token Expiration:** 24 hours (access), 7 days (refresh with remember_me)
- **Security Headers:** CORS, HTTPS-ready
- **Error Handling:** Centralized with consistent format

## Authentication Endpoints

### 1. Register User

**POST** `/api/v1/auth/register`

Creates a new user account and returns authentication tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "Jane Doe",
  "password": "SecurePass123",
  "experience_level": "beginner"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "name": "Jane Doe",
    "experience_level": "beginner",
    "email_verified": false,
    "created_at": "2025-01-15T10:30:00Z",
    "last_login": "2025-01-15T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": null,
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

**Validation Rules:**
- Email must be unique and valid format
- Password: min 8 chars, must contain uppercase, lowercase, and number
- Experience level: "beginner", "intermediate", or "advanced"

**Error Responses:**
- `400`: Email already registered or weak password
- `422`: Validation error

---

### 2. Login User

**POST** `/api/v1/auth/login`

Authenticates user and returns JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "remember_me": false
}
```

**Response (200 OK):**
```json
{
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "name": "Jane Doe",
    "experience_level": "beginner",
    "email_verified": false,
    "created_at": "2025-01-15T10:30:00Z",
    "last_login": "2025-01-15T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 604800
  }
}
```

**Notes:**
- If `remember_me` is true, refresh_token is included with 7-day expiration
- Access token is always returned with 24-hour expiration

**Error Responses:**
- `401`: Invalid credentials
- `403`: Account inactive
- `422`: Validation error

---

### 3. Logout User

**POST** `/api/v1/auth/logout`

Logs out current user (informational endpoint).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out",
  "detail": "Please discard your access and refresh tokens"
}
```

**Notes:**
- JWT tokens are stateless, so server-side logout is informational
- Client must discard tokens from storage
- Token will remain valid until expiration

**Error Responses:**
- `401`: Invalid or expired token

---

### 4. Get Current User

**GET** `/api/v1/auth/me`

Returns authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "name": "Jane Doe",
  "experience_level": "beginner",
  "email_verified": false,
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401`: Invalid or expired token

---

### 5. Refresh Access Token

**POST** `/api/v1/auth/refresh`

Generates new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Error Responses:**
- `401`: Invalid or expired refresh token

---

## Authentication Flow

### For Frontend Implementation:

1. **Registration:**
   ```
   POST /auth/register → Store tokens → Redirect to dashboard
   ```

2. **Login:**
   ```
   POST /auth/login → Store tokens → Redirect to dashboard
   ```

3. **Authenticated Requests:**
   ```
   Add header: Authorization: Bearer <access_token>
   ```

4. **Token Refresh:**
   ```
   If 401 error + have refresh_token:
     POST /auth/refresh → Update access_token → Retry request
   ```

5. **Logout:**
   ```
   POST /auth/logout → Remove tokens from storage → Redirect to login
   ```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    experience_level VARCHAR(50) DEFAULT 'beginner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
```

---

## Security Features Implemented

✅ **REQ-NF-SEC-001:** HTTPS-ready (TLS 1.3 when deployed)
✅ **REQ-NF-SEC-002:** Bcrypt password hashing (work factor 12)
✅ **REQ-NF-SEC-003:** SQL injection protection (parameterized queries via SQLAlchemy)
✅ **REQ-NF-SEC-004:** XSS protection (input validation, output escaping via Pydantic)
✅ **REQ-NF-SEC-005:** CSRF protection (stateless JWT tokens, SameSite cookies when used)
✅ **REQ-NF-SEC-009:** Secure session management (HTTP-only cookies option, secure flags)

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error type or message",
  "detail": "Detailed error information",
  "status_code": 400
}
```

Validation errors include field-specific details:

```json
{
  "error": "Validation Error",
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "message": "Request validation failed"
}
```

---

## CORS Configuration

**Allowed Origins (Development):**
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

**Allowed Methods:** GET, POST, PUT, DELETE, PATCH
**Credentials:** Supported
**Headers:** All headers allowed

---

## Testing the API

### Using cURL:

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPass123",
    "experience_level": "beginner"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "remember_me": false
  }'
```

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Next Steps for Frontend

1. ✅ **API Contract Available** - This document
2. 🔄 **Integration Points:**
   - Create auth context/provider
   - Implement token storage (localStorage or secure cookies)
   - Add Authorization header interceptor
   - Handle token refresh logic
   - Create login/register forms
   - Add auth guards for protected routes

3. 📋 **Future Endpoints (Batch 1+):**
   - Pose CRUD operations
   - Sequence management
   - Practice session tracking
   - User profile updates
   - Password reset flow

---

## OpenAPI Documentation

Full OpenAPI 3.1 specification available at:
- **JSON:** `/openapi.json`
- **Interactive Docs:** `/docs` (Swagger UI)
- **Alternative Docs:** `/redoc` (ReDoc)

---

## Support & Issues

- **Backend Agent:** @backend-agent
- **Channel:** #parallel-work
- **Errors:** #errors

---

**Document Version:** 1.0
**Last Updated:** 2025-12-05
**Status:** Ready for Integration ✅
