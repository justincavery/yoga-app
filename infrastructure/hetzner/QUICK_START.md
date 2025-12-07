# Hetzner Deployment - Quick Start (30 Minutes)

Get YogaFlow deployed to Hetzner in 30 minutes.

## Prerequisites

- ✅ Hetzner Cloud account
- ✅ GitHub repository
- ✅ Domain name (optional)

---

## Step 1: Create Server (5 min)

1. Login to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Create server:
   - **Location:** Falkenstein
   - **Image:** Ubuntu 24.04
   - **Type:** CPX21
   - **SSH Key:** Add yours
3. Note the IP address

---

## Step 2: Provision Server (5 min)

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Download and run provisioning script
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/yoga-app/main/infrastructure/hetzner/server-provision.sh
chmod +x server-provision.sh
sudo ./server-provision.sh

# Exit and copy will show you the next steps
```

---

## Step 3: Configure GitHub Actions (5 min)

### Generate SSH key on local machine:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/yogaflow-deploy
cat ~/.ssh/yogaflow-deploy.pub
```

### Add public key to server:

```bash
ssh root@YOUR_SERVER_IP
echo "YOUR_PUBLIC_KEY" >> /home/deploy/.ssh/authorized_keys
exit
```

### Add GitHub Secrets:

Go to GitHub → Settings → Secrets → Add:

1. `HETZNER_SERVER_IP` = Your server IP
2. `HETZNER_SSH_PRIVATE_KEY` = Content of `~/.ssh/yogaflow-deploy`
3. `VITE_API_URL` = `https://yourdomain.com` (or `http://YOUR_IP`)

---

## Step 4: Configure Environment (5 min)

SSH into server as deploy user:

```bash
ssh deploy@YOUR_SERVER_IP
cd /opt/yogaflow
cp .env.template .env
nano .env
```

Update these values:

```bash
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
DATABASE_URL=postgresql+asyncpg://yogaflow:YOUR_POSTGRES_PASSWORD@postgres:5432/yogaflow
ALLOWED_ORIGINS=https://yourdomain.com
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 5: Deploy! (5 min)

On your local machine:

```bash
git add .
git commit -m "Configure Hetzner deployment"
git push origin main
```

Watch deployment in GitHub Actions tab.

---

## Step 6: Setup SSL (Optional, 5 min)

**Only if you have a domain pointed to your server:**

```bash
ssh deploy@YOUR_SERVER_IP
cd /opt/yogaflow
sudo ./infrastructure/hetzner/ssl-setup.sh yourdomain.com
```

---

## Verify Deployment

```bash
# Check services
ssh deploy@YOUR_SERVER_IP
docker ps

# Check health
curl http://YOUR_SERVER_IP/health

# If SSL configured:
curl https://yourdomain.com/health
```

---

## You're Done! 🎉

- **Frontend:** `https://yourdomain.com` (or `http://YOUR_IP`)
- **API Docs:** `https://yourdomain.com/docs`
- **API Health:** `https://yourdomain.com/api/health`

---

## Next Steps

- Set up monitoring
- Configure email (optional)
- Review [Full Guide](HETZNER_DEPLOYMENT_GUIDE.md)

---

## Quick Commands

```bash
# View logs
ssh deploy@YOUR_SERVER_IP
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml logs -f

# Restart
docker compose -f docker-compose.prod.yml restart

# Manual deployment
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Cost: €10/month

That's it! Your app is deployed for less than the cost of a movie ticket per month.
