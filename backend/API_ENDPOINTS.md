# YogaFlow API Endpoints - Quick Reference

**Base URL:** `http://localhost:8000/api/v1`

## Authentication Endpoints

### POST /auth/register
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "email_verified": true,
    "is_active": true,
    "created_at": "2025-12-05T22:00:00Z"
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

### POST /auth/login
Authenticate user and get tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "remember_me": false
}
```

**Response:** `200 OK`
```json
{
  "user": { ... },
  "tokens": { ... }
}
```

### POST /auth/logout
Logout current user (requires authentication).

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out",
  "detail": "Please discard your access and refresh tokens"
}
```

### GET /auth/me
Get current user profile (requires authentication).

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "experience_level": "beginner",
  "email_verified": true,
  "is_active": true,
  "created_at": "2025-12-05T22:00:00Z",
  "updated_at": "2025-12-05T22:00:00Z"
}
```

## Pose Endpoints

### GET /poses
List poses with pagination, search, and filtering.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 20, max: 100): Items per page
- `search` (string, optional): Search by name (English or Sanskrit)
- `category` (enum, optional): Filter by category
  - Values: `standing`, `seated`, `balancing`, `backbends`, `forward_bends`, `twists`, `inversions`, `arm_balances`, `restorative`
- `difficulty` (enum, optional): Filter by difficulty
  - Values: `beginner`, `intermediate`, `advanced`
- `target_area` (string, optional): Filter by target body area

**Example Request:**
```
GET /poses?page=1&page_size=10&difficulty=beginner&search=warrior
```

**Response:** `200 OK`
```json
{
  "poses": [
    {
      "pose_id": 8,
      "name_english": "Warrior I",
      "name_sanskrit": "Virabhadrasana I",
      "category": "standing",
      "difficulty_level": "beginner",
      "description": "A powerful standing pose...",
      "instructions": [
        "Stand in Mountain Pose...",
        "Step left foot back 3-4 feet..."
      ],
      "benefits": "• Strengthens shoulders, arms...",
      "contraindications": "• High blood pressure...",
      "target_areas": ["legs", "hips", "chest", "shoulders", "arms"],
      "image_urls": ["https://placeholder.com/300"],
      "created_at": "2025-12-05T22:04:22Z",
      "updated_at": "2025-12-05T22:04:22Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### GET /poses/{pose_id}
Get single pose by ID.

**Response:** `200 OK`
```json
{
  "pose_id": 1,
  "name_english": "Mountain Pose",
  "name_sanskrit": "Tadasana",
  "category": "standing",
  "difficulty_level": "beginner",
  "description": "Mountain Pose is the foundation...",
  "instructions": [...],
  "benefits": "...",
  "contraindications": "...",
  "target_areas": ["full body", "legs", "core"],
  "image_urls": ["https://placeholder.com/300"],
  "created_at": "2025-12-05T22:04:22Z",
  "updated_at": "2025-12-05T22:04:22Z"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Pose with ID 99999 not found"
}
```

### POST /poses (Admin Only)
Create a new pose.

**Headers:**
- `Authorization: Bearer <admin_token>`
- `Content-Type: application/json`

**Request:**
```json
{
  "name_english": "New Pose",
  "name_sanskrit": "New Asana",
  "category": "standing",
  "difficulty_level": "beginner",
  "description": "A new yoga pose for practice",
  "instructions": [
    "Step 1: Start in mountain pose",
    "Step 2: Lift your arms overhead"
  ],
  "benefits": "Improves strength and flexibility",
  "contraindications": "Avoid with shoulder injury",
  "target_areas": ["shoulders", "core", "legs"],
  "image_urls": ["https://example.com/pose.jpg"]
}
```

**Response:** `201 Created`
```json
{
  "pose_id": 31,
  "name_english": "New Pose",
  ...
}
```

**Error Response:** `403 Forbidden`
```json
{
  "detail": "Admin access required"
}
```

### PUT /poses/{pose_id} (Admin Only)
Update an existing pose.

**Headers:**
- `Authorization: Bearer <admin_token>`
- `Content-Type: application/json`

**Request:** (all fields optional)
```json
{
  "description": "Updated description",
  "benefits": "Updated benefits"
}
```

**Response:** `200 OK`
```json
{
  "pose_id": 31,
  "name_english": "New Pose",
  "description": "Updated description",
  ...
}
```

### DELETE /poses/{pose_id} (Admin Only)
Delete a pose.

**Headers:** `Authorization: Bearer <admin_token>`

**Response:** `204 No Content`

## Upload Endpoints

### POST /upload/image (Admin Only)
Upload and optimize an image.

**Headers:**
- `Authorization: Bearer <admin_token>`
- `Content-Type: multipart/form-data`

**Request:**
```
POST /upload/image
Content-Type: multipart/form-data

file=@image.jpg
```

**Response:** `201 Created`
```json
{
  "url": "/uploads/images/550e8400-e29b-41d4-a716-446655440000.jpg",
  "filename": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "size": 245678,
  "width": 1200,
  "height": 800,
  "format": "JPEG"
}
```

**Validation:**
- Allowed formats: JPEG, PNG, WEBP
- Max file size: 10MB
- Auto-resized to max 2000px dimension
- Compressed with 85% quality

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Invalid file type. Allowed types: .jpg, .jpeg, .png, .webp"
}
```

### GET /upload/images/{filename}
Retrieve an uploaded image.

**Response:** `200 OK` (image file)

**Error Response:** `404 Not Found`
```json
{
  "detail": "Image not found"
}
```

### DELETE /upload/images/{filename} (Admin Only)
Delete an uploaded image.

**Headers:** `Authorization: Bearer <admin_token>`

**Response:** `204 No Content`

## Error Responses

All endpoints may return these common errors:

### 400 Bad Request
Invalid request data or parameters.
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
Missing or invalid authentication token.
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
Insufficient permissions (admin access required).
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
Resource not found.
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
Validation error with detailed field information.
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
Server-side error (check server logs).
```json
{
  "detail": "Internal server error"
}
```

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Expiration:**
- Access token: 24 hours
- Refresh token: 7 days (only if `remember_me` is true)

**Refresh Token:**
Use POST /auth/refresh with refresh token to get new access token.

## Admin Access

Admin-only endpoints require user email ending with `@admin.yogaflow.com` (MVP implementation).

In production, implement proper RBAC (Role-Based Access Control) system.

## Rate Limiting

Auth endpoints have rate limiting:
- 5 requests per minute per IP

Other endpoints currently have no rate limiting (implement in production).

## CORS

Allowed origins (configurable via environment):
- http://localhost:3000
- http://localhost:5173
- http://127.0.0.1:3000
- http://127.0.0.1:5173

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Health Check

### GET /health
Check API health status.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "yogaflow-api",
  "version": "1.0.0"
}
```

## Example Usage (cURL)

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123","name":"John Doe"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123","remember_me":false}'
```

**List Poses:**
```bash
curl http://localhost:8000/api/v1/poses?page=1&page_size=10
```

**Search Poses:**
```bash
curl "http://localhost:8000/api/v1/poses?search=warrior&difficulty=beginner"
```

**Get Pose:**
```bash
curl http://localhost:8000/api/v1/poses/1
```

**Upload Image (Admin):**
```bash
curl -X POST http://localhost:8000/api/v1/upload/image \
  -H "Authorization: Bearer <admin_token>" \
  -F "file=@pose-image.jpg"
```

## Example Usage (JavaScript/Fetch)

**Register:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123',
    name: 'John Doe'
  })
});
const data = await response.json();
const accessToken = data.tokens.access_token;
```

**List Poses:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/poses?page=1&page_size=10');
const data = await response.json();
console.log(data.poses);
```

**Get Pose (Authenticated):**
```javascript
const response = await fetch('http://localhost:8000/api/v1/poses/1', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const pose = await response.json();
```

**Upload Image (Admin):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/v1/upload/image', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});
const imageData = await response.json();
console.log(imageData.url); // Use this URL in <img> tag
```
