#!/bin/bash
#
# Emergency Container Startup Script
# Run this on the Hetzner server to manually start containers
#
# Usage: ./emergency-start.sh
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "YogaFlow Emergency Container Startup"
echo "====================================="
echo ""

# Navigate to application directory
cd /opt/yogaflow || {
    log_error "Cannot find /opt/yogaflow directory"
    exit 1
}

log_info "Current directory: $(pwd)"
echo ""

# Check if docker-compose file exists
if [[ ! -f docker-compose.prod.yml ]]; then
    log_error "docker-compose.prod.yml not found!"
    log_error "Files in current directory:"
    ls -la
    exit 1
fi

log_info "Found docker-compose.prod.yml"
echo ""

# Check current container status
log_info "Current container status:"
docker ps -a || log_warn "Failed to list containers"
echo ""

# Check if .env file exists
if [[ ! -f .env ]]; then
    log_error ".env file not found!"
    log_warn "Creating .env from template..."

    if [[ -f .env.template ]]; then
        cp .env.template .env
        log_warn "IMPORTANT: Edit /opt/yogaflow/.env and set:"
        log_warn "  - SECRET_KEY"
        log_warn "  - POSTGRES_PASSWORD"
        log_warn "  - DATABASE_URL"
        log_warn "  - ALLOWED_ORIGINS"
        exit 1
    else
        log_error ".env.template also not found!"
        exit 1
    fi
fi

log_info ".env file exists"
echo ""

# Generate SSL certificates if they don't exist
if [[ ! -f /opt/yogaflow/ssl/nginx-selfsigned.crt ]]; then
    log_info "Generating SSL certificates..."
    mkdir -p /opt/yogaflow/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /opt/yogaflow/ssl/nginx-selfsigned.key \
        -out /opt/yogaflow/ssl/nginx-selfsigned.crt \
        -subj "/C=DE/ST=Hessen/L=Falkenstein/O=YogaFlow/OU=IT/CN=yogaflow.local"
    chmod 644 /opt/yogaflow/ssl/nginx-selfsigned.crt
    chmod 600 /opt/yogaflow/ssl/nginx-selfsigned.key
    log_info "✓ SSL certificates generated"
else
    log_info "✓ SSL certificates already exist"
fi

log_info "SSL certificates:"
ls -lh /opt/yogaflow/ssl/
echo ""

# Stop any existing containers
log_info "Stopping existing containers..."
docker compose -f docker-compose.prod.yml down || log_warn "No containers to stop"
echo ""

# Pull latest images
log_info "Pulling latest images..."
docker compose -f docker-compose.prod.yml pull
echo ""

# Start containers
log_info "Starting containers..."
docker compose -f docker-compose.prod.yml up -d --build --remove-orphans
echo ""

# Wait for services
log_info "Waiting for services to start..."
sleep 10
echo ""

# Check container status
log_info "Container status:"
docker ps
echo ""

# Check PostgreSQL
log_info "Checking PostgreSQL..."
if docker exec yogaflow-postgres pg_isready -U yogaflow 2>/dev/null; then
    log_info "✓ PostgreSQL is ready"
else
    log_warn "PostgreSQL not ready yet, waiting..."
    sleep 5
    if docker exec yogaflow-postgres pg_isready -U yogaflow 2>/dev/null; then
        log_info "✓ PostgreSQL is ready"
    else
        log_error "PostgreSQL failed to start"
    fi
fi
echo ""

# Check backend health
log_info "Checking backend..."
for i in {1..30}; do
    if docker exec yogaflow-backend curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
        log_info "✓ Backend is healthy!"
        break
    fi
    if [[ $i -eq 30 ]]; then
        log_error "Backend health check failed after 30 attempts"
        log_error "Backend logs:"
        docker logs yogaflow-backend --tail 50
    else
        echo -n "."
        sleep 2
    fi
done
echo ""

# Check nginx
log_info "Checking Nginx..."
if docker ps | grep -q yogaflow-nginx; then
    log_info "✓ Nginx is running"

    # Check nginx configuration
    if docker exec yogaflow-nginx nginx -t 2>&1 | grep -q "successful"; then
        log_info "✓ Nginx configuration is valid"
    else
        log_error "Nginx configuration test failed:"
        docker exec yogaflow-nginx nginx -t
    fi
else
    log_error "Nginx container is not running"
    log_error "Nginx logs:"
    docker logs yogaflow-nginx --tail 50
fi
echo ""

# Test local connectivity
log_info "Testing local connectivity..."
if curl -f -s http://localhost/health >/dev/null 2>&1; then
    log_info "✓ HTTP (port 80) is accessible"
else
    log_warn "HTTP (port 80) is not responding"
fi

if curl -f -s -k https://localhost/health >/dev/null 2>&1; then
    log_info "✓ HTTPS (port 443) is accessible"
else
    log_warn "HTTPS (port 443) is not responding"
fi
echo ""

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me)
log_info "External IP: $EXTERNAL_IP"
echo ""

# Final status
log_info "====================================="
log_info "Startup Summary"
log_info "====================================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

log_info "Next steps:"
echo "1. Test from external: curl http://$EXTERNAL_IP/health"
echo "2. Check logs: docker logs yogaflow-backend -f"
echo "3. If issues persist, check: docker logs yogaflow-nginx"
echo ""
