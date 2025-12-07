# CI/CD Deployment Guide - YogaFlow

Complete guide for deploying YogaFlow using GitHub Actions CI/CD pipeline to Railway.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [GitHub Actions Setup](#github-actions-setup)
- [Secrets Configuration](#secrets-configuration)
- [Deployment Workflow](#deployment-workflow)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

## Overview

YogaFlow uses a comprehensive CI/CD pipeline built with GitHub Actions that:

- **Quality Gates**: Enforces code quality, testing, and security scanning
- **Automated Testing**: Runs unit tests, integration tests, and E2E tests
- **Docker Builds**: Creates optimized container images with multi-arch support
- **Railway Deployment**: Deploys to Railway with health checks and verification
- **Continuous Monitoring**: Automated health checks every 15 minutes
- **Rollback Capability**: One-click rollback to any previous version

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Actions                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Pull Request          Push to Main          Scheduled           │
│       │                     │                     │              │
│       ├─ Lint              ├─ Build              ├─ Health       │
│       ├─ Test              ├─ Test               │   Checks      │
│       ├─ Security          ├─ Docker             │               │
│       └─ Build             ├─ Deploy             └─ Performance  │
│                            ├─ Verify                 Monitoring  │
│                            └─ Release                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Railway Platform    │
                    ├───────────────────────┤
                    │  ┌─────────────────┐  │
                    │  │  Backend (API)  │  │
                    │  └─────────────────┘  │
                    │  ┌─────────────────┐  │
                    │  │   Frontend      │  │
                    │  └─────────────────┘  │
                    │  ┌─────────────────┐  │
                    │  │   PostgreSQL    │  │
                    │  └─────────────────┘  │
                    └───────────────────────┘
```

## Prerequisites

### 1. Railway Account Setup

1. **Create Railway Account**
   ```bash
   # Sign up at https://railway.app
   # Connect your GitHub account
   ```

2. **Create Railway Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Create project
   railway init

   # Add PostgreSQL
   railway add --database postgres
   ```

3. **Generate Railway Token**
   ```bash
   # Create deployment token
   railway token

   # Save this token - you'll need it for GitHub Secrets
   ```

### 2. GitHub Repository Setup

1. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/yourusername/yoga-app.git
   cd yoga-app
   ```

2. **Enable GitHub Actions**
   - Go to repository Settings → Actions → General
   - Enable "Allow all actions and reusable workflows"

3. **Configure Branch Protection**
   - Settings → Branches → Add rule for `main`
   - Check: "Require status checks to pass before merging"
   - Select required checks:
     - `Backend Quality Checks`
     - `Backend Tests`
     - `Frontend Quality Checks`
     - `Build Verification`

### 3. Environment Setup

Create environment in GitHub:
- Settings → Environments → New environment
- Name: `production`
- Add protection rules:
  - Required reviewers (optional)
  - Wait timer: 0 minutes (or as desired)

## GitHub Actions Setup

### Workflow Files

The CI/CD pipeline consists of 5 workflow files:

1. **`ci-cd-production.yml`** - Main deployment pipeline
   - Triggered on: Push to main, Pull requests
   - Jobs: Lint, Test, Build, Docker, Deploy, Security

2. **`pull-request.yml`** - PR-specific checks
   - Triggered on: Pull request events
   - Jobs: Quick checks, Quality gates, Tests

3. **`security-scan.yml`** - Daily security scans
   - Triggered on: Push, PR, Daily schedule
   - Jobs: Dependency scan, Code scan

4. **`rollback.yml`** - Manual rollback workflow
   - Triggered on: Manual dispatch only
   - Jobs: Validate, Rollback, Verify

5. **`health-check.yml`** - Production monitoring
   - Triggered on: Every 15 minutes, Manual
   - Jobs: Health checks, Performance, Status

### Workflow Execution Order

```
┌──────────────────────────────────────────────────────────────┐
│  1. Code Quality (Parallel)                                  │
│     ├─ Backend Lint & Format Check                           │
│     ├─ Frontend Lint & Type Check                            │
│     └─ Security Scanning (Bandit, Safety, Snyk)              │
└──────────────────────────────────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Testing (Parallel)                                        │
│     ├─ Backend Tests (PostgreSQL)                            │
│     ├─ Frontend Tests (Unit + Integration)                   │
│     └─ E2E Tests (Playwright) [PR only]                      │
└──────────────────────────────────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Build & Package                                           │
│     ├─ Docker Build (Backend)                                │
│     ├─ Docker Push to GHCR                                   │
│     └─ Frontend Build                                        │
└──────────────────────────────────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Deployment (Main branch only)                            │
│     ├─ Deploy Backend to Railway                             │
│     ├─ Deploy Frontend to Railway                            │
│     └─ Run Smoke Tests                                       │
└──────────────────────────────────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Post-Deployment                                           │
│     ├─ Security Scan (Trivy)                                 │
│     ├─ Create Release Notes                                  │
│     └─ Tag Release                                           │
└──────────────────────────────────────────────────────────────┘
```

## Secrets Configuration

### Required GitHub Secrets

Configure in: Settings → Secrets and variables → Actions

#### 1. Railway Deployment Token

```bash
# Generate token
railway token

# Add to GitHub Secrets
Name: RAILWAY_TOKEN
Value: [your-railway-token]
```

#### 2. Docker Registry (GitHub Container Registry)

Automatically available as `GITHUB_TOKEN` - no setup needed.

#### 3. Optional: Security Tools

```bash
# Snyk token (optional)
Name: SNYK_TOKEN
Value: [your-snyk-token]

# Sentry DSN (optional)
Name: SENTRY_DSN
Value: https://your-dsn@sentry.io/project-id
```

### Railway Environment Variables

Configure in Railway Dashboard or CLI:

#### Backend Service

```bash
# Required
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}'
railway variables set ENVIRONMENT=production
railway variables set ALLOWED_ORIGINS=https://your-frontend.railway.app

# Recommended
railway variables set LOG_LEVEL=INFO
railway variables set LOG_FORMAT=json

# Optional
railway variables set SENTRY_DSN=https://your-dsn@sentry.io/project
railway variables set EMAIL_ENABLED=true
railway variables set SMTP_HOST=smtp.gmail.com
railway variables set SMTP_USER=your-email@gmail.com
railway variables set SMTP_PASSWORD=your-app-password
```

#### Frontend Service

```bash
# Required
railway variables set VITE_API_URL=https://your-backend.railway.app
railway variables set NODE_ENV=production
```

## Deployment Workflow

### Automatic Deployment (Push to Main)

1. **Developer pushes to main branch**
   ```bash
   git push origin main
   ```

2. **GitHub Actions triggers automatically**
   - Workflow: `ci-cd-production.yml`
   - All jobs run in sequence

3. **Quality gates must pass**
   - Code linting
   - All tests
   - Security scans

4. **Docker images built and pushed**
   - Backend: `ghcr.io/yourusername/yoga-app-backend:latest`
   - Multi-arch: `linux/amd64`, `linux/arm64`

5. **Deployment to Railway**
   - Backend service deployed
   - Frontend service deployed
   - 30-second stabilization period

6. **Verification**
   - Smoke tests run automatically
   - Health checks verify deployment
   - Release notes created

### Manual Deployment

Trigger deployment manually:

1. Go to Actions → CI/CD Production Pipeline
2. Click "Run workflow"
3. Select branch (usually `main`)
4. Click "Run workflow"

### Pull Request Workflow

1. **Create pull request**
   ```bash
   git checkout -b feature/new-feature
   git push origin feature/new-feature
   ```

2. **Automatic checks run**
   - PR validation
   - Code quality checks
   - All tests
   - Build verification

3. **Review required checks**
   - All status checks must pass
   - Code review required (if configured)

4. **Merge to main**
   - Triggers production deployment automatically

## Monitoring & Health Checks

### Automated Health Checks

Every 15 minutes, automated checks run:

1. **Backend Health**
   - `/health` endpoint check
   - Response time monitoring
   - Database connectivity verification

2. **Frontend Health**
   - Homepage accessibility
   - Static asset loading

3. **Performance Monitoring**
   - Load testing with Artillery
   - Response time tracking
   - SSL certificate expiry check

### Health Check Workflow

Location: `.github/workflows/health-check.yml`

```bash
# Manual trigger
gh workflow run health-check.yml
```

### Incident Creation

If health checks fail:
- GitHub issue created automatically
- Labeled: `incident`, `production`, `urgent`
- Contains diagnostic information and action items

### Monitoring Dashboard

View workflow results:
- GitHub Actions → Health Check workflow
- Check run history and trends
- Review detailed logs for failures

## Rollback Procedures

### When to Rollback

- Critical bugs in production
- Performance degradation
- Security vulnerabilities discovered
- Database migration failures

### Rollback Process

#### 1. Identify Target Version

```bash
# List recent releases
git tag -l --sort=-version:refname | head -10

# Or check GitHub Releases
# https://github.com/yourusername/yoga-app/releases
```

#### 2. Initiate Rollback

**Via GitHub UI:**
1. Go to Actions → Rollback Deployment
2. Click "Run workflow"
3. Fill in:
   - Environment: `production`
   - Version: `v2024.12.05-abc1234`
   - Reason: "Critical bug in user authentication"
4. Click "Run workflow"

**Via GitHub CLI:**
```bash
gh workflow run rollback.yml \
  -f environment=production \
  -f version=v2024.12.05-abc1234 \
  -f reason="Critical bug in user authentication"
```

#### 3. Verify Rollback

1. **Automated checks run**
   - Version validation
   - Deployment execution
   - Health verification

2. **Manual verification**
   ```bash
   # Check health endpoint
   curl https://yoga-app-production.up.railway.app/health

   # Test critical paths
   # - User login
   # - Pose browsing
   # - Practice sessions
   ```

3. **Monitor metrics**
   - Railway dashboard
   - Error rates
   - Response times

#### 4. Post-Rollback

1. **GitHub issue created** with:
   - Rollback details
   - Action items
   - Root cause investigation checklist

2. **Team notification**
   - Review the incident
   - Plan forward fix
   - Update runbook if needed

### Database Rollback

⚠️ **WARNING: Database rollbacks are complex**

If database migration caused the issue:

1. **Backup current database**
   ```bash
   railway db dump > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Restore from backup**
   ```bash
   # Only if you have a backup from before the bad migration
   railway db restore < backup_20241205_120000.sql
   ```

3. **Revert Alembic migration**
   ```bash
   railway run alembic downgrade -1
   ```

## Troubleshooting

### Deployment Failures

#### Build Fails

**Check:**
```bash
# View workflow logs
gh run view [run-id] --log-failed

# Check Docker build
docker build -t test -f backend/Dockerfile.prod backend/
```

**Common causes:**
- Missing dependencies in `requirements.txt`
- Docker syntax errors
- Build context issues

**Fix:**
```bash
# Test locally first
docker build -t yogaflow-backend:test -f backend/Dockerfile.prod backend/
docker run -p 8000:8000 yogaflow-backend:test
```

#### Railway Deployment Fails

**Check:**
```bash
# Railway logs
railway logs

# Check service status
railway status

# Verify environment variables
railway variables
```

**Common causes:**
- Missing environment variables
- PORT binding issues
- Database connectivity

**Fix:**
```bash
# Set missing variables
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Restart service
railway restart
```

#### Health Checks Fail

**Symptoms:**
- `/health` endpoint returns 500
- Database connection errors
- Long response times

**Diagnosis:**
```bash
# Check backend logs
railway logs --service backend

# Test health endpoint
curl -v https://yoga-app-production.up.railway.app/health

# Check database
railway connect postgres
```

**Fix:**
```bash
# Verify DATABASE_URL
railway variables | grep DATABASE_URL

# Check Alembic migrations
railway run alembic current
railway run alembic upgrade head
```

### Test Failures

#### Backend Tests Fail

```bash
# Run tests locally
cd backend
pytest app/tests/ -v

# Check specific test
pytest app/tests/test_specific.py::test_function -v

# Run with database
DATABASE_URL=postgresql://user:pass@localhost:5432/test pytest app/tests/
```

#### Frontend Tests Fail

```bash
# Run tests locally
cd frontend
npm run test:run

# Run specific test
npx vitest run path/to/test.spec.js

# Run with UI
npm run test:ui
```

#### E2E Tests Fail

```bash
# Run Playwright tests locally
cd frontend
npx playwright test

# Debug mode
npx playwright test --debug

# Show browser
npx playwright test --headed
```

### Rollback Failures

**If rollback fails:**

1. **Check version exists**
   ```bash
   git tag -l | grep v2024.12.05
   ```

2. **Verify Railway token**
   ```bash
   # In GitHub Secrets, regenerate RAILWAY_TOKEN
   railway token
   ```

3. **Manual Railway deployment**
   ```bash
   git checkout [version-tag]
   railway up
   ```

### Performance Issues

**High response times:**

```bash
# Check Railway metrics
railway metrics

# Increase workers (backend)
# Edit Dockerfile.prod:
# CMD gunicorn ... --workers 8  # Increase from 4
```

**High memory usage:**

```bash
# Check memory limits
railway ps

# Scale up if needed
# Railway Dashboard → Settings → Resources
```

## Best Practices

### Development Workflow

1. **Feature branches**
   ```bash
   git checkout -b feature/description
   ```

2. **Small, focused PRs**
   - One feature per PR
   - Keep under 500 lines changed

3. **Test locally first**
   ```bash
   # Backend
   pytest backend/tests/

   # Frontend
   npm test

   # E2E
   npx playwright test
   ```

4. **Commit messages**
   - Follow conventional commits
   - `feat:`, `fix:`, `docs:`, `chore:`

### Deployment Best Practices

1. **Deploy during low traffic**
   - Off-peak hours preferred
   - Monitor during deployment

2. **Database migrations**
   - Test migrations locally
   - Backup before migration
   - Make migrations backwards compatible

3. **Environment parity**
   - Keep staging and production similar
   - Test on staging first

4. **Monitoring**
   - Watch health checks post-deployment
   - Monitor error rates in Sentry
   - Check Railway metrics

### Security Best Practices

1. **Secrets management**
   - Never commit secrets
   - Rotate regularly
   - Use GitHub Secrets

2. **Dependency updates**
   - Review security advisories weekly
   - Update dependencies regularly
   - Run `npm audit` and `safety check`

3. **Access control**
   - Limit who can deploy to production
   - Use branch protection rules
   - Require PR reviews

## Support & Resources

### Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Railway Docs](https://docs.railway.app)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Internal Docs
- `DEPLOYMENT_STATUS.md` - Deployment readiness
- `RAILWAY_DEPLOYMENT.md` - Railway-specific guide
- `DATABASE_MIGRATION.md` - Database migration guide

### Troubleshooting
- Check GitHub Actions logs
- Review Railway logs: `railway logs`
- Check deployment verification script output

### Getting Help
- Create issue in repository
- Check Railway Discord
- Review workflow run logs

---

**Last Updated:** December 6, 2025
**Version:** 1.0.0
**Maintained by:** DevOps Team
