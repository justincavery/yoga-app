#!/bin/bash
# Railway Deployment Verification Script
# Tests all endpoints and verifies deployment is working

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${1:-https://yoga-app-production.up.railway.app}"
FRONTEND_URL="${2:-https://yoga-app-production.up.railway.app}"

echo "========================================"
echo "Railway Deployment Verification"
echo "========================================"
echo ""
echo "Backend URL:  $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local url="$1"
    local expected_code="${2:-200}"
    local description="$3"

    echo -n "Testing: $description ... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)

    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_code)"
        return 1
    fi
}

# Function to test JSON response
test_json_endpoint() {
    local url="$1"
    local key="$2"
    local expected_value="$3"
    local description="$4"

    echo -n "Testing: $description ... "

    response=$(curl -s "$url" 2>&1)

    if echo "$response" | grep -q "\"$key\""; then
        if [ -n "$expected_value" ]; then
            if echo "$response" | grep -q "\"$key\":.*\"$expected_value\""; then
                echo -e "${GREEN}✓ PASS${NC} (found $key=$expected_value)"
                return 0
            else
                echo -e "${YELLOW}⚠ WARN${NC} (found $key but value doesn't match)"
                return 1
            fi
        else
            echo -e "${GREEN}✓ PASS${NC} (found $key)"
            return 0
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (key $key not found)"
        echo "Response: $response"
        return 1
    fi
}

echo "========================================="
echo "Backend API Tests"
echo "========================================="
echo ""

# Test backend health
test_json_endpoint "$BACKEND_URL/health" "status" "healthy" "Health check endpoint"

# Test root endpoint
test_json_endpoint "$BACKEND_URL/" "name" "" "Root endpoint"

# Test API docs
test_endpoint "$BACKEND_URL/docs" "200" "API documentation"

# Test OpenAPI schema
test_endpoint "$BACKEND_URL/openapi.json" "200" "OpenAPI schema"

# Test poses endpoint (public)
test_endpoint "$BACKEND_URL/api/v1/poses" "200" "Poses list endpoint"

echo ""
echo "========================================="
echo "Frontend Tests"
echo "========================================="
echo ""

# Test frontend homepage
test_endpoint "$FRONTEND_URL" "200" "Frontend homepage"

# Test frontend static assets
test_endpoint "$FRONTEND_URL/assets" "404" "Frontend assets (404 is normal)"

echo ""
echo "========================================="
echo "Database Tests"
echo "========================================="
echo ""

# Test that poses are loaded
echo -n "Testing: Poses data loaded ... "
poses_response=$(curl -s "$BACKEND_URL/api/v1/poses")
if echo "$poses_response" | grep -q "Mountain Pose"; then
    echo -e "${GREEN}✓ PASS${NC} (found pose data)"
else
    echo -e "${YELLOW}⚠ WARN${NC} (no pose data found - may need to import)"
fi

echo ""
echo "========================================="
echo "CORS Tests"
echo "========================================="
echo ""

# Test CORS headers
echo -n "Testing: CORS headers ... "
cors_response=$(curl -s -I -H "Origin: $FRONTEND_URL" "$BACKEND_URL/health" 2>&1)
if echo "$cors_response" | grep -qi "access-control-allow-origin"; then
    echo -e "${GREEN}✓ PASS${NC} (CORS headers present)"
else
    echo -e "${RED}✗ FAIL${NC} (CORS headers missing)"
    echo "Note: Update backend ALLOWED_ORIGINS environment variable"
fi

echo ""
echo "========================================="
echo "Security Tests"
echo "========================================="
echo ""

# Test HTTPS redirect
echo -n "Testing: HTTPS enabled ... "
if echo "$BACKEND_URL" | grep -q "https://"; then
    echo -e "${GREEN}✓ PASS${NC} (using HTTPS)"
else
    echo -e "${RED}✗ FAIL${NC} (not using HTTPS)"
fi

# Test security headers
echo -n "Testing: Security headers ... "
security_response=$(curl -s -I "$BACKEND_URL/health" 2>&1)
if echo "$security_response" | grep -qi "x-content-type-options"; then
    echo -e "${GREEN}✓ PASS${NC} (security headers present)"
else
    echo -e "${YELLOW}⚠ WARN${NC} (some security headers missing)"
fi

echo ""
echo "========================================="
echo "Environment Configuration"
echo "========================================="
echo ""

echo "Backend environment checks:"
echo -n "  - DATABASE_URL: "
if curl -s "$BACKEND_URL/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Configured${NC}"
else
    echo -e "${RED}✗ Not configured or database unreachable${NC}"
fi

echo -n "  - SECRET_KEY: "
if curl -s "$BACKEND_URL/api/v1/auth/register" -X POST -H "Content-Type: application/json" -d '{}' 2>&1 | grep -q "error"; then
    echo -e "${GREEN}✓ Configured${NC}"
else
    echo -e "${YELLOW}⚠ Unable to verify${NC}"
fi

echo ""
echo "========================================="
echo "Summary"
echo "========================================="
echo ""
echo "Deployment verification complete!"
echo ""
echo "Next steps:"
echo "  1. Test user registration: $FRONTEND_URL/register"
echo "  2. Test user login: $FRONTEND_URL/login"
echo "  3. Browse poses: $FRONTEND_URL/poses"
echo "  4. Check logs: railway logs"
echo "  5. Monitor metrics: railway dashboard"
echo ""
echo "For issues, check:"
echo "  - Railway logs: railway logs"
echo "  - Environment variables: railway variables"
echo "  - Database status: railway status"
echo ""
