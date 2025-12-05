#!/bin/bash
# Health Check Script for YogaFlow Backend
# Used for monitoring and deployment verification

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TIMEOUT="${TIMEOUT:-5}"
MAX_RETRIES="${MAX_RETRIES:-3}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

check_endpoint() {
    local endpoint=$1
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s --max-time "$TIMEOUT" "${API_URL}${endpoint}" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $endpoint is healthy"
            return 0
        fi
        retries=$((retries + 1))
        if [ $retries -lt $MAX_RETRIES ]; then
            sleep 2
        fi
    done

    echo -e "${RED}✗${NC} $endpoint is unhealthy"
    return 1
}

echo "Checking YogaFlow API Health..."
echo "API URL: $API_URL"
echo ""

# Check health endpoint
if ! check_endpoint "/health"; then
    echo -e "${RED}Health check failed${NC}"
    exit 1
fi

# Check root endpoint
if ! check_endpoint "/"; then
    echo -e "${RED}Root endpoint check failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}All health checks passed${NC}"
exit 0
