#!/bin/bash
#
# Generate self-signed SSL certificates for Nginx
# Run this on the Hetzner server before deploying
#
# Usage: sudo ./generate-ssl-certs.sh
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_warn "This script should be run as root (use sudo)"
   exit 1
fi

SSL_DIR="/opt/yogaflow/ssl"
CERT_FILE="$SSL_DIR/nginx-selfsigned.crt"
KEY_FILE="$SSL_DIR/nginx-selfsigned.key"

log_info "Checking for SSL certificates..."

# Create SSL directory if it doesn't exist
if [[ ! -d "$SSL_DIR" ]]; then
    log_info "Creating SSL directory: $SSL_DIR"
    mkdir -p "$SSL_DIR"
    chown -R deploy:deploy "$SSL_DIR"
fi

# Check if certificates already exist
if [[ -f "$CERT_FILE" ]] && [[ -f "$KEY_FILE" ]]; then
    log_info "SSL certificates already exist:"
    echo "  Certificate: $CERT_FILE"
    echo "  Key: $KEY_FILE"
    echo ""

    # Check expiry
    EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
    log_info "Certificate expires: $EXPIRY"
    echo ""

    read -p "Regenerate certificates? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Keeping existing certificates"
        exit 0
    fi
fi

log_info "Generating self-signed SSL certificate..."

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=DE/ST=Hessen/L=Falkenstein/O=YogaFlow/OU=IT/CN=yogaflow.local" \
    2>/dev/null

# Set proper permissions
chmod 644 "$CERT_FILE"
chmod 600 "$KEY_FILE"
chown deploy:deploy "$CERT_FILE" "$KEY_FILE"

log_info "✓ SSL certificates generated successfully!"
echo ""
log_info "Certificate details:"
openssl x509 -in "$CERT_FILE" -text -noout | grep -E "Issuer:|Subject:|Not After"
echo ""
log_warn "Note: These are self-signed certificates for development/testing."
log_warn "For production, use Let's Encrypt with the ssl-setup.sh script."
echo ""
