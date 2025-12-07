#!/bin/bash
#
# Seed Database Script
# Run this on the Hetzner server to populate the database with poses
#
# Usage: ./seed-database.sh [--force]
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

log_info "YogaFlow Database Seeding Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [[ ! -f docker-compose.prod.yml ]]; then
    log_error "docker-compose.prod.yml not found!"
    log_error "Please run this script from /opt/yogaflow directory"
    exit 1
fi

# Check if content/poses.yaml exists
if [[ ! -f content/poses.yaml ]]; then
    log_error "content/poses.yaml not found!"
    log_error "Poses data file is missing"
    exit 1
fi

log_info "Found poses.yaml with $(grep -c "name_english:" content/poses.yaml) poses"
echo ""

# Check if backend container is running
if ! docker ps | grep -q yogaflow-backend; then
    log_error "Backend container is not running!"
    log_error "Please start containers first: docker compose -f docker-compose.prod.yml up -d"
    exit 1
fi

log_info "Backend container is running"
echo ""

# Build force flag if provided
FORCE_FLAG=""
if [[ "${1:-}" == "--force" ]]; then
    FORCE_FLAG="--force"
    log_warn "Force mode enabled - will clear existing poses"
fi

# Run the import script inside the backend container
log_info "Running database import..."
docker exec yogaflow-backend python -m scripts.import_poses_auto $FORCE_FLAG

# Check if import was successful
if [[ $? -eq 0 ]]; then
    log_info "✓ Database seeding completed successfully!"
    echo ""

    # Verify poses were imported
    log_info "Verifying import..."
    POSE_COUNT=$(curl -s http://localhost:8000/api/v1/poses | jq -r '.total' 2>/dev/null || echo "0")

    if [[ "$POSE_COUNT" -gt 0 ]]; then
        log_info "✓ Verified: $POSE_COUNT poses in database"
    else
        log_warn "Could not verify pose count"
    fi
else
    log_error "Database seeding failed!"
    exit 1
fi

echo ""
log_info "======================================"
log_info "Database seeding complete!"
log_info "You can now access the application with data"
log_info "======================================"
echo ""
