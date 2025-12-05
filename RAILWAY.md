# Railway Deployment - Config as Code

This project is configured for Railway deployment using infrastructure-as-code.

## 📁 Configuration Files

```
yoga-app/
├── railway.toml              # Root project config
├── railway.json              # Root project config (JSON)
├── backend/
│   └── railway.json          # Backend service config
└── frontend/
    └── railway.json          # Frontend service config
```

## 🚀 Quick Deploy

### Method 1: One-Click Deploy (Recommended)

1. Go to https://railway.app
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select **justincavery/yoga-app**
4. Railway will automatically:
   - Detect `railway.json` in backend/ and frontend/
   - Build using Docker (backend) and Nixpacks (frontend)
   - Deploy both services

### Method 2: Railway CLI

```bash
# Login
railway login

# Link to project (creates new or links existing)
railway link

# Add PostgreSQL database
railway add --database postgres

# Deploy all services
railway up

# Or deploy specific service
cd backend && railway up
cd frontend && railway up
```

## 🔧 Required Environment Variables

Railway will need these environment variables configured through the web UI or CLI:

### Backend Service

```bash
# Automatically set by Railway when you add PostgreSQL
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Generate with: openssl rand -hex 32
SECRET_KEY=<your-secret-key-here>

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Environment
ENVIRONMENT=production

# CORS (set after frontend is deployed)
CORS_ORIGINS=https://your-frontend-url.railway.app

# Optional: Error tracking
SENTRY_DSN=<your-sentry-dsn>
```

### Frontend Service

```bash
# Backend URL (set after backend is deployed)
VITE_API_URL=https://your-backend-url.railway.app

# Environment
NODE_ENV=production
```

## 📝 Setting Environment Variables

### Via Web UI:

1. Click on service (backend or frontend)
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add key-value pairs
5. Railway auto-redeploys

### Via CLI:

```bash
# Set variable for current service
railway variables set SECRET_KEY=your-secret-key

# Set variable for specific service
railway variables set -s backend SECRET_KEY=your-secret-key

# View all variables
railway variables
```

## 🔗 Service References

Railway services can reference each other using `${{ServiceName.VARIABLE}}` syntax:

```bash
# Backend references database
DATABASE_URL=${{Postgres.DATABASE_URL}}

# You can also reference other services
API_URL=${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

## 🏗️ Build Configuration

### Backend (Dockerfile)

- **Builder**: `DOCKERFILE`
- **Dockerfile**: `Dockerfile.prod`
- **Health Check**: `/health` endpoint
- **Port**: Auto-assigned by Railway (via `$PORT`)

### Frontend (Nixpacks)

- **Builder**: `NIXPACKS`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`
- **Watch Patterns**: `src/**` (triggers rebuilds)

## 🔄 Deployment Workflow

1. **Push to GitHub**: `git push origin main`
2. **Railway Auto-Deploy**: Detects changes and triggers build
3. **Build Phase**:
   - Backend builds Docker image
   - Frontend builds with Vite
4. **Deploy Phase**:
   - Runs health checks
   - Switches traffic to new deployment
5. **Live**: Your app is updated!

## 🎯 Production Checklist

- [ ] PostgreSQL database added
- [ ] Backend `SECRET_KEY` generated and set
- [ ] Backend `DATABASE_URL` configured
- [ ] Backend domain generated
- [ ] Frontend `VITE_API_URL` set to backend domain
- [ ] Frontend domain generated
- [ ] Backend `CORS_ORIGINS` set to frontend domain
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Frontend loads and can communicate with backend
- [ ] User registration works
- [ ] User login works
- [ ] Data persists in PostgreSQL

## 📊 Monitoring

Railway provides built-in monitoring:

- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History and rollback
- **Health Checks**: Automatic health monitoring

Access via Railway dashboard for each service.

## 💰 Estimated Costs

**Free Tier**: $5/month credit (good for testing)

**Production (Pay-as-you-go)**:
- Backend: ~$5-7/month (512MB RAM, Docker)
- Frontend: ~$1-2/month (static hosting)
- PostgreSQL: ~$5-10/month (1GB storage)

**Total**: ~$10-20/month

## 🐛 Troubleshooting

### Build fails

```bash
# View build logs
railway logs --build

# Check railway.json syntax
cat backend/railway.json | jq
```

### Deployment fails

```bash
# View deployment logs
railway logs

# Check environment variables
railway variables
```

### Database connection issues

```bash
# Verify DATABASE_URL is set
railway variables | grep DATABASE_URL

# Check database status
railway status
```

### CORS errors

Ensure `CORS_ORIGINS` in backend matches frontend domain exactly:
```bash
railway variables set -s backend CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app
```

## 🔐 Security Notes

- Never commit `.env` files with secrets
- Use Railway's environment variables for all secrets
- `SECRET_KEY` should be cryptographically random (32+ bytes)
- Enable Railway's automatic HTTPS (enabled by default)
- Review Railway's security best practices

## 📚 Resources

- [Railway Docs](https://docs.railway.app)
- [Railway Config Reference](https://docs.railway.app/deploy/config-as-code)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)

---

**Config-as-Code Status**: ✅ Fully configured
**Last Updated**: December 5, 2025
