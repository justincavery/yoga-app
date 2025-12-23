#!/bin/bash
#
# Update production database with pose image URLs
# Run this after deployment completes successfully
#

SERVER="23.88.127.14"
USER="root"

echo "Updating pose images in production database..."
echo "=============================================="
echo ""

ssh ${USER}@${SERVER} << 'ENDSSH'
set -e

cd /opt/yogaflow

# Check if backend container is running
if ! docker ps | grep -q yogaflow-backend; then
    echo "ERROR: Backend container is not running!"
    docker ps -a | grep yogaflow
    exit 1
fi

echo "Backend container is healthy"
echo ""

# Run the update script
echo "Running database update script..."
docker exec yogaflow-backend python /app/scripts/update_pose_images.py

# Verify images were updated
echo ""
echo "Verifying update..."
docker exec yogaflow-backend python /app/scripts/update_pose_images.py --list | head -10

ENDSSH

echo ""
echo "=============================================="
echo "Database update complete!"
echo "Pose images and thumbnails are now populated."
echo "=============================================="
