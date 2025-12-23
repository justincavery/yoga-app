#!/bin/bash
# Diagnose and fix backend container issues

set -e

cd /opt/yogaflow

echo "=== Backend Container Diagnostics ==="
echo ""

echo "1. Container Status:"
docker ps -a | grep yogaflow

echo ""
echo "2. Backend Container Logs (last 50 lines):"
docker logs --tail=50 yogaflow-backend

echo ""
echo "3. Health Check Status:"
docker inspect yogaflow-backend --format='{{.State.Health.Status}}'

echo ""
echo "4. Last Health Check Log:"
docker inspect yogaflow-backend --format='{{range .State.Health.Log}}{{.Output}}{{end}}' | tail -5

echo ""
echo "5. Database Connection:"
docker exec yogaflow-postgres pg_isready -U yogaflow

echo ""
echo "=== Attempting to Fix ==="

# Restart backend container
echo "Restarting backend container..."
docker-compose -f docker-compose.prod.yml restart backend

sleep 10

echo "New status:"
docker ps | grep backend

echo ""
echo "Done! Check if backend is now healthy."
