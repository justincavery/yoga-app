# YogaFlow Backend API

FastAPI-based REST API for YogaFlow yoga practice application.

## Features

- **JWT Authentication** - Secure token-based auth with bcrypt password hashing
- **PostgreSQL-Compatible Schema** - Database models ready for production
- **Centralized Logging** - Structured JSON logging with request tracking
- **OpenAPI Documentation** - Auto-generated interactive API docs
- **CORS Support** - Configured for frontend integration
- **Error Handling** - Consistent error responses across all endpoints
- **Security** - Implements OWASP best practices (SQL injection, XSS, CSRF protection)

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ (for production) or SQLite (for development)
- Virtual environment

### Installation

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv ../venv
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Edit `.env` file:

```env
# Development (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./yogaflow.db

# Production (PostgreSQL)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/yogaflow

# Generate secure secret key:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secure-secret-key-here

DEBUG=true
ENVIRONMENT=development
```

### Running the Server

```bash
# Development server with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Production server with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

The API will be available at:
- **API:** http://localhost:8000/api/v1
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI:** http://localhost:8000/openapi.json

## API Documentation

See [API_CONTRACT.md](./API_CONTRACT.md) for complete API documentation.

### Quick API Examples

**Register User:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "Test User", "password": "SecurePass123", "experience_level": "beginner"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'
```

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection & session
│   │   ├── security.py         # JWT & password utilities
│   │   └── logging_config.py   # Centralized logging
│   ├── models/                 # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── pose.py
│   │   ├── sequence.py
│   │   ├── practice_session.py
│   │   ├── favorites.py
│   │   └── achievement.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   └── user.py
│   ├── api/
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   └── v1/endpoints/
│   │       └── auth.py         # Authentication endpoints
│   ├── services/               # Business logic
│   │   └── auth_service.py
│   └── middleware/             # Custom middleware
│       ├── error_handler.py
│       └── request_logging.py
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── API_CONTRACT.md            # API documentation
└── README.md                  # This file
```

## Database Schema

The application uses SQLAlchemy ORM with support for both SQLite (development) and PostgreSQL (production).

### Tables

- **users** - User accounts and authentication
- **poses** - Yoga poses/asanas
- **sequences** - Ordered collections of poses
- **sequence_poses** - Junction table for sequences and poses
- **practice_sessions** - User practice history
- **user_favorites** - Saved sequences
- **achievements** - Available badges/milestones
- **user_achievements** - Earned achievements

See [POSTGRESQL_SCHEMA.sql](./POSTGRESQL_SCHEMA.sql) for complete schema.

## Security

### Implemented Security Features

✅ Password hashing with bcrypt (work factor 12)
✅ JWT tokens with secure expiration
✅ SQL injection protection (parameterized queries)
✅ XSS protection (input validation, output escaping)
✅ CSRF protection (stateless tokens)
✅ CORS configuration
✅ Rate limiting (planned for production)
✅ Secure session management

### Security Best Practices

- Never commit `.env` file to version control
- Use strong, random SECRET_KEY in production
- Enable HTTPS in production (TLS 1.3)
- Rotate secrets regularly
- Monitor failed login attempts
- Keep dependencies updated
- Run security audits regularly

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## Logging

The application uses structured logging (JSON format in production) with the following features:

- Request/response logging with timing
- Authentication event logging
- Error logging with stack traces
- Configurable log levels
- Sensitive data exclusion

Logs include:
- HTTP method and path
- Status code
- Duration (ms)
- User ID (for authenticated requests)
- Error details (without sensitive data)

## Development

### Adding New Endpoints

1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Create service in `app/services/`
4. Create endpoint in `app/api/v1/endpoints/`
5. Register router in `app/main.py`

### Database Migrations

For production, use Alembic for database migrations:

```bash
# Initialize Alembic (already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Using Docker

```bash
# Build image
docker build -t yogaflow-backend .

# Run container
docker run -p 8000:8000 --env-file .env yogaflow-backend
```

### Using Gunicorn (Production)

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

### Environment Variables

Required in production:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Strong random key for JWT signing
- `ENVIRONMENT=production`
- `DEBUG=false`
- `ALLOWED_ORIGINS` - Frontend URLs

Optional:
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` - For email features
- `LOG_LEVEL` - Logging verbosity
- `BCRYPT_ROUNDS` - Password hashing work factor (default: 12)

## Troubleshooting

### Database Connection Issues

- Check DATABASE_URL format
- Verify PostgreSQL is running
- Check firewall/network settings
- Ensure database exists

### Authentication Issues

- Verify SECRET_KEY is set
- Check token expiration settings
- Review CORS configuration
- Check client Authorization header format

### Performance Issues

- Enable database query logging (DEBUG=true)
- Check database indexes
- Review N+1 query patterns
- Consider connection pooling settings

## Contributing

1. Follow CLAUDE.md guidelines
2. Use centralized logging
3. No single-letter variable names
4. Write integration tests
5. Document API changes in API_CONTRACT.md

## License

Proprietary - YogaFlow Application

## Support

- **Documentation:** /docs or /redoc
- **API Contract:** API_CONTRACT.md
- **Issues:** Report to @backend-agent
