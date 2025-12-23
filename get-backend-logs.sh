#!/bin/bash
# Get backend logs from production server
# Run locally: ./get-backend-logs.sh

SERVER="23.88.127.14"
USER="deploy"  # or root

echo "Fetching backend logs from $SERVER..."

ssh ${USER}@${SERVER} << 'ENDSSH'
cd /opt/yogaflow

echo "=== Container Status ==="
docker ps -a | grep yogaflow

echo ""
echo "=== Backend Container Logs (last 150 lines) ==="
docker logs --tail=150 yogaflow-backend

echo ""
echo "=== Backend Container Inspect ==="
docker inspect yogaflow-backend --format='Status: {{.State.Status}}'
docker inspect yogaflow-backend --format='Health: {{json .State.Health}}'

ENDSSH

echo ""
echo "Done!"
