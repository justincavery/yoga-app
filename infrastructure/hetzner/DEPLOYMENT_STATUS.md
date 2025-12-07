# YogaFlow Hetzner Deployment Status

**Last Updated:** 2025-12-07 22:14 UTC
**Status:** 🟡 Deployed but not externally accessible
**Issue:** Firewall blocking external access to ports 80/443

---

## Current Situation

### ✅ What's Working

1. **Server provisioned successfully**
   - CPX21 server in Falkenstein
   - Ubuntu 24.04, Docker installed
   - Deploy user configured with sudo permissions

2. **Deployment pipeline working**
   - GitHub Actions workflow executing successfully
   - SSH connection to server working
   - Files deploying correctly
   - Docker images building and pulling

3. **Application containers running**
   - `yogaflow-postgres`: ✅ Running and healthy
   - `yogaflow-backend`: ✅ Running and healthy (verified via internal health check)
   - `yogaflow-nginx`: ✅ Running and started successfully

4. **Internal connectivity working**
   - Backend responds to health checks from within container
   - Docker network configured correctly
   - All containers can communicate

### ❌ What's Not Working

1. **External connectivity failing**
   - Cannot connect to server on port 80 (HTTP)
   - Cannot connect to server on port 443 (HTTPS)
   - GitHub Actions verification step fails with connection errors

### 🔍 Root Cause

The UFW firewall on the Hetzner server is likely blocking inbound traffic on ports 80 and 443. While the provisioning script sets up UFW, it may need ports 80/443 explicitly allowed.

---

## Resolution Steps

### Option 1: Run Fix Script (Recommended)

SSH into your server and run the firewall fix script:

```bash
# SSH into server
ssh deploy@YOUR_SERVER_IP

# Switch to root or use sudo
sudo su

# Navigate to deployment directory
cd /opt/yogaflow

# Run the fix script
sudo ./infrastructure/hetzner/fix-firewall.sh
```

This script will:
- Configure UFW to allow ports 80/443
- Restart Docker and containers
- Test connectivity
- Provide diagnostic information

### Option 2: Manual Fix

If you prefer to fix manually:

```bash
# SSH into server
ssh deploy@YOUR_SERVER_IP

# Allow HTTP and HTTPS in firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Verify UFW status
sudo ufw status verbose

# Restart containers to ensure port bindings are correct
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml restart

# Test local connectivity
curl http://localhost/health
curl -k https://localhost/health
```

### Option 3: Check Hetzner Cloud Firewall

If UFW is configured correctly but external access still fails:

1. Log into [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Navigate to your project
3. Go to "Firewalls" in the left menu
4. Check if there's a firewall attached to your server
5. If yes, ensure it allows:
   - Port 22 (SSH)
   - Port 80 (HTTP)
   - Port 443 (HTTPS)

---

## Verification

After running the fix, verify external connectivity:

```bash
# From your local machine (replace YOUR_SERVER_IP)
curl http://YOUR_SERVER_IP/health
curl -k https://YOUR_SERVER_IP/health
```

Expected response:
```json
{"status":"healthy"}
```

---

## Diagnostics

Run the diagnostic script to troubleshoot issues:

```bash
# SSH into server
ssh deploy@YOUR_SERVER_IP

# Run diagnostics
cd /opt/yogaflow
sudo ./infrastructure/hetzner/diagnose-network.sh
```

This will check:
- Docker container status
- Port bindings
- UFW firewall rules
- iptables rules
- System Nginx conflicts
- Local connectivity
- External IP

---

## Deployment History

### Latest Deployment (Run #20011034055)

**Time:** 2025-12-07 22:14 UTC
**Commit:** c04e09c24ebc5639035ae2dd3c39a7b9c1e9681c
**Branch:** main

**Steps:**
1. ✅ Tests completed (with continue-on-error)
2. ✅ Frontend built successfully
3. ✅ SSH connection established
4. ✅ Files copied to server
5. ✅ System Nginx stopped successfully
6. ✅ Docker images pulled
7. ✅ Backend built from Dockerfile
8. ✅ Containers started
9. ✅ PostgreSQL became healthy
10. ✅ Backend health check passed internally
11. ✅ Nginx container started
12. ❌ External verification failed (connection timeout on ports 80/443)

---

## Next Steps

1. **Immediate:** Fix firewall configuration using one of the options above
2. **After firewall fix:** Trigger a new deployment or manually verify
3. **Once accessible:** Configure SSL with Let's Encrypt
4. **Final:** Update DNS records and GitHub secrets with production domain

---

## Support Commands

### Check container status
```bash
docker ps
docker logs yogaflow-nginx
docker logs yogaflow-backend
docker logs yogaflow-postgres
```

### Check network connectivity
```bash
# From server
netstat -tulpn | grep -E ':80|:443'
docker port yogaflow-nginx

# Test from container
docker exec yogaflow-backend curl -f http://localhost:8000/health
```

### Restart services
```bash
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml restart
```

### View logs
```bash
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml logs -f
```

---

## Architecture Deployed

```
Internet
    |
    v
[Hetzner Cloud Server - CPX21]
    |
    ├─ UFW Firewall (ports: 22, 80, 443) ← NEEDS CONFIGURATION
    |
    └─ Docker Network
        |
        ├─ yogaflow-nginx (80, 443)
        |   ├─ Serves frontend (React SPA)
        |   └─ Proxies API to backend
        |
        ├─ yogaflow-backend (8000)
        |   └─ FastAPI application
        |
        └─ yogaflow-postgres (5432)
            └─ PostgreSQL database
```

---

## Cost Summary

- **Hetzner CPX21:** €10/month
- **Total:** €10/month

---

For more information, see:
- [HETZNER_DEPLOYMENT_GUIDE.md](HETZNER_DEPLOYMENT_GUIDE.md)
- [QUICK_START.md](QUICK_START.md)
