#!/bin/bash
#
# SSL Certificate Setup Script
# Sets up Let's Encrypt SSL certificates for YogaFlow
#
# Usage:
#   sudo ./ssl-setup.sh yourdomain.com
#

set -euo pipefail

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Check if domain is provided
if [ -z "${1:-}" ]; then
    log_error "Usage: $0 yourdomain.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@${DOMAIN}}

log_info "Setting up SSL certificate for $DOMAIN"

# Create self-signed certificate first (for initial setup)
log_info "Creating temporary self-signed certificate..."
mkdir -p /opt/yogaflow/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /opt/yogaflow/ssl/nginx-selfsigned.key \
    -out /opt/yogaflow/ssl/nginx-selfsigned.crt \
    -subj "/C=DE/ST=Hessen/L=Falkenstein/O=YogaFlow/CN=$DOMAIN"

log_info "Self-signed certificate created"

# Update Nginx configuration with the domain
log_info "Updating Nginx configuration with domain..."
sed -i "s/server_name _;/server_name $DOMAIN;/g" /opt/yogaflow/infrastructure/hetzner/nginx/conf.d/yogaflow.conf

# Restart Nginx to apply changes
log_info "Restarting Nginx..."
cd /opt/yogaflow
docker compose -f docker-compose.prod.yml restart nginx

# Wait for Nginx to start
sleep 5

# Obtain Let's Encrypt certificate
log_info "Obtaining Let's Encrypt certificate..."
certbot certonly --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal

if [ $? -eq 0 ]; then
    log_info "Let's Encrypt certificate obtained successfully!"

    # Update Nginx to use Let's Encrypt certificate
    log_info "Updating Nginx to use Let's Encrypt certificate..."
    sed -i "s|ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;|ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;|g" \
        /opt/yogaflow/infrastructure/hetzner/nginx/conf.d/yogaflow.conf
    sed -i "s|ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;|ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;|g" \
        /opt/yogaflow/infrastructure/hetzner/nginx/conf.d/yogaflow.conf

    # Uncomment the Let's Encrypt lines
    sed -i "s|# ssl_certificate /etc/letsencrypt|ssl_certificate /etc/letsencrypt|g" \
        /opt/yogaflow/infrastructure/hetzner/nginx/conf.d/yogaflow.conf

    # Restart Nginx with new certificate
    cd /opt/yogaflow
    docker compose -f docker-compose.prod.yml restart nginx

    log_info "SSL setup completed successfully!"
    log_info "Your site is now accessible at https://$DOMAIN"

    # Set up auto-renewal
    log_info "Setting up auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet && docker exec yogaflow-nginx nginx -s reload") | crontab -

    log_info "Auto-renewal configured (runs twice daily)"
else
    log_error "Failed to obtain Let's Encrypt certificate"
    log_warn "Please ensure:"
    echo "  1. Domain $DOMAIN points to this server IP: $(curl -s ifconfig.me)"
    echo "  2. Ports 80 and 443 are open in firewall"
    echo "  3. DNS propagation is complete (may take up to 48 hours)"
    echo ""
    log_warn "The site will use self-signed certificate for now"
    exit 1
fi
