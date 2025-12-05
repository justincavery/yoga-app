# YogaFlow Infrastructure

This directory contains infrastructure configuration and documentation.

## Local Development Setup

### Prerequisites
- Docker and Docker Compose installed
- Python 3.10+ installed
- PostgreSQL client tools (optional, for direct DB access)

### Starting the Development Environment

1. **Start PostgreSQL databases:**
   ```bash
   docker compose up -d
   ```

2. **Verify database is running:**
   ```bash
   docker compose ps
   psql postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev -c "SELECT version();"
   ```

3. **Stop databases:**
   ```bash
   docker compose down
   ```

4. **Stop and remove volumes (CAUTION: deletes all data):**
   ```bash
   docker compose down -v
   ```

## Database Configuration

### Development Database
- **Host:** localhost
- **Port:** 5432
- **Database:** yogaflow_dev
- **Username:** yogaflow
- **Password:** yogaflow_dev_password
- **Connection String:** `postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev`

### Test Database
- **Host:** localhost
- **Port:** 5433
- **Database:** yogaflow_test
- **Username:** yogaflow_test
- **Password:** yogaflow_test_password
- **Connection String:** `postgresql://yogaflow_test:yogaflow_test_password@localhost:5433/yogaflow_test`

## Monitoring Setup

### Sentry Configuration

Sentry is configured for error tracking and performance monitoring.

1. **Create a Sentry account** at https://sentry.io
2. **Create a new project** for YogaFlow
3. **Copy the DSN** from project settings
4. **Add to .env file:**
   ```
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
   ```

### Logging

The application uses a centralized logging framework with:
- **Structured JSON logging** for production
- **Human-readable logging** for development
- **Multiple log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Context injection** (request_id, user_id, etc.)
- **File and console output**

Configuration via environment variables:
```bash
LOG_LEVEL=INFO          # Minimum log level
LOG_FORMAT=json         # 'json' or 'human'
LOG_FILE=logs/app.log   # Optional file output
```

## CI/CD Pipeline

GitHub Actions workflows are configured for:

### Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)
- **Lint:** Code style checks (flake8, black, isort, ESLint)
- **Test:** Unit and integration tests with coverage
- **Build:** Application build process
- **Deploy:** Automatic deployment to staging/production

### Security Scanning (`.github/workflows/security-scan.yml`)
- **Dependency scanning:** safety, npm audit
- **Code security:** bandit for Python
- **Scheduled scans:** Daily at 2 AM UTC

## Production Deployment (To Be Configured)

The following will be set up in future batches:
- Cloud hosting (DigitalOcean/AWS/GCP)
- Container registry for Docker images
- Load balancer configuration
- SSL/TLS certificates
- CDN for static assets
- Backup and disaster recovery
- Monitoring dashboards

## Health Checks

PostgreSQL containers include health checks:
```bash
# Check container health
docker compose ps

# Manual health check
docker exec yogaflow-postgres pg_isready -U yogaflow -d yogaflow_dev
```

## Troubleshooting

### Port Already in Use
If ports 5432 or 5433 are already in use:
```bash
# Check what's using the port
lsof -i :5432

# Stop local PostgreSQL if running
brew services stop postgresql@14

# Or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# View database logs
docker compose logs postgres

# Connect to database shell
docker exec -it yogaflow-postgres psql -U yogaflow -d yogaflow_dev
```

### Reset Database
```bash
# Stop and remove everything
docker compose down -v

# Start fresh
docker compose up -d
```

## Next Steps

1. **Backend Agent:** Use these database connection details to set up SQLAlchemy models
2. **Frontend Agent:** API will be available at http://localhost:8000 (once backend is running)
3. **CI/CD:** Pipeline is ready, will run on first push to GitHub
