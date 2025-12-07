# Railway Deployment Guide - YogaFlow

Complete guide to deploying YogaFlow to Railway (https://yoga-app-production.up.railway.app/)

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Deploy](#quick-deploy)
- [Environment Variables](#environment-variables)
- [Deployment Configuration](#deployment-configuration)
- [Database Migration](#database-migration)
- [Troubleshooting](#troubleshooting)
- [Post-Deployment](#post-deployment)

## Prerequisites

1. **Railway Account**
   - Sign up at https://railway.app (free tier available)
   - Connect your GitHub account

2. **GitHub Repository**
   - Project must be pushed to GitHub
   - Repository: `justincavery/yoga-app` (or your fork)

3. **Railway CLI (Optional)**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

## Quick Deploy

### Method 1: GitHub Deploy (Recommended)

1. **Go to Railway Dashboard**
   - Visit https://railway.app/dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `yoga-app` repository

2. **Railway Auto-Detection**
   - Railway will detect `railway.json` files in:
     - `backend/railway.json` (Backend service)
     - `frontend/railway.json` (Frontend service)
   - Both services will be configured automatically

3. **Add PostgreSQL Database**
   - In Railway project, click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway creates database with `DATABASE_URL` automatically

### Method 2: Railway CLI

```bash
# Clone repository
git clone https://github.com/justincavery/yoga-app.git
cd yoga-app

# Login to Railway
railway login

# Initialize Railway project
railway init

# Add PostgreSQL
railway add --database postgres

# Deploy backend
cd backend
railway up

# Deploy frontend
cd ../frontend
railway up
```

## Environment Variables

### Backend Environment Variables

Set these in Railway Dashboard → Backend Service → Variables:

```bash
# Database (automatically set by Railway when you add PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Security - Generate with: openssl rand -hex 32
SECRET_KEY=your-generated-secret-key-here

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS - Set after frontend deploys
ALLOWED_ORIGINS=https://your-frontend-domain.up.railway.app,https://yoga-app-production.up.railway.app

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Email (Optional)
EMAIL_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yogaflow.app
FRONTEND_URL=https://your-frontend-domain.up.railway.app

# Monitoring (Optional)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Upload Configuration
UPLOAD_DIRECTORY=/app/uploads
MAX_UPLOAD_SIZE_MB=10
```

**How to Set Variables:**

**Via Railway Web UI:**
1. Click on Backend service
2. Go to "Variables" tab
3. Click "New Variable"
4. Add each key-value pair
5. Click "Deploy" to apply

**Via Railway CLI:**
```bash
cd backend
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set ENVIRONMENT=production
railway variables set ALLOWED_ORIGINS=https://your-frontend.railway.app
```

### Frontend Environment Variables

Set these in Railway Dashboard → Frontend Service → Variables:

```bash
# Backend API URL (set after backend deploys)
VITE_API_URL=https://your-backend-domain.up.railway.app

# Environment
NODE_ENV=production
```

**Via Railway CLI:**
```bash
cd frontend
railway variables set VITE_API_URL=https://your-backend.railway.app
railway variables set NODE_ENV=production
```

## Deployment Configuration

### Backend Configuration (`backend/railway.json`)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.prod"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

**Key Points:**
- Uses Docker builder for Python backend
- Dockerfile: `Dockerfile.prod` (configured for Railway)
- Health check at `/health` endpoint
- Auto-restarts on failure (max 10 retries)
- **PORT binding**: Dockerfile uses `$PORT` environment variable (Railway requirement)

### Frontend Configuration (`frontend/railway.json`)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm install && npm run build",
    "watchPatterns": ["src/**"]
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "npm run preview -- --host 0.0.0.0 --port ${PORT:-3000}",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Key Points:**
- Uses Nixpacks builder for Node.js
- Builds with Vite (`npm run build`)
- Serves with Vite preview server
- Watches `src/**` for changes (auto-rebuild)

## Database Migration

Railway uses PostgreSQL instead of SQLite. Migration is automatic.

### 1. Database URL Format

Railway provides PostgreSQL URL in format:
```
postgresql://user:password@host:port/database
```

For async SQLAlchemy (used in YogaFlow):
```
postgresql+asyncpg://user:password@host:port/database
```

### 2. Automatic Migration

The backend Dockerfile includes Alembic migrations:

```dockerfile
# In Dockerfile.prod startup script
alembic upgrade head
```

This runs automatically on deployment.

### 3. Manual Migration (if needed)

```bash
# Via Railway CLI
cd backend
railway run alembic upgrade head

# Or via Railway dashboard shell
alembic upgrade head
```

### 4. Verify Migration

Check Railway logs:
```bash
railway logs
```

Look for:
```
INFO  [alembic.runtime.migration] Running upgrade -> head
INFO  Database initialized successfully
```

## Database Connection Configuration

The backend automatically handles database URL conversion:

```python
# app/core/database.py handles both formats:
# - SQLite: sqlite+aiosqlite:///./yogaflow.db
# - PostgreSQL: postgresql+asyncpg://...
```

Railway's `DATABASE_URL` is automatically converted to async format.

## Troubleshooting

### Issue: Backend Build Fails

**Check:**
```bash
railway logs --build
```

**Common Causes:**
- Missing dependencies in `requirements.txt`
- Docker build errors
- Python version mismatch

**Fix:**
- Ensure `requirements.txt` is complete
- Check Dockerfile.prod syntax
- Verify Python 3.11 is specified

### Issue: Backend Deployment Fails

**Check:**
```bash
railway logs
```

**Common Causes:**
- Missing `SECRET_KEY` environment variable
- Wrong `DATABASE_URL` format
- Port binding issues

**Fix:**
```bash
# Set SECRET_KEY
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Verify DATABASE_URL exists
railway variables | grep DATABASE_URL

# Check PORT is being used (should see in logs)
railway logs | grep PORT
```

### Issue: Frontend Can't Connect to Backend

**Symptoms:**
- CORS errors in browser console
- API calls fail
- Login doesn't work

**Fix:**

1. **Update Backend CORS:**
```bash
cd backend
railway variables set ALLOWED_ORIGINS=https://your-frontend.railway.app
```

2. **Update Frontend API URL:**
```bash
cd frontend
railway variables set VITE_API_URL=https://your-backend.railway.app
```

3. **Redeploy both services:**
```bash
railway up --detach
```

### Issue: Database Connection Fails

**Check:**
```bash
railway variables | grep DATABASE_URL
railway status
```

**Fix:**
- Verify PostgreSQL service is running
- Check DATABASE_URL is set correctly
- Ensure backend has access to database service

### Issue: Health Check Fails

**Check:**
```bash
curl https://your-backend.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "yogaflow-api",
  "version": "1.0.0"
}
```

**Fix:**
- Check backend logs for errors
- Verify database connection
- Ensure all environment variables are set

### Issue: Port Binding Error

**Error in logs:**
```
Error: Cannot bind to port 8000
```

**Fix:**
The Dockerfile must use Railway's `$PORT` variable:

```dockerfile
CMD gunicorn app.main:app \
     --bind 0.0.0.0:${PORT:-8000}
```

This is already configured in `Dockerfile.prod`.

## Post-Deployment

### 1. Generate Domains

**Backend:**
1. Go to Backend service → Settings → Networking
2. Click "Generate Domain"
3. Copy domain (e.g., `backend-production-xyz.up.railway.app`)

**Frontend:**
1. Go to Frontend service → Settings → Networking
2. Click "Generate Domain"
3. Copy domain (e.g., `frontend-production-xyz.up.railway.app`)

### 2. Update CORS and API URLs

**Update Backend CORS:**
```bash
railway variables set -s backend ALLOWED_ORIGINS=https://frontend-production-xyz.up.railway.app
```

**Update Frontend API URL:**
```bash
railway variables set -s frontend VITE_API_URL=https://backend-production-xyz.up.railway.app
```

### 3. Custom Domain (Optional)

1. Go to Frontend service → Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `yogaflow.app`)
4. Add CNAME record to your DNS:
   ```
   CNAME @ frontend-production-xyz.up.railway.app
   ```

### 4. Monitoring Setup

**Railway Built-in:**
- Metrics (CPU, Memory, Network)
- Logs (real-time)
- Deployments (history, rollback)

**Sentry (Optional):**
```bash
# Sign up at sentry.io
# Create new project
# Copy DSN and set:
railway variables set -s backend SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

### 5. Database Backups

Railway automatically backs up PostgreSQL databases.

**Manual backup:**
```bash
# Download database dump
railway db dump > backup.sql

# Restore from dump
railway db restore < backup.sql
```

### 6. Testing Checklist

- [ ] Backend health check returns 200 OK
- [ ] Frontend loads in browser
- [ ] User registration works
- [ ] User login works
- [ ] Poses list displays
- [ ] Search and filters work
- [ ] Practice sessions can be started
- [ ] Data persists in PostgreSQL
- [ ] Email sending works (if enabled)
- [ ] File uploads work
- [ ] Mobile responsive design works

### 7. Performance Optimization

**Backend:**
- Enable connection pooling (already configured)
- Use Redis for caching (optional upgrade)
- Monitor slow queries with Sentry

**Frontend:**
- Vite optimizes build automatically
- Consider CDN for static assets
- Enable compression (Railway does this)

## Cost Estimate

**Railway Pricing (2025):**

**Free Tier:**
- $5 free credits per month
- Good for testing and small projects

**Production (Pay-as-you-go):**
- Backend: ~$5-7/month (512MB RAM, Docker)
- Frontend: ~$1-2/month (static hosting)
- PostgreSQL: ~$5-10/month (1GB storage, 100 connections)

**Total: ~$10-20/month**

## Railway CLI Reference

```bash
# Login
railway login

# Link to existing project
railway link

# Create new project
railway init

# Add PostgreSQL
railway add --database postgres

# Deploy current directory
railway up

# Deploy specific service
railway up -s backend

# View logs
railway logs

# View logs for specific service
railway logs -s backend

# Set environment variable
railway variables set KEY=value

# Set variable for specific service
railway variables set -s backend SECRET_KEY=value

# List all variables
railway variables

# Open Railway dashboard
railway open

# Check deployment status
railway status

# Run command in Railway environment
railway run python manage.py migrate

# Connect to database
railway connect postgres

# Download database dump
railway db dump > backup.sql
```

## Security Best Practices

1. **Never commit secrets**
   - Use `.env.example` for documentation
   - Add `.env` to `.gitignore`
   - Use Railway environment variables for all secrets

2. **Strong SECRET_KEY**
   ```bash
   openssl rand -hex 32
   ```
   - Minimum 32 bytes
   - Use cryptographically random values
   - Rotate regularly

3. **CORS Configuration**
   - Only allow your frontend domain
   - Don't use wildcard (`*`) in production
   - Update when domains change

4. **HTTPS Only**
   - Railway provides HTTPS automatically
   - Enforce HTTPS in backend (configured)
   - Use secure cookies

5. **Database Security**
   - Railway manages PostgreSQL security
   - Use connection pooling
   - Enable SSL (Railway default)

## Support and Resources

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Railway Status:** https://status.railway.app
- **YogaFlow Issues:** https://github.com/justincavery/yoga-app/issues

## Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub (main branch)
- [ ] `railway.json` files configured
- [ ] `Dockerfile.prod` uses `$PORT` variable
- [ ] `.env.example` documented
- [ ] Database migrations tested locally

### Deployment
- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] Environment variables configured
- [ ] Domains generated

### Post-Deployment
- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] CORS configured properly
- [ ] Database migrations ran
- [ ] User flows tested end-to-end
- [ ] Monitoring configured (Sentry)
- [ ] Backups verified

### Production
- [ ] Custom domain configured (optional)
- [ ] SSL certificates active
- [ ] Error tracking active
- [ ] Performance monitoring active
- [ ] Documentation updated

---

**Deployment Status:** ✅ Ready for Railway
**Target URL:** https://yoga-app-production.up.railway.app/
**Last Updated:** December 6, 2025
**Configuration Version:** 2.0
