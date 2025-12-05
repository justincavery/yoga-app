# YogaFlow - Yoga Practice Application

A comprehensive yoga practice application with guided sequences, pose library, and progress tracking.

![YogaFlow](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-19.x-blue)

## Overview

YogaFlow is a modern web application designed to help users practice yoga with guided sequences, detailed pose instructions, and comprehensive progress tracking. The application features a robust backend API built with FastAPI and a responsive frontend built with React.

### Key Features

- **100+ Yoga Poses**: Comprehensive pose library with detailed instructions, benefits, and modifications
- **25+ Guided Sequences**: Pre-designed sequences for different levels and goals
- **Practice Sessions**: Timer-based practice with auto-transitions and audio cues
- **Progress Tracking**: Track practice history, statistics, and streaks
- **User Profiles**: Personalized profiles with settings and preferences
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Technology Stack

### Backend
- **FastAPI**: Modern, high-performance Python web framework
- **PostgreSQL**: Production-grade relational database
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **Pydantic**: Data validation and settings management
- **JWT**: Secure authentication
- **Sentry**: Error tracking and monitoring

### Frontend
- **React 19**: Modern JavaScript framework
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Zustand**: State management
- **React Query**: Data fetching and caching

### Infrastructure
- **Docker**: Containerization
- **Nginx**: Reverse proxy and static file serving
- **GitHub Actions**: CI/CD pipeline

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 14+** (or Docker)
- **Git**

### Quick Start with Docker

The easiest way to run YogaFlow is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/yourusername/yoga-app.git
cd yoga-app

# Start all services (database, backend, nginx)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

The application will be available at:
- Frontend: http://localhost (port 80)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the development server
npm run dev
```

## Development

### Project Structure

```
yoga-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality (config, database)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── middleware/        # Custom middleware
│   │   └── tests/             # Test suite
│   ├── alembic/               # Database migrations
│   ├── scripts/               # Utility scripts
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── stores/            # State management
│   │   └── utils/             # Utility functions
│   └── package.json           # Node dependencies
├── infrastructure/            # Infrastructure configuration
│   ├── nginx/                 # Nginx configs
│   └── scripts/               # Deployment scripts
├── docs/                      # Documentation
└── docker-compose.yml         # Docker orchestration
```

### Running Tests

#### Backend Tests

```bash
cd backend
pytest app/tests/ -v                    # Run all tests
pytest app/tests/ -v --cov=app          # With coverage
pytest app/tests/test_poses.py -v      # Specific test file
```

#### Frontend Tests

```bash
cd frontend
npm run test                   # Run tests in watch mode
npm run test:run              # Run once
npm run test:ui               # Run with UI
```

### Code Quality

```bash
# Backend linting
cd backend
black app/                    # Format code
flake8 app/                  # Lint code

# Frontend linting
cd frontend
npm run lint                 # ESLint
npm run lint:fix            # Auto-fix issues
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password

#### Poses
- `GET /api/v1/poses` - List all poses (with filtering)
- `GET /api/v1/poses/{id}` - Get pose details
- `POST /api/v1/poses` - Create pose (admin only)

#### Sequences
- `GET /api/v1/sequences` - List all sequences
- `GET /api/v1/sequences/{id}` - Get sequence details
- `POST /api/v1/sequences` - Create sequence (admin only)

#### Practice Sessions
- `POST /api/v1/sessions/start` - Start practice session
- `POST /api/v1/sessions/{id}/complete` - Complete session
- `GET /api/v1/sessions/{id}` - Get session details
- `GET /api/v1/sessions/active` - Get active session

#### History & Statistics
- `GET /api/v1/history` - Get practice history
- `GET /api/v1/history/stats` - Get practice statistics
- `GET /api/v1/history/calendar` - Get calendar data

#### User Profile
- `GET /api/v1/profile` - Get user profile
- `PUT /api/v1/profile` - Update profile
- `PUT /api/v1/profile/password` - Change password

## Deployment

### Production Deployment

See detailed deployment documentation:
- [Deployment Checklist](docs/deployment-checklist.md)
- [Security Checklist](docs/security-checklist.md)

#### Quick Production Deployment

1. **Configure Production Environment**
   ```bash
   # Backend
   cp backend/.env.production backend/.env
   # Edit with production values

   # Frontend
   cp frontend/.env.production frontend/.env
   # Edit with production values
   ```

