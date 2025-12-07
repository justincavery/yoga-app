#!/bin/bash
#
# Hetzner Server Provisioning Script for YogaFlow
#
# This script sets up a fresh Ubuntu server with Docker, Docker Compose,
# Nginx, security hardening, and all dependencies needed for deployment.
#
# Usage: Run this once on a fresh Hetzner CPX21 server
#   chmod +x server-provision.sh
#   sudo ./server-provision.sh
#

set -euo pipefail

# Color output
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

log_info "Starting YogaFlow server provisioning..."

# Update system
log_info "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install essential packages
log_info "Installing essential packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw \
    fail2ban \
    htop \
    vim \
    wget \
    unzip \
    software-properties-common

# Install Docker
log_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Start and enable Docker
    systemctl start docker
    systemctl enable docker

    log_info "Docker installed successfully"
else
    log_info "Docker already installed"
fi

# Create deploy user
log_info "Creating deploy user..."
if ! id "deploy" &>/dev/null; then
    useradd -m -s /bin/bash deploy
    usermod -aG docker deploy
    log_info "Deploy user created"
else
    log_info "Deploy user already exists"
fi

# Grant deploy user sudo privileges for deployment tasks
log_info "Configuring sudo access for deploy user..."
cat > /etc/sudoers.d/deploy <<EOF
# Allow deploy user to manage services for deployment
deploy ALL=(ALL) NOPASSWD: /bin/systemctl stop nginx
deploy ALL=(ALL) NOPASSWD: /bin/systemctl disable nginx
deploy ALL=(ALL) NOPASSWD: /bin/systemctl is-active nginx
deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart docker
EOF
chmod 0440 /etc/sudoers.d/deploy
log_info "Sudo configuration completed"

# Set up SSH for deploy user
log_info "Setting up SSH for deploy user..."
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
touch /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh

log_warn "IMPORTANT: Add your GitHub Actions SSH public key to /home/deploy/.ssh/authorized_keys"
log_warn "You can do this by running:"
log_warn "  echo 'YOUR_PUBLIC_KEY' >> /home/deploy/.ssh/authorized_keys"

# Create application directories
log_info "Creating application directories..."
mkdir -p /opt/yogaflow/{backend,frontend,nginx,postgres-data,logs,backups}
chown -R deploy:deploy /opt/yogaflow
chmod -R 755 /opt/yogaflow

# Install Nginx
log_info "Installing Nginx..."
apt-get install -y nginx
systemctl start nginx
systemctl enable nginx

# Install Certbot for SSL
log_info "Installing Certbot..."
apt-get install -y certbot python3-certbot-nginx

# Configure firewall
log_info "Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

log_info "Firewall configured"

# Configure fail2ban for SSH protection
log_info "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
EOF

systemctl restart fail2ban
systemctl enable fail2ban

log_info "Fail2ban configured"

# Optimize Docker for production
log_info "Configuring Docker for production..."
cat > /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

systemctl restart docker

# Set up automatic security updates
log_info "Configuring automatic security updates..."
apt-get install -y unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";
EOF

# Create backup script
log_info "Creating backup script..."
cat > /opt/yogaflow/backup.sh <<'EOF'
#!/bin/bash
# Database backup script
BACKUP_DIR="/opt/yogaflow/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/postgres_backup_$TIMESTAMP.sql.gz"

# Create backup
docker exec yogaflow-postgres pg_dump -U yogaflow yogaflow | gzip > "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "postgres_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x /opt/yogaflow/backup.sh
chown deploy:deploy /opt/yogaflow/backup.sh

# Set up daily backup cron job
log_info "Setting up daily backups..."
(crontab -u deploy -l 2>/dev/null; echo "0 2 * * * /opt/yogaflow/backup.sh >> /opt/yogaflow/logs/backup.log 2>&1") | crontab -u deploy -

# Create .env template
log_info "Creating .env template..."
cat > /opt/yogaflow/.env.template <<EOF
# YogaFlow Environment Configuration
# Copy this to .env and fill in your values

# Application
ENVIRONMENT=production
SECRET_KEY=CHANGE_THIS_TO_RANDOM_STRING
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://yogaflow:CHANGE_DB_PASSWORD@postgres:5432/yogaflow
POSTGRES_USER=yogaflow
POSTGRES_PASSWORD=CHANGE_DB_PASSWORD
POSTGRES_DB=yogaflow

# CORS - Update with your domain
ALLOWED_ORIGINS=https://your-domain.com

# Frontend
VITE_API_URL=https://api.your-domain.com

# Email (optional)
EMAIL_ENABLED=false
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# Monitoring (optional)
SENTRY_DSN=
EOF

chown deploy:deploy /opt/yogaflow/.env.template

# System optimizations
log_info "Applying system optimizations..."
cat >> /etc/sysctl.conf <<EOF

# YogaFlow optimizations
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
vm.swappiness = 10
EOF

sysctl -p

# Display summary
log_info "================================================"
log_info "Server provisioning completed successfully!"
log_info "================================================"
echo ""
log_info "Next steps:"
echo "  1. Add GitHub Actions SSH public key to /home/deploy/.ssh/authorized_keys"
echo "  2. Copy /opt/yogaflow/.env.template to /opt/yogaflow/.env and configure"
echo "  3. Update DNS records to point to this server IP: $(curl -s ifconfig.me)"
echo "  4. Deploy application via GitHub Actions"
echo ""
log_info "Server details:"
echo "  - Deploy user: deploy"
echo "  - Application directory: /opt/yogaflow"
echo "  - Backup script: /opt/yogaflow/backup.sh (runs daily at 2 AM)"
echo "  - Docker installed: $(docker --version)"
echo "  - Nginx installed: $(nginx -v 2>&1)"
echo ""
log_warn "Security reminders:"
echo "  - Change SSH port (optional but recommended)"
echo "  - Set up SSH key-only authentication"
echo "  - Configure domain SSL with: certbot --nginx -d yourdomain.com"
echo ""
log_info "You can now deploy using GitHub Actions!"
