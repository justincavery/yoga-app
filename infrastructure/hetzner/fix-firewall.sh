#!/bin/bash
#
# Firewall Fix Script for YogaFlow Deployment
# Run this on your Hetzner server as root to open ports 80/443
#
# Usage: sudo ./fix-firewall.sh
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
   exit 1
fi

log_info "Starting firewall configuration..."
echo ""

# 1. Configure UFW firewall
log_info "Configuring UFW firewall rules..."
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

log_info "UFW firewall configured"
echo ""

# 2. Verify UFW status
log_info "Current UFW status:"
ufw status verbose
echo ""

# 3. Check iptables for any blocking rules
log_info "Checking iptables for conflicting rules..."
DOCKER_FORWARD=$(iptables -L DOCKER-USER -n 2>/dev/null | grep -E 'dpt:80|dpt:443' || echo "")
if [[ -n "$DOCKER_FORWARD" ]]; then
    log_warn "Found Docker firewall rules that might interfere"
fi
echo ""

# 4. Restart Docker to ensure network rules are correct
log_info "Restarting Docker to refresh network configuration..."
systemctl restart docker
sleep 3
log_info "Docker restarted"
echo ""

# 5. Restart containers
log_info "Restarting YogaFlow containers..."
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
echo ""

# 6. Wait for services to be ready
log_info "Waiting for services to be healthy..."
sleep 10

# Check backend health
for i in {1..30}; do
  if docker exec yogaflow-backend curl -f -s -o /dev/null http://localhost:8000/health; then
    log_info "✓ Backend is healthy!"
    break
  fi
  echo "Waiting for backend... ($i/30)"
  sleep 2
done
echo ""

# 7. Test local connectivity
log_info "Testing local connectivity..."
echo -n "HTTP (port 80): "
if curl -f -s -o /dev/null http://localhost; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo -n "HTTPS (port 443): "
if curl -f -s -o /dev/null -k https://localhost; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi
echo ""

# 8. Display external IP and test instructions
EXTERNAL_IP=$(curl -s ifconfig.me)
log_info "================================================"
log_info "Firewall configuration complete!"
log_info "================================================"
echo ""
log_info "Server external IP: $EXTERNAL_IP"
echo ""
log_info "Test external connectivity with:"
echo "  curl http://$EXTERNAL_IP/health"
echo "  curl -k https://$EXTERNAL_IP/health"
echo ""
log_info "If external access still fails, check:"
echo "  1. Hetzner Cloud Firewall in the web console"
echo "  2. Your network/ISP firewall"
echo "  3. Run ./diagnose-network.sh for detailed diagnostics"
echo ""
log_warn "IMPORTANT: If you have a domain configured, also check:"
echo "  - DNS records are pointing to $EXTERNAL_IP"
echo "  - SSL certificates are properly configured"
echo ""
log_info "Next steps:"
echo "  - Test from your local machine: curl http://$EXTERNAL_IP/health"
echo "  - Set up SSL if you have a domain"
echo "  - Update GitHub secrets with correct VITE_API_URL"
echo ""
