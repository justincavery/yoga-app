#!/bin/bash
# Comprehensive backend container diagnostics
# Run on server: ./diagnose-backend-detailed.sh

set -e

cd /opt/yogaflow

echo "=== YogaFlow Backend Diagnostics ==="
echo ""

echo "1. All Container Status:"
docker ps -a | grep yogaflow || echo "No containers found"

echo ""
echo "2. Docker Compose Services:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "3. Redis Status:"
docker ps -a | grep redis
if docker ps | grep -q yogaflow-redis; then
  echo "Redis is running"
  docker exec yogaflow-redis redis-cli ping
else
  echo "Redis is NOT running"
fi

echo ""
echo "4. Postgres Status:"
docker ps -a | grep postgres
if docker ps | grep -q yogaflow-postgres; then
  echo "Postgres is running"
  docker exec yogaflow-postgres pg_isready -U yogaflow
else
  echo "Postgres is NOT running"
fi

echo ""
echo "5. Backend Container Status:"
if docker ps -a | grep -q yogaflow-backend; then
  echo "Backend container exists"

  echo ""
  echo "5a. Container Details:"
  docker inspect yogaflow-backend --format='State: {{.State.Status}}'
  docker inspect yogaflow-backend --format='Health: {{.State.Health.Status}}'
  docker inspect yogaflow-backend --format='Exit Code: {{.State.ExitCode}}'
  docker inspect yogaflow-backend --format='Error: {{.State.Error}}'

  echo ""
  echo "5b. Container Environment:"
  docker inspect yogaflow-backend --format='{{range .Config.Env}}{{println .}}{{end}}' | grep -E '(DATABASE_URL|REDIS_URL|SECRET_KEY|ENVIRONMENT)' || echo "No env vars found"

  echo ""
  echo "5c. Health Check Configuration:"
  docker inspect yogaflow-backend --format='{{json .Config.Healthcheck}}' | python3 -m json.tool 2>/dev/null || echo "No health check configured"

  echo ""
  echo "5d. Last 100 Lines of Backend Logs:"
  docker logs --tail=100 yogaflow-backend

  echo ""
  echo "5e. Check if /health endpoint is accessible:"
  if docker ps | grep -q yogaflow-backend; then
    docker exec yogaflow-backend curl -f http://localhost:8000/health 2>&1 || echo "Health endpoint not accessible"
  else
    echo "Container not running, cannot check health endpoint"
  fi
else
  echo "Backend container does not exist"
fi

echo ""
echo "6. Network Configuration:"
docker network ls | grep yogaflow || echo "No yogaflow network found"
if docker network ls | grep -q yogaflow; then
  docker network inspect yogaflow_yogaflow-network | python3 -m json.tool | head -50
fi

echo ""
echo "7. Volume Mounts:"
docker inspect yogaflow-backend --format='{{range .Mounts}}{{println .Source "→" .Destination}}{{end}}' 2>/dev/null || echo "Cannot inspect mounts"

echo ""
echo "8. Check if content directory exists:"
ls -la /opt/yogaflow/content/images/poses/ | head -20 || echo "Content directory not found"

echo ""
echo "9. Check .env file:"
if [ -f /opt/yogaflow/.env ]; then
  echo ".env file exists"
  echo "Environment variables (secrets masked):"
  grep -v -E '(PASSWORD|SECRET|KEY)' /opt/yogaflow/.env || echo "All vars contain secrets"
else
  echo ".env file NOT found"
fi

echo ""
echo "=== Diagnostic complete ==="
echo ""
echo "Common issues to check:"
echo "1. Backend logs show connection errors to Postgres or Redis"
echo "2. DATABASE_URL environment variable is not set or incorrect"
echo "3. REDIS_URL environment variable is not set or incorrect"
echo "4. SECRET_KEY is not set"
echo "5. Backend container is crashing on startup (check Exit Code)"
echo "6. Health check is failing (check logs for /health endpoint errors)"
