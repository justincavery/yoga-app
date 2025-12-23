#!/bin/bash
#
# Manual Database Seeding from Local Machine
# Run this script from your LOCAL machine to seed the production database
#
# Usage: ./manual-seed-from-local.sh SERVER_IP
#

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 SERVER_IP"
    echo "Example: $0 95.217.123.45"
    exit 1
fi

SERVER_IP=$1
DEPLOY_USER="root"

echo "🔄 Manual Database Seeding"
echo "=========================="
echo "Server: $SERVER_IP"
echo ""

# Check if we're in the project root
if [ ! -f "content/poses.yaml" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "   content/poses.yaml not found"
    exit 1
fi

echo "✓ Found content/poses.yaml"
echo ""

# Create temporary package
echo "📦 Creating package..."
tar -czf /tmp/yoga-seed.tar.gz content/ backend/scripts/import_poses_auto.py

echo "✓ Package created"
echo ""

# Copy to server
echo "📤 Copying to server..."
scp /tmp/yoga-seed.tar.gz ${DEPLOY_USER}@${SERVER_IP}:/tmp/

echo "✓ Copied to server"
echo ""

# Extract and run on server
echo "🌱 Seeding database on server..."
ssh ${DEPLOY_USER}@${SERVER_IP} << 'ENDSSH'
    set -e

    cd /opt/yogaflow

    # Extract package
    echo "Extracting files..."
    tar -xzf /tmp/yoga-seed.tar.gz
    rm /tmp/yoga-seed.tar.gz

    echo "✓ Files extracted"
    echo ""

    # Check current pose count
    echo "Checking current database..."
    BEFORE=$(curl -s http://localhost:8000/api/v1/poses | jq -r '.total' 2>/dev/null || echo "0")
    echo "Poses before: $BEFORE"
    echo ""

    # Copy files into container
    echo "Copying files into backend container..."
    docker cp content yogaflow-backend:/app/
    docker cp backend/scripts/import_poses_auto.py yogaflow-backend:/app/scripts/

    # Run import
    echo "Running import script..."
    docker exec yogaflow-backend python /app/scripts/import_poses_auto.py

    echo ""
    echo "Verifying..."
    sleep 2

    # Check new count
    AFTER=$(curl -s http://localhost:8000/api/v1/poses | jq -r '.total' 2>/dev/null || echo "0")
    echo "Poses after: $AFTER"
    echo ""

    if [ "$AFTER" -gt 0 ]; then
        echo "✅ SUCCESS! Database now has $AFTER poses"
    else
        echo "❌ FAILED: Database still empty"
        exit 1
    fi
ENDSSH

echo ""
echo "=========================="
echo "✅ Database Seeding Complete!"
echo ""
echo "Test it:"
echo "  curl https://app.laurayoga.co.uk/api/v1/poses | jq '.total'"
echo ""
echo "Visit your dashboard:"
echo "  https://app.laurayoga.co.uk/dashboard"
echo ""
