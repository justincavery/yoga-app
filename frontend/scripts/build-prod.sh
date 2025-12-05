#!/bin/bash
# Production Build Script for YogaFlow Frontend
# This script builds the frontend for production deployment

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/dist"

echo -e "${GREEN}Starting YogaFlow Frontend Production Build${NC}"
echo "Project Root: $PROJECT_ROOT"
echo ""

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 1. Check Node.js
log_info "Checking Node.js installation..."
if ! command -v node >/dev/null 2>&1; then
    log_error "Node.js is not installed"
    exit 1
fi
log_info "Node version: $(node --version)"

# 2. Check environment file
if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
    log_error ".env.production file not found"
    log_error "Create it from .env.example and set production values"
    exit 1
fi

# 3. Clean previous build
if [ -d "$BUILD_DIR" ]; then
    log_info "Cleaning previous build..."
    rm -rf "$BUILD_DIR"
fi

# 4. Install dependencies
log_info "Installing dependencies..."
cd "$PROJECT_ROOT"
npm ci --production=false

# 5. Run linter
log_info "Running linter..."
npm run lint || {
    log_warn "Linting failed. Continue? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
}

# 6. Run tests
log_info "Running tests..."
npm run test:run || {
    log_error "Tests failed. Aborting build."
    exit 1
}

# 7. Build for production
log_info "Building for production..."
NODE_ENV=production npm run build

# 8. Verify build
if [ ! -d "$BUILD_DIR" ]; then
    log_error "Build failed - dist directory not created"
    exit 1
fi

log_info "Build completed successfully"
log_info "Build output: $BUILD_DIR"
log_info "Build size:"
du -sh "$BUILD_DIR"

# 9. Build summary
echo ""
echo -e "${GREEN}Production build complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Test the build locally: npm run preview"
echo "2. Deploy to your hosting service:"
echo "   - Netlify: netlify deploy --prod --dir=dist"
echo "   - Vercel: vercel --prod"
echo "   - AWS S3: aws s3 sync dist/ s3://your-bucket-name/"
echo "3. Verify deployment: https://yourdomain.com"
echo ""
