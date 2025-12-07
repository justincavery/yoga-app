# Deploy YogaFlow to Railway - Quick Start

**Target URL:** https://yoga-app-production.up.railway.app/

## 🚀 Quick Deploy (5 minutes)

### Option 1: One-Click Deploy (Easiest)

1. **Go to Railway**
   - Visit https://railway.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `yoga-app` repository
   - Railway auto-detects configuration

3. **Add PostgreSQL**
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway creates `DATABASE_URL` automatically

4. **Configure Environment Variables**

   **Backend Service:**
   ```bash
   SECRET_KEY=<run: openssl rand -hex 32>
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://your-frontend.railway.app
   ```

   **Frontend Service:**
   ```bash
   VITE_API_URL=https://your-backend.railway.app
   NODE_ENV=production
   ```

5. **Generate Domains**
   - Backend: Settings → Networking → Generate Domain
   - Frontend: Settings → Networking → Generate Domain

6. **Update CORS**
   - Update backend `ALLOWED_ORIGINS` with frontend domain
   - Redeploy backend

### Option 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd /path/to/yoga-app
railway init

# Add PostgreSQL
railway add --database postgres

# Set environment variables
cd backend
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set ENVIRONMENT=production

# Deploy backend
railway up

# Deploy frontend
cd ../frontend
railway variables set VITE_API_URL=https://your-backend.railway.app
railway up

# Generate domains
railway domain

# Verify deployment
cd ../infrastructure/scripts
./verify_deployment.sh https://your-backend.railway.app https://your-frontend.railway.app
```

## ✅ Deployment Checklist

- [ ] Railway account created
- [ ] Project connected to GitHub
- [ ] PostgreSQL database added
- [ ] Backend `SECRET_KEY` generated (32+ bytes)
- [ ] Backend `DATABASE_URL` configured (automatic)
- [ ] Backend domain generated
- [ ] Frontend `VITE_API_URL` configured
- [ ] Frontend domain generated
- [ ] Backend `ALLOWED_ORIGINS` updated with frontend domain
- [ ] Both services deployed successfully
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Frontend loads in browser
- [ ] User registration works
- [ ] User login works

## 📋 Required Environment Variables

### Backend (Critical)

```bash
# Security - REQUIRED
SECRET_KEY=your-32-byte-random-key-here

# Database - Automatic
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Environment
ENVIRONMENT=production

# CORS - Update after frontend deploys
ALLOWED_ORIGINS=https://your-frontend-domain.railway.app
```

### Frontend (Critical)

```bash
# Backend URL - Update after backend deploys
VITE_API_URL=https://your-backend-domain.railway.app

# Environment
NODE_ENV=production
```

## 🔍 Verify Deployment

```bash
# Check backend health
curl https://your-backend.railway.app/health

# Expected response:
# {"status":"healthy","service":"yogaflow-api","version":"1.0.0"}

# Check frontend
curl https://your-frontend.railway.app

# Expected: HTML page

# Run full verification
./infrastructure/scripts/verify_deployment.sh \
  https://your-backend.railway.app \
  https://your-frontend.railway.app
```

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
railway logs

# Common issues:
# 1. Missing SECRET_KEY → Set: railway variables set SECRET_KEY=$(openssl rand -hex 32)
# 2. Database connection → Verify: railway variables | grep DATABASE_URL
# 3. Port binding → Dockerfile uses $PORT (already configured)
```

### Frontend Can't Connect to Backend

```bash
# 1. Update backend CORS
railway variables set -s backend ALLOWED_ORIGINS=https://your-frontend.railway.app

# 2. Update frontend API URL
railway variables set -s frontend VITE_API_URL=https://your-backend.railway.app

# 3. Redeploy both
railway up --detach
```

### Database Migration Failed

```bash
# Check migration logs
railway logs | grep alembic

# Run migrations manually
railway run alembic upgrade head

# Verify tables exist
railway connect postgres
\dt
```

### CORS Errors in Browser

**Symptom:** Console shows CORS policy errors

**Fix:**
```bash
# Backend must allow frontend domain
railway variables set -s backend ALLOWED_ORIGINS=https://frontend-production-xyz.railway.app

# Redeploy backend
cd backend && railway up
```

## 📚 Full Documentation

- **Detailed Guide:** [infrastructure/RAILWAY_DEPLOYMENT.md](infrastructure/RAILWAY_DEPLOYMENT.md)
- **Database Migration:** [infrastructure/DATABASE_MIGRATION.md](infrastructure/DATABASE_MIGRATION.md)
- **Config Reference:** [RAILWAY.md](RAILWAY.md)

## 💡 Tips

1. **Generate Strong Secret Key**
   ```bash
   openssl rand -hex 32
   ```

2. **Monitor Deployments**
   - Railway dashboard shows logs, metrics, deployments
   - Check health: `curl https://your-backend.railway.app/health`

3. **Cost Optimization**
   - Free tier: $5/month credit
   - Production: ~$10-20/month
   - Monitor usage in Railway dashboard

4. **Database Backups**
   - Railway auto-backs up PostgreSQL
   - Manual backup: `railway db dump > backup.sql`

5. **Custom Domain** (Optional)
   - Add in Railway → Settings → Domains
   - Update DNS with CNAME record

## 🆘 Need Help?

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **YogaFlow Issues:** https://github.com/justincavery/yoga-app/issues

## 📊 Post-Deployment

After successful deployment:

1. **Test Complete User Flow**
   - Register account
   - Login
   - Browse poses
   - Start practice session
   - View dashboard

2. **Import Pose Data** (if needed)
   ```bash
   # If poses are empty
   railway run python scripts/import_poses.py
   ```

3. **Set Up Monitoring** (Optional)
   - Create Sentry account: https://sentry.io
   - Add to backend: `railway variables set SENTRY_DSN=your-dsn`

4. **Share Your App**
   - Frontend: https://your-frontend.railway.app
   - Backend API: https://your-backend.railway.app
   - API Docs: https://your-backend.railway.app/docs

---

**Configuration Status:** ✅ Ready for deployment
**Estimated Setup Time:** 5-10 minutes
**Last Updated:** December 6, 2025
