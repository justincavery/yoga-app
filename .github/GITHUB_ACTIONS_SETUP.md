# GitHub Actions Setup Guide

Quick setup guide for YogaFlow CI/CD pipeline.

## Prerequisites

- GitHub repository with admin access
- Railway account with project created
- Railway CLI installed locally

## Setup Steps (10 minutes)

### 1. Generate Railway Token

```bash
# Install Railway CLI if not already installed
npm install -g @railway/cli

# Login to Railway
railway login

# Generate deployment token
railway token
```

**Copy the token** - you'll need it in the next step.

### 2. Configure GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:

| Name | Value | Description |
|------|-------|-------------|
| `RAILWAY_TOKEN` | [your-token-from-step-1] | Railway deployment token |

### 3. Configure Railway Environment Variables

**Backend Service:**
```bash
# Switch to backend service
railway link

# Set required variables
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}'
railway variables set ENVIRONMENT=production

# After frontend deploys, add CORS
railway variables set ALLOWED_ORIGINS=https://your-frontend.railway.app
```

**Frontend Service:**
```bash
# Switch to frontend service
railway link

# Set required variables
railway variables set VITE_API_URL=https://your-backend.railway.app
railway variables set NODE_ENV=production
```

### 4. Create GitHub Environment

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name: `production`
4. Click **Configure environment**
5. (Optional) Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches: `main` only

### 5. Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Under "Actions permissions", select:
   - ✅ Allow all actions and reusable workflows
3. Under "Workflow permissions", select:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

### 6. Configure Branch Protection (Recommended)

1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - Select required checks:
     - `Backend Quality Checks`
     - `Backend Tests`
     - `Frontend Quality Checks`
     - `Build Verification`
5. Click **Create**

## Workflow Overview

### Available Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI/CD Production Pipeline** | Push to main, PR | Main deployment pipeline |
| **Pull Request Checks** | Pull request | PR-specific quality gates |
| **Security Scanning** | Push, PR, Daily | Dependency and code security |
| **Rollback Deployment** | Manual | Roll back to previous version |
| **Production Health Check** | Every 15 min, Manual | Monitor production health |

### Workflow Triggers

**Automatic:**
- Push to `main` → Full CI/CD pipeline runs → Deploys to production
- Pull request → PR checks run → Must pass before merge
- Every 15 minutes → Health check runs
- Daily at 2 AM UTC → Security scan runs

**Manual:**
- Rollback: Actions → Rollback Deployment → Run workflow
- Health check: Actions → Production Health Check → Run workflow
- CI/CD: Actions → CI/CD Production Pipeline → Run workflow

## First Deployment

### Step 1: Push to Main

```bash
git checkout main
git pull origin main

# If you have changes to commit:
git add .
git commit -m "chore: enable CI/CD pipeline"
git push origin main
```

### Step 2: Monitor Deployment

1. Go to **Actions** tab in GitHub
2. Click on the running workflow
3. Watch each job execute:
   - ✅ Backend lint
   - ✅ Backend test
   - ✅ Frontend lint
   - ✅ Frontend test
   - ✅ Docker build
   - ✅ Deploy production
   - ✅ Security scan

### Step 3: Verify Deployment

After deployment completes:

```bash
# Check backend health
curl https://your-backend.railway.app/health

# Should return:
# {"status":"healthy","service":"yogaflow-api","version":"1.0.0"}

# Check frontend
curl https://your-frontend.railway.app

# Should return HTML
```

Or use the verification script:
```bash
./infrastructure/scripts/verify_deployment.sh \
  https://your-backend.railway.app \
  https://your-frontend.railway.app
```

## Common Operations

### Deploy to Production

**Automatic (recommended):**
```bash
git checkout main
git merge your-feature-branch
git push origin main
```

**Manual trigger:**
1. Go to Actions → CI/CD Production Pipeline
2. Click "Run workflow"
3. Select branch: `main`
4. Click "Run workflow"

### Rollback

1. Find the version to rollback to:
   - Check GitHub Releases tab
   - Or: `git tag -l --sort=-version:refname | head -10`

2. Go to Actions → Rollback Deployment

3. Click "Run workflow" and fill in:
   - Environment: `production`
   - Version: `v2024.12.05-abc1234`
   - Reason: "Critical bug in authentication"

4. Click "Run workflow"

5. Monitor the rollback in Actions tab

### View Logs

