# Railway Deployment Guide - YogaFlow

Deploy the entire YogaFlow application to Railway in under 10 minutes.

## Why Railway?

- ✅ **Docker Support** - Uses your existing docker-compose setup
- ✅ **Built-in PostgreSQL** - Managed database with automatic backups
- ✅ **Free Tier** - $5 free credits monthly, then pay-as-you-go
- ✅ **Auto-Deploy** - Deploy from GitHub automatically
- ✅ **Environment Variables** - Easy configuration management
- ✅ **HTTPS** - Automatic SSL certificates
- ✅ **Fast** - Global CDN and edge network

## Prerequisites

1. GitHub account
2. Railway account (sign up at https://railway.app with GitHub)
3. Project pushed to GitHub

## Step 1: Prepare Your Repository

### 1.1 Create `.gitignore` (if not exists)

```bash
cat > .gitignore << 'EOF'
# Environment files
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Node
node_modules/
.npm
.eslintcache

# Build
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
EOF
```

### 1.2 Push to GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

## Step 2: Deploy to Railway (Method 1 - Easiest)

### 2.1 Create New Project

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your `yoga-app` repository

### 2.2 Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will provision a PostgreSQL instance
4. Note: Railway automatically creates a `DATABASE_URL` environment variable

### 2.3 Configure Backend Service

1. Click on your backend service
2. Go to "Settings" → "Environment Variables"
3. Add these variables:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<generate-a-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://your-frontend-url.railway.app
ENVIRONMENT=production
SENTRY_DSN=<optional-sentry-dsn>
```

4. Go to "Settings" → "Networking"
5. Click "Generate Domain" to get a public URL
6. Note the backend URL (e.g., `https://yoga-backend.railway.app`)

### 2.4 Configure Frontend Service

1. Click "+ New" → "Empty Service"
2. Connect to your GitHub repo (select frontend folder)
3. Go to "Settings" → "Build & Deploy"
4. Set:
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview`
   - **Root Directory**: `frontend`

5. Go to "Settings" → "Environment Variables"
6. Add:

```
VITE_API_URL=https://your-backend-url.railway.app
NODE_ENV=production
```

7. Go to "Settings" → "Networking"
8. Click "Generate Domain"

### 2.5 Run Database Migrations

1. Click on your backend service
2. Go to "Deployments" → Select latest deployment
3. Click "View Logs"
4. Verify migrations ran automatically (or run manually):

```bash
# In Railway backend service
alembic upgrade head
```

## Step 3: Deploy to Railway (Method 2 - Using Railway CLI)

### 3.1 Install Railway CLI

```bash
npm install -g @railway/cli
```

### 3.2 Login to Railway

```bash
railway login
```

### 3.3 Initialize Project

```bash
railway init
```

### 3.4 Add PostgreSQL

```bash
railway add --database postgres
```

### 3.5 Deploy Backend

```bash
cd backend
railway up
```

### 3.6 Deploy Frontend

```bash
cd ../frontend
railway up
```

### 3.7 Link Services

```bash
railway link
```

## Step 4: Create Railway Configuration Files

### 4.1 Create `railway.json` (Backend)

```bash
cat > backend/railway.json << 'EOF'
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
EOF
```

### 4.2 Create `railway.json` (Frontend)

```bash
cat > frontend/railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm install && npm run build",
    "watchPatterns": ["src/**"]
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "npm run preview",
    "restartPolicyType": "ON_FAILURE"
  }
}
EOF
```

## Step 5: Alternative - Deploy with Docker Compose

Railway supports docker-compose for multi-service deployments.

### 5.1 Create `railway.toml`

```bash
cat > railway.toml << 'EOF'
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile.prod"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
numReplicas = 1
restartPolicyType = "ON_FAILURE"
EOF
```

### 5.2 Deploy

```bash
railway up
```

## Step 6: Configure Production Environment

### 6.1 Generate Secret Key

```bash
openssl rand -hex 32
```

Copy the output and set as `SECRET_KEY` in Railway environment variables.

### 6.2 Update CORS Origins

In Railway backend environment variables, update:

```
CORS_ORIGINS=https://your-actual-frontend-domain.railway.app
```

### 6.3 Set Up Sentry (Optional but Recommended)

1. Create account at https://sentry.io
2. Create new project for YogaFlow
3. Copy DSN
4. Add to Railway environment variables:
   ```
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   ```

## Step 7: Verify Deployment

### 7.1 Check Backend Health

```bash
curl https://your-backend-url.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