2. **Deploy with Docker**
   ```bash
   # Build and start production containers
   docker-compose -f docker-compose.prod.yml up -d

   # Run database migrations
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

   # Check service health
   docker-compose -f docker-compose.prod.yml ps
   ```

3. **Configure SSL/TLS**
   - Obtain SSL certificate (Let's Encrypt recommended)
   - Update nginx configuration
   - Restart nginx service

4. **Set up monitoring**
   - Configure Sentry for error tracking
   - Set up uptime monitoring
   - Configure backup schedule

### Environment Variables

#### Backend Required Variables
- `SECRET_KEY`: JWT secret key (64+ random characters)
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_ORIGINS`: Comma-separated list of frontend URLs
- `EMAIL_ENABLED`: Enable email functionality (true/false)
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`: Email configuration

#### Frontend Required Variables
- `VITE_API_URL`: Backend API URL
- `VITE_APP_ENV`: Environment (development/production)

See `.env.example` files for complete list of variables.

## Database Migrations

### Creating Migrations

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file
# Edit if necessary: alembic/versions/xxxxx_description.py

# Apply migration
alembic upgrade head
```

### Managing Migrations

```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision>
```

## Monitoring & Logging

### Application Logs

```bash
# Backend logs (Docker)
docker-compose logs -f backend

# Backend logs (manual)
tail -f backend/logs/app.log

# Frontend logs (development)
# View in browser console
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connectivity
docker-compose exec backend python -c "from app.core.database import engine; print('OK' if engine else 'FAIL')"
```

### Error Tracking

Sentry is configured for error tracking. Configure `SENTRY_DSN` in your environment to enable:

```bash
# Backend
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production

# Frontend
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Security

### Security Features

- **Authentication**: JWT-based authentication with refresh tokens
- **Password Security**: Bcrypt hashing with configurable rounds
- **Rate Limiting**: Protection against brute force attacks
- **CORS**: Configured for production domains only
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Prevention**: ORM-based queries
- **XSS Protection**: Output encoding and CSP headers

### Security Best Practices

1. **Never commit secrets** to version control
2. **Use strong passwords** for database and admin accounts
3. **Enable HTTPS** in production
4. **Keep dependencies updated** (`pip-audit`, `npm audit`)
5. **Review security checklist** before deployment
6. **Configure backups** and test restoration
7. **Monitor logs** for suspicious activity
8. **Use environment variables** for all secrets

See [Security Checklist](docs/security-checklist.md) for complete security guidelines.

## Troubleshooting

### Common Issues

#### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify connection string
echo $DATABASE_URL
```

#### Frontend Can't Connect to Backend

```bash
# Check CORS configuration
# Ensure frontend URL is in ALLOWED_ORIGINS

# Verify backend is running
curl http://localhost:8000/health

# Check frontend API URL
cat frontend/.env | grep VITE_API_URL
```

#### Migration Conflicts

```bash
# Check current version
alembic current

# Resolve by downgrading and re-applying
alembic downgrade -1
alembic upgrade head
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/React
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## Testing

### Test Coverage

- **Backend**: 80%+ coverage target
- **Frontend**: 70%+ coverage target

Run coverage reports:

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
npm run test:run -- --coverage
open coverage/index.html
```

## Performance

### Optimization

- **Database**: Connection pooling, query optimization
- **API**: Response caching, pagination
- **Frontend**: Code splitting, lazy loading, image optimization
- **CDN**: Static assets served via nginx with caching

### Performance Targets

- Page load time: < 2 seconds
- API response time: < 200ms (p95)
- Time to interactive: < 3 seconds
- Lighthouse score: > 90

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [/docs](/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/yoga-app/issues)
- **Email**: support@yogaflow.app

## Acknowledgments

- Yoga pose content and sequences by certified yoga instructors
- UI/UX design inspired by modern fitness applications
- Built with open-source technologies

## Roadmap

See [roadmap.md](plans/roadmap.md) for detailed development roadmap.

### Upcoming Features

- **Phase 2** (Q1 2026):
  - Custom sequence builder
  - Advanced statistics and charts
  - Breathing exercises
  - Goal setting and tracking

- **Phase 3** (Q2 2026):
  - Achievement badges
  - Meditation timer
  - Video demonstrations
  - Social features

---

**Version**: 1.0.0
**Last Updated**: December 5, 2025
**Status**: Production Ready
