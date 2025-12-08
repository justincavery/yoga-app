#!/bin/bash
#
# Quick Database Seeding - Run on Hetzner Server
# This is a simplified version that can be executed directly via SSH
#

set -e

echo "YogaFlow - Quick Database Seed"
echo "==============================="
echo ""

# Check backend container
if ! docker ps | grep -q yogaflow-backend; then
    echo "ERROR: Backend container not running!"
    exit 1
fi

echo "✓ Backend container is running"
echo ""

# Run import
echo "Seeding database..."
docker exec yogaflow-backend python -m scripts.import_poses_auto

echo ""
echo "Verifying..."
sleep 2

# Check count
POSES=$(curl -s http://localhost:8000/api/v1/poses | jq -r '.total' 2>/dev/null || echo "0")
echo "Poses in database: $POSES"

if [[ "$POSES" -gt 0 ]]; then
    echo "✅ SUCCESS! Database has $POSES poses"
else
    echo "❌ FAILED: Database still empty"
    exit 1
fi
