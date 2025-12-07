# IMMEDIATE FIX - No Containers Running

## Quick Diagnosis and Fix

SSH into your server and run these commands:

```bash
# 1. Check what's happening
ssh deploy@YOUR_SERVER_IP
cd /opt/yogaflow

# 2. Check if files exist
ls -la

# 3. Check docker compose file
cat docker-compose.prod.yml

# 4. Check if .env exists
ls -la .env

# 5. Run emergency startup script
./infrastructure/hetzner/emergency-start.sh
```

## Manual Fix (if emergency script doesn't work)

### Step 1: Check Environment File

```bash
cd /opt/yogaflow

# Check if .env exists
if [[ ! -f .env ]]; then
  echo "Creating .env file..."
  cat > .env <<'EOF'
ENVIRONMENT=production
SECRET_KEY=CHANGE_THIS_SECRET_KEY_12345678901234567890123456789012
DEBUG=false

DATABASE_URL=postgresql+asyncpg://yogaflow:yogaflow123@postgres:5432/yogaflow
POSTGRES_USER=yogaflow
POSTGRES_PASSWORD=yogaflow123
POSTGRES_DB=yogaflow

ALLOWED_ORIGINS=*

EMAIL_ENABLED=false
LOG_LEVEL=INFO
EOF

  echo "⚠️  IMPORTANT: This uses default passwords. Change them later!"
fi
```

### Step 2: Generate SSL Certificates

```bash
# Create SSL directory and generate certs
mkdir -p /opt/yogaflow/ssl
cd /opt/yogaflow/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx-selfsigned.key \
  -out nginx-selfsigned.crt \
  -subj "/C=DE/ST=Hessen/L=Falkenstein/O=YogaFlow/OU=IT/CN=yogaflow.local"

chmod 644 nginx-selfsigned.crt
chmod 600 nginx-selfsigned.key

# Verify
ls -lh /opt/yogaflow/ssl/
```

### Step 3: Start Containers

```bash
cd /opt/yogaflow

# Stop any existing containers
docker compose -f docker-compose.prod.yml down

# Start containers
docker compose -f docker-compose.prod.yml up -d --build

# Watch logs
docker compose -f docker-compose.prod.yml logs -f
```

### Step 4: Verify

```bash
# Check containers
docker ps

# Check backend health (wait 30 seconds first)
sleep 30
docker exec yogaflow-backend curl -f http://localhost:8000/health

# Check from localhost
curl http://localhost/health
curl -k https://localhost/health

# Get your external IP
curl ifconfig.me
```

## Common Issues and Fixes

### Issue: "docker-compose.prod.yml not found"

The deployment hasn't run yet or failed. Pull code manually:

```bash
cd /opt/yogaflow
git pull origin main
```

### Issue: ".env file missing"

See Step 1 above to create it.

### Issue: "SSL certificates not found"

See Step 2 above to create them.

### Issue: "Backend not healthy"

Check logs:
```bash
docker logs yogaflow-backend
docker logs yogaflow-postgres
```

Common causes:
- Database not ready (wait longer)
- Wrong DATABASE_URL in .env
- Port conflicts

### Issue: "Nginx won't start"

Check logs:
```bash
docker logs yogaflow-nginx
```

Common causes:
- SSL certificate files missing
- Backend not running
- Ports 80/443 in use

Fix port conflicts:
```bash
# Check what's using ports
sudo netstat -tulpn | grep -E ':80|:443'

# Stop system nginx if running
sudo systemctl stop nginx
sudo systemctl disable nginx
```

## One-Line Nuclear Option

If nothing works, this will reset everything:

```bash
cd /opt/yogaflow && \
docker compose -f docker-compose.prod.yml down -v && \
rm -rf ssl && \
mkdir -p ssl && \
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/nginx-selfsigned.key -out ssl/nginx-selfsigned.crt -subj "/C=DE/ST=Hessen/L=Falkenstein/O=YogaFlow/OU=IT/CN=yogaflow.local" && \
docker compose -f docker-compose.prod.yml up -d --build --remove-orphans && \
sleep 20 && \
docker ps
```

## Get Help

After running any of the above, send me the output of:

```bash
docker ps -a
docker logs yogaflow-nginx --tail 50
docker logs yogaflow-backend --tail 50
ls -la /opt/yogaflow/
ls -la /opt/yogaflow/ssl/
```

This will help diagnose what's still wrong.
