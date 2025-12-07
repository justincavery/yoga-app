# Hetzner Deployment Guide for YogaFlow

Complete guide for deploying YogaFlow to Hetzner Cloud CPX21 server.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Initial Configuration](#initial-configuration)
4. [GitHub Actions Setup](#github-actions-setup)
5. [First Deployment](#first-deployment)
6. [SSL Certificate Setup](#ssl-certificate-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need

- **Hetzner Account** with CPX21 server created in Falkenstein
- **Domain name** (optional but recommended)
- **GitHub repository** with Actions enabled
- **SSH client** on your local machine

### Server Specifications

**Recommended: CPX21**
- 3 vCPU (AMD EPYC)
- 4GB RAM
- 80GB NVMe SSD
- 20TB traffic/month
- Cost: €9.49-10.59/month

**Location:** Falkenstein, Germany (fsn1)

---

## Server Setup

### Step 1: Create Hetzner Server

1. Log into Hetzner Cloud Console
2. Create new project (if needed): "YogaFlow Production"
3. Click "Add Server"
4. Select:
   - **Location:** Falkenstein (fsn1)
   - **Image:** Ubuntu 24.04 LTS
   - **Type:** CPX21 (Dedicated vCPU)
   - **Volume:** None needed
   - **Network:** Default
   - **SSH Key:** Add your public key (or use password)
   - **Name:** yogaflow-prod

5. Click "Create & Buy Now"
6. Note the server IP address

### Step 2: Initial Server Access

```bash
# SSH into your server (replace with your IP)
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y
```

### Step 3: Run Provisioning Script

```bash
# Clone your repository or copy the provisioning script
cd /tmp
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/yoga-app/main/infrastructure/hetzner/server-provision.sh

# Make executable
chmod +x server-provision.sh

# Run provisioning (this takes 5-10 minutes)
sudo ./server-provision.sh
```

The provisioning script will:
- ✅ Install Docker & Docker Compose
- ✅ Install Nginx & Certbot
- ✅ Configure firewall (UFW)
- ✅ Set up fail2ban for SSH protection
- ✅ Create `deploy` user for deployments
- ✅ Create application directories in `/opt/yogaflow`
- ✅ Set up automatic backups
- ✅ Configure system optimizations

---

## Initial Configuration

### Step 1: Generate SSH Key for GitHub Actions

On your **local machine**:

```bash
# Generate new SSH key pair for deployments
ssh-keygen -t ed25519 -f ~/.ssh/yogaflow-deploy -C "github-actions@yogaflow"

# Display the public key (copy this)
cat ~/.ssh/yogaflow-deploy.pub
```

On the **server**:

```bash
# Add the public key to deploy user
echo "YOUR_PUBLIC_KEY_HERE" >> /home/deploy/.ssh/authorized_keys

# Test SSH connection from local machine
ssh -i ~/.ssh/yogaflow-deploy deploy@YOUR_SERVER_IP
```

### Step 2: Create Environment Configuration

On the **server**:

```bash
# Navigate to application directory
cd /opt/yogaflow

# Copy template and edit
cp .env.template .env
nano .env
```

Configure your `.env` file:

```bash
# Application
ENVIRONMENT=production
SECRET_KEY=YOUR_SUPER_SECRET_KEY_HERE_CHANGE_THIS
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://yogaflow:YOUR_DB_PASSWORD@postgres:5432/yogaflow
POSTGRES_USER=yogaflow
POSTGRES_PASSWORD=YOUR_DB_PASSWORD_CHANGE_THIS
POSTGRES_DB=yogaflow

# CORS - Update with your actual domain
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend API URL
VITE_API_URL=https://yourdomain.com

# Email (optional)
EMAIL_ENABLED=false
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=noreply@yourdomain.com
# SMTP_PASSWORD=your_smtp_password

# Monitoring (optional)
# SENTRY_DSN=https://your-sentry-dsn
```

**Generate secure secrets:**

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate database password
openssl rand -base64 32
```

### Step 3: Set File Permissions

```bash
# Set proper ownership
chown -R deploy:deploy /opt/yogaflow
chmod 600 /opt/yogaflow/.env

# Make scripts executable
chmod +x /opt/yogaflow/backup.sh
```

---

## GitHub Actions Setup

### Step 1: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `HETZNER_SERVER_IP` | Your server IP | Hetzner server IP address |
| `HETZNER_SSH_PRIVATE_KEY` | Private key content | Content of `~/.ssh/yogaflow-deploy` |
| `VITE_API_URL` | `https://yourdomain.com` | Frontend API URL |

**To get private key content:**

```bash
cat ~/.ssh/yogaflow-deploy
```

Copy the entire output including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`

### Step 2: Create Production Environment

In GitHub repository:

1. Go to Settings → Environments
2. Click "New environment"
3. Name: `production`
4. Add protection rules (optional):
   - ✅ Required reviewers
   - ✅ Wait timer
   - ✅ Deployment branches: `main` only

### Step 3: Enable GitHub Actions

1. Go to Settings → Actions → General
2. Under "Actions permissions", select:
   - ✅ Allow all actions and reusable workflows
3. Under "Workflow permissions", select:
   - ✅ Read and write permissions
4. Save changes

---

## First Deployment

### Option 1: Deploy via GitHub Actions (Recommended)

```bash
# On your local machine
git add .
git commit -m "Configure Hetzner deployment"
git push origin main

# Watch deployment in GitHub Actions tab
```

The deployment will:
1. ✅ Run all tests
2. ✅ Build frontend
3. ✅ Deploy to Hetzner
4. ✅ Verify health checks

### Option 2: Manual Deployment

On the **server**:

```bash
# Navigate to app directory
cd /opt/yogaflow

# Clone your repository (first time)
git clone https://github.com/YOUR_USERNAME/yoga-app.git .

# Or pull latest changes
git pull origin main

# Deploy with Docker Compose
docker compose -f docker-compose.prod.yml up -d --build

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check services
docker ps

# Check logs
docker logs yogaflow-backend
docker logs yogaflow-postgres
docker logs yogaflow-nginx
```

---

## SSL Certificate Setup

### Prerequisites

1. **Domain DNS configured:**
   - A record: `yourdomain.com` → Your server IP
   - A record: `www.yourdomain.com` → Your server IP

2. **Verify DNS propagation:**
   ```bash
   dig yourdomain.com
   nslookup yourdomain.com
   ```

### Option 1: Automated SSL Setup

On the **server**:

```bash
cd /opt/yogaflow
chmod +x infrastructure/hetzner/ssl-setup.sh
sudo ./infrastructure/hetzner/ssl-setup.sh yourdomain.com admin@yourdomain.com
```

This script will:
- ✅ Create temporary self-signed certificate
- ✅ Obtain Let's Encrypt certificate
- ✅ Configure Nginx to use SSL
- ✅ Set up auto-renewal (runs twice daily)

### Option 2: Manual SSL Setup

```bash
# Stop containers
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml down

# Create directories
mkdir -p /var/www/certbot

# Get certificate
certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos \
  --no-eff-email

# Update Nginx config
nano infrastructure/hetzner/nginx/conf.d/yogaflow.conf

# Find and uncomment these lines:
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

# Replace yourdomain.com with your actual domain

# Restart containers
docker compose -f docker-compose.prod.yml up -d

# Set up auto-renewal
(crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet && docker exec yogaflow-nginx nginx -s reload") | crontab -
```

### Verify SSL

```bash
# Check certificate
curl -I https://yourdomain.com

# Test SSL configuration
docker exec yogaflow-nginx nginx -t

# Force renewal test
certbot renew --dry-run
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/api/health

# View service status
docker ps

# View logs (last 100 lines)
docker logs --tail 100 yogaflow-backend
docker logs --tail 100 yogaflow-postgres
docker logs --tail 100 yogaflow-nginx
```

### Database Backups

Backups run automatically daily at 2 AM (configured in provisioning script).

**Manual backup:**

```bash
# Run backup manually
/opt/yogaflow/backup.sh

# View backups
ls -lh /opt/yogaflow/backups/

# Restore from backup
gunzip < /opt/yogaflow/backups/postgres_backup_TIMESTAMP.sql.gz | \
  docker exec -i yogaflow-postgres psql -U yogaflow yogaflow
```

### Log Management

```bash
# View logs
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f postgres
docker compose -f docker-compose.prod.yml logs -f nginx

# Clear Docker logs
truncate -s 0 $(docker inspect --format='{{.LogPath}}' yogaflow-backend)
```

### Resource Monitoring

```bash
# System resources
htop

# Docker stats
docker stats

# Disk usage
df -h
docker system df

# Clean up unused Docker resources
docker system prune -a --volumes
```

### Updates

```bash
# Update application code
cd /opt/yogaflow
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## Troubleshooting

### Common Issues

#### 1. Deployment Fails - Connection Refused

**Symptoms:** GitHub Actions can't connect to server

**Solutions:**
```bash
# Check SSH service
systemctl status ssh

# Check firewall
ufw status

# Verify deploy user SSH access
ssh deploy@YOUR_SERVER_IP

# Check SSH key permissions
chmod 600 /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys
```

#### 2. Backend Not Starting

**Symptoms:** Backend container keeps restarting

**Solutions:**
```bash
# Check logs
docker logs yogaflow-backend

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port already in use

# Verify .env file
cat /opt/yogaflow/.env

# Check database
docker logs yogaflow-postgres
docker exec yogaflow-postgres pg_isready -U yogaflow

# Restart services
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml restart
```

#### 3. Database Connection Failed

**Symptoms:** Backend can't connect to PostgreSQL

**Solutions:**
```bash
# Check if postgres is running
docker ps | grep postgres

# Check postgres logs
docker logs yogaflow-postgres

# Verify DATABASE_URL in .env
# Should be: postgresql+asyncpg://yogaflow:PASSWORD@postgres:5432/yogaflow

# Test connection
docker exec yogaflow-postgres psql -U yogaflow -d yogaflow -c "SELECT 1;"

# Restart postgres
docker compose -f docker-compose.prod.yml restart postgres
```

#### 4. Nginx 502 Bad Gateway

**Symptoms:** Website shows 502 error

**Solutions:**
```bash
# Check if backend is running
docker ps | grep backend

# Check backend health
docker exec yogaflow-backend curl -f http://localhost:8000/health

# Check nginx logs
docker logs yogaflow-nginx

# Test nginx config
docker exec yogaflow-nginx nginx -t

# Restart nginx
docker compose -f docker-compose.prod.yml restart nginx
```

#### 5. SSL Certificate Issues

**Symptoms:** HTTPS not working or certificate errors

**Solutions:**
```bash
# Check certificate expiry
certbot certificates

# Renew certificate
certbot renew --force-renewal

# Verify nginx SSL config
docker exec yogaflow-nginx cat /etc/nginx/conf.d/yogaflow.conf | grep ssl_certificate

# Check certificate files exist
ls -l /etc/letsencrypt/live/yourdomain.com/

# Restart nginx
docker compose -f docker-compose.prod.yml restart nginx
```

#### 6. Out of Disk Space

**Symptoms:** Deployment fails, database errors

**Solutions:**
```bash
# Check disk usage
df -h

# Clean Docker resources
docker system prune -a --volumes

# Remove old backups
find /opt/yogaflow/backups -name "*.sql.gz" -mtime +14 -delete

# Clean apt cache
apt-get clean
apt-get autoclean
```

### Debug Mode

Enable detailed logging temporarily:

```bash
# Edit .env
nano /opt/yogaflow/.env

# Change:
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
docker compose -f docker-compose.prod.yml restart backend

# View detailed logs
docker logs -f yogaflow-backend

# Remember to disable debug mode in production!
```

### Emergency Rollback

```bash
# Stop all services
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml down

# Restore from backup
gunzip < /opt/yogaflow/backups/postgres_backup_LATEST.sql.gz | \
  docker exec -i yogaflow-postgres psql -U yogaflow yogaflow

# Checkout previous working commit
git log --oneline
git checkout PREVIOUS_COMMIT_HASH

# Redeploy
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Cost Optimization

### Current Monthly Costs

| Service | Cost |
|---------|------|
| Hetzner CPX21 | €10/month |
| **Total** | **€10/month** |

### Tips to Reduce Costs

1. **Use CX33 instead** (if in EU): €6/month (shared vCPU)
2. **Disable unused services** in Docker Compose
3. **Optimize images:** Regular cleanup with `docker system prune`
4. **Monitor traffic:** 20TB should be plenty

---

## Security Checklist

- ✅ Firewall enabled (UFW)
- ✅ SSH key-only authentication
- ✅ Fail2ban protecting SSH
- ✅ Non-root deploy user
- ✅ SSL/TLS certificates
- ✅ Strong database passwords
- ✅ SECRET_KEY rotated
- ✅ Regular security updates
- ✅ Docker containers running as non-root
- ✅ Environment variables not committed to git

---

## Quick Reference

### Common Commands

```bash
# SSH into server
ssh deploy@YOUR_SERVER_IP

# View logs
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml logs -f

# Restart services
docker compose -f docker-compose.prod.yml restart

# Update and redeploy
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build

# Backup database
/opt/yogaflow/backup.sh

# Check service health
curl http://localhost:8000/health
docker ps
docker stats

# Clean up Docker
docker system prune -a
```

### Important Files

- `/opt/yogaflow/.env` - Environment configuration
- `/opt/yogaflow/docker-compose.prod.yml` - Docker Compose config
- `/opt/yogaflow/infrastructure/hetzner/nginx/` - Nginx configuration
- `/opt/yogaflow/backups/` - Database backups
- `/opt/yogaflow/logs/` - Application logs

### Support Resources

- Hetzner Cloud Docs: https://docs.hetzner.com/cloud/
- Docker Compose Docs: https://docs.docker.com/compose/
- Nginx Docs: https://nginx.org/en/docs/
- Let's Encrypt Docs: https://letsencrypt.org/docs/

---

## Success Checklist

After deployment, verify:

- ✅ Frontend accessible at `https://yourdomain.com`
- ✅ Backend API at `https://yourdomain.com/api/health`
- ✅ API docs at `https://yourdomain.com/docs`
- ✅ SSL certificate valid
- ✅ All Docker containers running
- ✅ Database backups configured
- ✅ GitHub Actions deployment working
- ✅ Monitoring and logs accessible

---

**Congratulations! Your YogaFlow app is now deployed on Hetzner! 🎉**

For support or issues, refer to the troubleshooting section above.
