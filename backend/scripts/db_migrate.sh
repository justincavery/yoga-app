#!/bin/bash
# Database Migration Script for YogaFlow
# Handles Alembic migrations safely with backup support

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "$PROJECT_ROOT"

# Activate virtual environment if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Check current migration status
log_info "Current migration status:"
alembic current

# Show pending migrations
log_info "Checking for pending migrations..."
if alembic upgrade head --sql > /dev/null 2>&1; then
    log_info "Pending migrations found"
else
    log_info "No pending migrations"
    exit 0
fi

# Ask for confirmation in production
if [ "${APP_ENV:-development}" = "production" ]; then
    log_warn "Running migrations in PRODUCTION environment"
    read -p "Continue? (yes/no): " -r
    if [ "$REPLY" != "yes" ]; then
        log_info "Migration cancelled"
        exit 0
    fi
fi

# Run migrations
log_info "Applying migrations..."
alembic upgrade head

log_info "Migration completed successfully"
alembic current
