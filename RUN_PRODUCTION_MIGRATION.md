# Production Database Migration Guide

## ⚠️ IMPORTANT: Run This After Deployment

The login is now working with backward compatibility, but you should run the database migration to enable the account lockout security feature.

## What This Migration Does

Adds two security columns to the `users` table:
- `failed_login_attempts` - Tracks failed login attempts
- `account_locked_until` - Timestamp when account lockout expires

These enable automatic account lockout after 5 failed login attempts (configurable).

## How to Run Migration on Production

### Option 1: Via SSH (Recommended)

```bash
# SSH into your production server
ssh deploy@YOUR_SERVER_IP

# Navigate to application directory
cd /opt/yogaflow

# Run the migration inside the backend container
docker exec yogaflow-backend alembic upgrade head

# Verify the migration
docker exec yogaflow-backend alembic current

# Check backend logs for any errors
docker logs --tail=50 yogaflow-backend
```

### Option 2: During Deployment

If you want migrations to run automatically on deployment, update your GitHub Actions workflow:

**File:** `.github/workflows/deploy-hetzner.yml`

Add this step after container startup (around line 195):

```yaml
- name: Run database migrations
  run: |
    ssh deploy@${{ secrets.HETZNER_SERVER_IP }} << 'ENDSSH'
      cd /opt/yogaflow

      # Wait for backend to be healthy
      echo "Waiting for backend to be ready..."
      sleep 10

      # Run migrations
      docker exec yogaflow-backend alembic upgrade head

      # Verify
      docker exec yogaflow-backend alembic current
    ENDSSH
```

## Verify Migration Was Successful

```bash
# Check current migration version
docker exec yogaflow-backend alembic current

# Should show:
# b5f321cd1234 (head)
# add account lockout fields
```

## Rollback (If Needed)

If something goes wrong, you can rollback:

```bash
# Rollback one migration
docker exec yogaflow-backend alembic downgrade -1

# Or rollback to specific revision
docker exec yogaflow-backend alembic downgrade ac494d920e90
```

## What Happens After Migration

### Account Lockout Feature Enabled
- After 5 failed login attempts, account locks for 30 minutes
- User sees: "Account is locked due to too many failed login attempts. Try again in X minutes."
- Lockout automatically expires after configured time
- Failed attempt counter resets on successful login

### Configuration (Optional)

You can adjust these settings in your `.env` file:

```bash
# Maximum failed login attempts before lockout (default: 5)
MAX_LOGIN_ATTEMPTS=5

# Lockout duration in minutes (default: 30)
ACCOUNT_LOCKOUT_MINUTES=30
```

After changing settings:
```bash
docker compose -f docker-compose.prod.yml restart backend
```

## Migration File Details

**File:** `backend/alembic/versions/add_account_lockout_fields.py`

**Revision:** `b5f321cd1234`
**Previous Revision:** `ac494d920e90`

### SQL Executed

```sql
-- Add account security columns
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN account_locked_until TIMESTAMP;
```

## Troubleshooting

### Migration Fails

```bash
# Check if backend container is running
docker ps | grep yogaflow-backend

# Check backend logs
docker logs yogaflow-backend

# Check database connection
docker exec yogaflow-backend python -c "from app.core.database import engine; print('DB OK')"
```

### Migration Already Applied

If you see "Target database is not up to date" or migration already exists:

```bash
# Check migration history
docker exec yogaflow-backend alembic history

# Check current version
docker exec yogaflow-backend alembic current

# If stuck, try:
docker exec yogaflow-backend alembic stamp head
docker exec yogaflow-backend alembic upgrade head
```

### Database Connection Issues

```bash
# Verify database is running
docker exec yogaflow-postgres pg_isready -U yogaflow

# Check database connection from backend
docker exec yogaflow-backend python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.getenv('DATABASE_URL').replace('asyncpg', 'psycopg2'))
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print(result.fetchone())
"
```

## Current Status

**Deployment:** Emergency fix deployed (backward compatible)
**Migration Status:** Not yet run on production
**Login Status:** ✅ Working (without lockout feature)
**After Migration:** ✅ Working (with lockout feature)

## Timeline

1. **Now:** Deployment in progress (5-10 minutes)
2. **After deployment:** Login works, but no account lockout yet
3. **Run migration:** Enable account lockout security feature
4. **Done:** Full security features active

## Questions?

- Check GitHub Actions for deployment status
- Check backend logs: `docker logs yogaflow-backend`
- Check database status: `docker exec yogaflow-postgres pg_isready`