**GitHub Actions logs:**
1. Go to Actions tab
2. Click on workflow run
3. Click on job name
4. Expand steps to see detailed logs

**Railway logs:**
```bash
# Backend logs
railway logs --service backend

# Frontend logs
railway logs --service frontend

# Real-time logs
railway logs --service backend --tail
```

### Monitor Health

**Automatic monitoring:**
- Health checks run every 15 minutes
- Check Actions tab for "Production Health Check" runs
- GitHub issues created automatically if health checks fail

**Manual check:**
1. Go to Actions → Production Health Check
2. Click "Run workflow"
3. View results

## Troubleshooting

### Deployment Fails

**Check workflow logs:**
1. Go to Actions tab
2. Click failed workflow run
3. Click failed job
4. Review error messages

**Common issues:**

| Error | Cause | Solution |
|-------|-------|----------|
| "RAILWAY_TOKEN not found" | Secret not configured | Add secret in Settings → Secrets |
| "Backend tests failed" | Test errors | Fix tests locally first |
| "Docker build failed" | Dockerfile syntax | Test Docker build locally |
| "Health check failed" | Backend not responding | Check Railway logs |

### Health Checks Fail

```bash
# Check Railway service status
railway status

# View recent logs
railway logs --service backend

# Check environment variables
railway variables

# Restart service
railway restart --service backend
```

### Can't Access Deployment

**Check domains:**
```bash
# List services
railway status

# Each service should have a domain
# If not, generate one:
# Railway Dashboard → Service → Settings → Networking → Generate Domain
```

**Check CORS:**
```bash
# Update backend ALLOWED_ORIGINS
railway variables set ALLOWED_ORIGINS=https://your-frontend.railway.app
```

## Monitoring

### Health Check Dashboard

View health check history:
1. Go to Actions tab
2. Filter by "Production Health Check"
3. Review success/failure trends

### Performance Monitoring

**Railway Dashboard:**
- CPU usage
- Memory usage
- Network traffic
- Request latency

**Access:**
- https://railway.app/dashboard
- Select your project
- Click on service
- View metrics

### Error Tracking (Optional)

**Enable Sentry:**
```bash
# Sign up at sentry.io
# Create new project
# Get DSN

# Set in Railway
railway variables set SENTRY_DSN=https://your-dsn@sentry.io/project
```

## Security

### Secret Rotation

**Railway token:**
```bash
# Generate new token
railway token

# Update GitHub secret
# Settings → Secrets → RAILWAY_TOKEN → Update

# Test deployment
# Actions → CI/CD Production Pipeline → Run workflow
```

**Application secret key:**
```bash
# Generate new key
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# This will trigger a redeploy
```

### Dependency Updates

**Automatic (recommended):**
1. Enable Dependabot:
   - Settings → Security → Dependabot
   - Enable version updates
2. Review and merge Dependabot PRs

**Manual:**
```bash
# Backend
cd backend
pip list --outdated
pip install --upgrade [package]
pip freeze > requirements.txt

# Frontend
cd frontend
npm outdated
npm update
```

## Best Practices

### Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Develop and test locally**
   ```bash
   # Backend tests
   cd backend && pytest app/tests/

   # Frontend tests
   cd frontend && npm test
   ```

3. **Create pull request**
   - Push branch to GitHub
   - Create PR
   - Wait for checks to pass
   - Request review

4. **Merge to main**
   - Squash and merge
   - Delete branch
   - Automatic deployment to production

### Commit Messages

Use conventional commits:
```
feat: add user profile page
fix: resolve authentication bug
docs: update deployment guide
chore: update dependencies
test: add integration tests
refactor: simplify auth logic
```

### Code Review

Before merging:
- ✅ All tests pass
- ✅ Code reviewed by team member
- ✅ No merge conflicts
- ✅ Documentation updated

## Support

### Documentation
- [CI/CD Deployment Guide](../infrastructure/CICD_DEPLOYMENT_GUIDE.md)
- [Railway Deployment](../infrastructure/RAILWAY_DEPLOYMENT.md)
- [Deployment Readiness](../infrastructure/DEPLOYMENT_READINESS_ASSESSMENT.md)

### External Resources
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Railway Docs](https://docs.railway.app)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Getting Help
- Check workflow logs in Actions tab
- Review Railway logs: `railway logs`
- Create issue in repository
- Check Railway Discord

---

**Setup Complete!** You're ready to deploy to production with CI/CD.

**Next Step:** Push to main branch to trigger your first automated deployment.
