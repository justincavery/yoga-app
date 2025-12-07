#!/bin/bash
#
# One-time fix to grant deploy user sudo privileges
# Run this on your Hetzner server as root
#
# Usage: sudo ./fix-sudo-permissions.sh
#

set -euo pipefail

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root (use sudo)"
   exit 1
fi

echo "Configuring sudo access for deploy user..."

# Grant deploy user sudo privileges for deployment tasks
cat > /etc/sudoers.d/deploy <<'EOF'
# Allow deploy user to manage services for deployment
deploy ALL=(ALL) NOPASSWD: /bin/systemctl stop nginx
deploy ALL=(ALL) NOPASSWD: /bin/systemctl disable nginx
deploy ALL=(ALL) NOPASSWD: /bin/systemctl is-active nginx
deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart docker
EOF

chmod 0440 /etc/sudoers.d/deploy

# Validate sudoers file
if visudo -c -f /etc/sudoers.d/deploy; then
    echo "✓ Sudo configuration completed successfully"
else
    echo "ERROR: Invalid sudoers configuration"
    rm /etc/sudoers.d/deploy
    exit 1
fi

# Stop system Nginx now to free ports for Docker
if systemctl is-active --quiet nginx; then
    echo "Stopping system Nginx..."
    systemctl stop nginx
    systemctl disable nginx
    echo "✓ System Nginx stopped and disabled"
fi

echo ""
echo "Setup complete! The deploy user can now:"
echo "  - Stop/disable system Nginx"
echo "  - Check Nginx status"
echo "  - Restart Docker if needed"
echo ""
echo "You can now trigger a deployment from GitHub Actions."
