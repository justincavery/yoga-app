#!/bin/bash
# Deploy and update database on Hetzner server
# Run this locally: ./deploy-and-update.sh

set -e

SERVER="23.88.127.14"
USER="root"  # Change to 'deploy' if using deploy user

echo "🔍 Checking deployment status on server..."

ssh ${USER}@${SERVER} << 'ENDSSH'
set -e

cd /opt/yogaflow

echo "=== Container Status ==="
docker ps

echo ""
echo "=== Backend Logs (last 20 lines) ==="
docker logs --tail=20 yogaflow-backend

echo ""
echo "=== Updating Database with Pose Images ==="

# Copy update script to container if needed
docker cp backend/scripts/update_pose_images.py yogaflow-backend:/app/scripts/ 2>/dev/null || true

# Run database update
docker exec yogaflow-backend python scripts/update_pose_images.py

echo ""
echo "✅ Database updated successfully!"
echo ""
echo "=== Final Container Status ==="
docker ps | grep yogaflow

ENDSSH

echo ""
echo "✅ All done! The app should be live with images at http://23.88.127.14"
