#!/bin/bash
#
# Network Diagnostics Script for YogaFlow Deployment
# Run this on the Hetzner server to diagnose connectivity issues
#
# Usage: sudo ./diagnose-network.sh
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}YogaFlow Network Diagnostics${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}ERROR: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# 1. Check Docker containers
echo -e "${YELLOW}[1/8] Checking Docker containers...${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 2. Check if containers are listening on ports
echo -e "${YELLOW}[2/8] Checking container port bindings...${NC}"
docker port yogaflow-nginx 2>/dev/null || echo -e "${RED}Nginx container not found or not running${NC}"
echo ""

# 3. Check if ports are open on host
echo -e "${YELLOW}[3/8] Checking host port bindings...${NC}"
netstat -tulpn | grep -E ':80|:443' || echo -e "${RED}No processes listening on ports 80/443${NC}"
echo ""

# 4. Check UFW firewall status
echo -e "${YELLOW}[4/8] Checking UFW firewall...${NC}"
ufw status verbose
echo ""

# 5. Check if system Nginx is still running
echo -e "${YELLOW}[5/8] Checking for system Nginx...${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "${RED}⚠ System Nginx is RUNNING - this may conflict with Docker Nginx${NC}"
    systemctl status nginx --no-pager -l
else
    echo -e "${GREEN}✓ System Nginx is not running${NC}"
fi
echo ""

# 6. Check iptables rules
echo -e "${YELLOW}[6/8] Checking iptables rules...${NC}"
iptables -L -n -v | grep -E 'dpt:80|dpt:443' || echo "No specific rules for ports 80/443"
echo ""

# 7. Test local connectivity
echo -e "${YELLOW}[7/8] Testing local connectivity...${NC}"
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

echo -n "Backend (port 8000): "
if docker exec yogaflow-backend curl -f -s -o /dev/null http://localhost:8000/health; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi
echo ""

# 8. Check server external IP
echo -e "${YELLOW}[8/8] Server external connectivity...${NC}"
EXTERNAL_IP=$(curl -s ifconfig.me)
echo "External IP: $EXTERNAL_IP"
echo ""

# Summary and recommendations
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Summary and Recommendations${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if UFW is blocking ports
UFW_STATUS=$(ufw status | grep -E '^80/tcp|^443/tcp' || echo "")
if [[ -z "$UFW_STATUS" ]]; then
    echo -e "${RED}⚠ UFW may be blocking ports 80/443${NC}"
    echo -e "${YELLOW}Run: sudo ufw allow 80/tcp && sudo ufw allow 443/tcp${NC}"
    echo ""
fi

# Check if Docker containers are bound to correct ports
NGINX_RUNNING=$(docker ps | grep yogaflow-nginx || echo "")
if [[ -z "$NGINX_RUNNING" ]]; then
    echo -e "${RED}⚠ Nginx container is not running${NC}"
    echo -e "${YELLOW}Run: cd /opt/yogaflow && docker compose -f docker-compose.prod.yml up -d${NC}"
    echo ""
fi

# Check if Hetzner Cloud Firewall might be blocking
echo -e "${YELLOW}Note: If UFW is configured correctly but external access still fails,${NC}"
echo -e "${YELLOW}check the Hetzner Cloud Firewall in the Hetzner Cloud Console:${NC}"
echo -e "${YELLOW}https://console.hetzner.cloud/ → Your Project → Firewalls${NC}"
echo ""

echo -e "${GREEN}Diagnostics complete!${NC}"
