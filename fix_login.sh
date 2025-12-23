#!/bin/bash
# Fix missing login columns

echo "Adding missing columns to users table..."
docker exec yogaflow-postgres psql -U yogaflow -d yogaflow << 'EOF'
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN account_locked_until TIMESTAMP;
EOF

echo ""
echo "Verifying columns were added..."
docker exec yogaflow-postgres psql -U yogaflow -d yogaflow -c "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name IN ('failed_login_attempts', 'account_locked_until');"

echo ""
echo "Restarting backend..."
docker compose -f docker-compose.prod.yml restart backend

echo ""
echo "Done! Try logging in now."