### 7.2 Check Frontend

Visit `https://your-frontend-url.railway.app` in browser.

### 7.3 Test Complete Flow

1. Register a new account
2. Login
3. Browse poses
4. Start a practice session
5. View dashboard

## Step 8: Post-Deployment Tasks

### 8.1 Set Up Custom Domain (Optional)

1. In Railway frontend service → Settings → Domains
2. Add your custom domain
3. Update DNS with provided CNAME record

### 8.2 Monitor Application

Railway provides built-in monitoring:
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History of all deployments

### 8.3 Set Up Alerts (Optional)

Configure Sentry alerts for:
- Error rates
- Performance issues
- Failed deployments

## Costs

Railway pricing (as of 2025):

**Free Tier:**
- $5 credit per month
- Perfect for testing and small projects
- Enough to run YogaFlow for evaluation

**Usage-Based Pricing:**
- ~$5-15/month for small production apps
- PostgreSQL: ~$5-10/month (depending on usage)
- Backend: ~$5/month (512MB RAM)
- Frontend: ~$1-2/month (static hosting)

**Estimated Total: $10-20/month for production**

## Troubleshooting

### Database Connection Issues

```bash
# Check if DATABASE_URL is set correctly
railway variables

# Test database connection
railway run python -c "import psycopg2; print('Connected!')"
```

### Build Failures

```bash
# View build logs
railway logs

# Rebuild
railway up --detach
```

### Environment Variables Not Loading

```bash
# List all variables
railway variables

# Set a variable
railway variables set KEY=value
```

### Frontend Can't Connect to Backend

1. Verify CORS_ORIGINS includes frontend domain
2. Check VITE_API_URL points to backend domain
3. Ensure both services are running

## Alternative Deployment Options

If Railway doesn't work for you, here are alternatives:

### Option 2: Render (Free Tier Available)
- Similar to Railway
- Free PostgreSQL
- Free web services (with limitations)
- Guide: https://render.com/docs

### Option 3: Fly.io
- Good for global deployment
- Docker-based
- Free tier available
- Guide: https://fly.io/docs

### Option 4: DigitalOcean App Platform
- $5/month minimum
- Managed PostgreSQL ($15/month)
- Very reliable
- Guide: https://www.digitalocean.com/products/app-platform

### Option 5: Vercel (Frontend) + Railway (Backend + DB)
- **Frontend**: Deploy to Vercel (free tier, excellent performance)
- **Backend + Database**: Railway
- Best of both worlds for performance

## Quick Deploy Script

Save this as `deploy-to-railway.sh`:

```bash
#!/bin/bash

echo "🚀 Deploying YogaFlow to Railway..."

# Install Railway CLI if not installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login
echo "🔐 Logging in to Railway..."
railway login

# Link project (or create new)
echo "🔗 Linking to Railway project..."
railway link

# Add PostgreSQL if needed
echo "🗄️  Setting up PostgreSQL..."
railway add --database postgres || echo "Database already exists"

# Deploy backend
echo "🔧 Deploying backend..."
cd backend
railway up
cd ..

# Deploy frontend
echo "🎨 Deploying frontend..."
cd frontend
railway up
cd ..

echo "✅ Deployment complete!"
echo "🌐 Check your Railway dashboard for service URLs"
```

Make it executable and run:

```bash
chmod +x deploy-to-railway.sh
./deploy-to-railway.sh
```

## Next Steps After Deployment

1. **Test Thoroughly** - Go through all user flows
2. **Monitor Errors** - Watch Sentry for any issues
3. **Optimize Performance** - Use Railway metrics to identify bottlenecks
4. **Scale if Needed** - Increase replicas if traffic grows
5. **Set Up Backups** - Railway does automatic backups, but consider additional backup strategy
6. **Add Custom Domain** - Point your domain to Railway
7. **Set Up Analytics** - Add Google Analytics or similar
8. **Create Admin User** - Create first admin account for content management

---

**Your YogaFlow app is now live on Railway!** 🎉

Share your deployment URL and start getting users practicing yoga! 🧘‍♀️
