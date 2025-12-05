#!/bin/bash
# Production Deployment Script for YogaFlow Backend
# This script handles database migrations, health checks, and deployment

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_ENV="${DEPLOY_ENV:-production}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"

echo -e "${GREEN}Starting YogaFlow Backend Deployment${NC}"
echo "Environment: $DEPLOY_ENV"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Function to print colored messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Pre-deployment checks
log_info "Running pre-deployment checks..."

# Check Python
if ! command_exists python3; then
    log_error "Python 3 is not installed"
    exit 1
fi

# Check environment file
if [ "$DEPLOY_ENV" = "production" ] && [ ! -f "$PROJECT_ROOT/.env.production" ]; then
    log_error ".env.production file not found"
    exit 1
fi

# Check virtual environment
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/venv"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# 2. Install/Update dependencies
log_info "Installing dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"

# 3. Run tests (unless skipped)
if [ "$SKIP_TESTS" = "false" ]; then
    log_info "Running tests..."
    cd "$PROJECT_ROOT"
    if pytest app/tests/ -v; then
        log_info "All tests passed"
    else
        log_error "Tests failed. Deployment aborted."
        exit 1
    fi
else
    log_warn "Skipping tests (SKIP_TESTS=true)"
fi

# 4. Database migrations
if [ "$SKIP_MIGRATIONS" = "false" ]; then
    log_info "Running database migrations..."
    cd "$PROJECT_ROOT"

    # Check if there are pending migrations
    if alembic current 2>&1 | grep -q "Can't locate revision"; then
        log_warn "Database not initialized. Running initial migration..."
        alembic upgrade head
    else
        log_info "Applying migrations..."
        alembic upgrade head
    fi

    log_info "Migrations completed"
else
    log_warn "Skipping migrations (SKIP_MIGRATIONS=true)"
fi

# 5. Health check on existing service (if running)
log_info "Checking if service is already running..."
if command_exists curl; then
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_info "Service is running. Will perform graceful restart."
        GRACEFUL_RESTART=true
    else
        log_info "Service is not running. Will perform fresh start."
        GRACEFUL_RESTART=false
    fi
else
    log_warn "curl not found. Skipping health check."
    GRACEFUL_RESTART=false
fi

# 6. Stop existing service (if using systemd)
if command_exists systemctl; then
    if systemctl is-active --quiet yogaflow-api; then
        log_info "Stopping existing service..."
        sudo systemctl stop yogaflow-api
    fi
fi

# 7. Deployment complete message
log_info "${GREEN}Deployment preparation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review the deployment checklist: docs/deployment-checklist.md"
echo "2. Start the service:"
echo "   - Using systemd: sudo systemctl start yogaflow-api"
echo "   - Using Docker: docker-compose up -d backend"
echo "   - Manual: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"
echo "3. Verify health: curl http://localhost:8000/health"
echo "4. Monitor logs for errors"
echo ""
log_info "Deployment script completed successfully"
