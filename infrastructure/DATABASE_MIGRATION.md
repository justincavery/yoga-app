# Database Migration Plan: SQLite → PostgreSQL

Migration guide for YogaFlow database from development SQLite to production PostgreSQL on Railway.

## Overview

**Current:** SQLite (development)
**Target:** PostgreSQL (production on Railway)
**Migration Tool:** Alembic (already configured)
**Data Loss:** None (automated migration)

## Why PostgreSQL?

1. **Production-Ready**
   - ACID compliance
   - Concurrent connections
   - Advanced features (JSON, full-text search)

2. **Railway Compatibility**
   - Managed PostgreSQL service
   - Automatic backups
   - Connection pooling
   - SSL by default

3. **Scalability**
   - Handles multiple users
   - Better performance under load
   - Advanced indexing

## Migration Strategy

### Automatic Migration (Recommended)

Railway deployment handles migration automatically:

1. **Railway provides PostgreSQL**
   - Automatically creates `DATABASE_URL`
   - Format: `postgresql://user:pass@host:port/db`

2. **Backend handles conversion**
   - `app/core/database.py` detects PostgreSQL URL
   - Converts to async format: `postgresql+asyncpg://...`

3. **Alembic runs migrations**
   - Docker startup script runs: `alembic upgrade head`
   - Creates all tables from schema
   - No data loss (migrations are idempotent)

### Manual Migration (Development → Production)

If you need to migrate existing data:

#### Step 1: Export SQLite Data

```bash
# From backend directory
cd /Users/justinavery/claude/yoga-app/backend

# Activate virtual environment
source venv/bin/activate

# Export data using custom script
python scripts/export_data.py
```

Creates: `data_export.json` with all records

#### Step 2: Deploy to Railway

```bash
# Deploy backend (creates PostgreSQL tables)
cd backend
railway up
```

Wait for deployment to complete.

#### Step 3: Import Data to PostgreSQL

```bash
# Import data to Railway PostgreSQL
railway run python scripts/import_data.py data_export.json
```

## Database Configuration

### Development (SQLite)

```python
# .env
DATABASE_URL=sqlite+aiosqlite:///./yogaflow.db
```

### Production (PostgreSQL)

Railway automatically sets:
```bash
# Railway environment variable (set automatically)
DATABASE_URL=postgresql://user:password@host:port/yogaflow
```

Backend converts to async format:
```python
# Converted automatically in app/core/database.py
postgresql+asyncpg://user:password@host:port/yogaflow
```

## Schema Compatibility

### SQLAlchemy Models (No Changes Needed)

All models in `backend/app/models/` are database-agnostic:

- `user.py` - User accounts
- `pose.py` - Yoga poses
- `sequence.py` - Pose sequences
- `session.py` - Practice sessions
- `practice_history.py` - User practice history

SQLAlchemy handles dialect differences automatically.

### Data Types Mapping

| SQLite Type | PostgreSQL Type | Notes |
|-------------|-----------------|-------|
| INTEGER | INTEGER | Direct mapping |
| TEXT | VARCHAR/TEXT | Direct mapping |
| REAL | FLOAT | Direct mapping |
| BLOB | BYTEA | For file storage |
| DATETIME | TIMESTAMP | Timezone aware |
| BOOLEAN | BOOLEAN | Native support |
| JSON | JSONB | Better performance |

### Alembic Migrations

All migrations in `backend/alembic/versions/` work with both databases:

```python
# Example: Create users table
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True),
        sa.Column('hashed_password', sa.String(255)),
        # ... more columns
    )
```

SQLAlchemy translates to appropriate SQL for each database.

## Testing Migration

### 1. Test Locally with PostgreSQL

```bash
# Install PostgreSQL locally (macOS)
brew install postgresql@14
brew services start postgresql@14

# Create test database
createdb yogaflow_test

# Update .env for testing
DATABASE_URL=postgresql+asyncpg://localhost/yogaflow_test

# Run migrations
alembic upgrade head

# Test application
uvicorn app.main:app --reload
```

### 2. Verify Schema

```bash
# Connect to local PostgreSQL
psql yogaflow_test

# List tables
\dt

# Describe users table
\d users

# Check data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM poses;
```

Expected tables:
- users
- poses
- sequences
- sequence_poses (junction table)
- practice_sessions
- practice_history
- alembic_version (migration tracking)

### 3. Test Application

```bash
# Run backend tests
cd backend
pytest

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/poses
```

## Railway PostgreSQL Setup

### 1. Add PostgreSQL to Railway Project

**Via Web UI:**
1. Go to Railway project
2. Click "+ New"
3. Select "Database" → "PostgreSQL"
4. Railway creates database instantly

**Via CLI:**
```bash
railway add --database postgres
```

### 2. Verify DATABASE_URL

```bash
# Check environment variables
railway variables | grep DATABASE_URL

# Should show:
# DATABASE_URL=postgresql://postgres:xxxxx@containers-us-west-xxx.railway.app:7432/railway
```

### 3. Connect to Database

**Via Railway Dashboard:**
1. Click on PostgreSQL service
2. Go to "Data" tab
3. Browse tables and data

**Via Railway CLI:**
```bash
# Open PostgreSQL shell
railway connect postgres

# Run SQL commands
SELECT * FROM users;
\dt  # List tables
\q   # Quit
```

**Via psql (local):**
```bash
# Get DATABASE_URL from Railway
railway variables get DATABASE_URL

# Connect with psql
psql "postgresql://user:pass@host:port/railway"
```

## Backup and Recovery

### Automatic Backups (Railway)

Railway automatically backs up PostgreSQL:
- **Frequency:** Daily
- **Retention:** 7 days (free tier), 30 days (paid)
- **Point-in-time recovery:** Available on paid plans

### Manual Backup

```bash
# Backup database
railway db dump > backup_$(date +%Y%m%d).sql

# Restore from backup
railway db restore < backup_20251206.sql
```

### Export Data (JSON)

```bash
# Export all data to JSON
railway run python scripts/export_data.py

# Download from Railway
railway run cat data_export.json > local_backup.json
```

## Rollback Plan

If migration fails:

### 1. Check Logs

```bash
railway logs | grep -i error
railway logs | grep -i alembic
```

### 2. Verify Database State

```bash
railway connect postgres

# Check migration version
SELECT * FROM alembic_version;

# Check table existence
\dt
```

### 3. Downgrade Migration (if needed)

```bash
# Downgrade one version
railway run alembic downgrade -1

# Downgrade to specific version
railway run alembic downgrade <revision_id>

# Downgrade all
railway run alembic downgrade base
```

### 4. Re-run Migration

```bash
# Upgrade to latest
railway run alembic upgrade head
```

### 5. Restore from Backup (last resort)

```bash
# Restore Railway database from backup
railway db restore < backup.sql
```

## Common Migration Issues

### Issue: asyncpg Not Installed

**Error:**
```
ModuleNotFoundError: No module named 'asyncpg'
```

**Fix:**
```bash
# Already in requirements.txt
asyncpg>=0.29.0
```

Verify it's installed:
```bash
railway run pip list | grep asyncpg
```

### Issue: Connection Timeout

**Error:**
```
asyncpg.exceptions.ConnectionTimeoutError
```

**Fix:**
- Check DATABASE_URL is correct
- Verify PostgreSQL service is running
- Check network connectivity

### Issue: Schema Mismatch

**Error:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Fix:**
```bash
# Check current version
railway run alembic current

# Upgrade to head
railway run alembic upgrade head
```

### Issue: Data Type Incompatibility

**Error:**
```
sqlalchemy.exc.DataError: invalid input syntax
```

**Fix:**
- Check Alembic migrations for database-specific code
- Ensure models use SQLAlchemy types (not raw SQL)
- Test migration on local PostgreSQL first

## Performance Optimization

### 1. Connection Pooling

Already configured in `app/core/database.py`:

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,        # Max connections
    max_overflow=10,     # Extra connections during peak
    pool_pre_ping=True,  # Test connections before use
    pool_recycle=3600,   # Recycle after 1 hour
)
```

### 2. Indexing

Add indexes for frequently queried columns:

```python
# In Alembic migration
op.create_index('idx_users_email', 'users', ['email'])
op.create_index('idx_poses_difficulty', 'poses', ['difficulty'])
op.create_index('idx_sessions_user_id', 'practice_sessions', ['user_id'])
```

Already configured in models with `index=True`.

### 3. Query Optimization

Use database-specific features:

```python
# PostgreSQL JSON queries
from sqlalchemy.dialects.postgresql import JSONB

# Use JSONB for metadata
metadata = Column(JSONB)

# Query JSON fields
query = select(Pose).where(Pose.metadata['difficulty'] == 'beginner')
```

## Monitoring

### 1. Railway Metrics

Available in Railway dashboard:
- Connection count
- Query performance
- Database size
- Cache hit ratio

### 2. Application Logging

Backend logs database queries:

```python
# Enable SQL logging in development
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 3. Slow Query Detection

Monitor with Sentry:
```python
# In app/core/monitoring.py
sentry_sdk.init(
    traces_sample_rate=0.1,  # Sample 10% of queries
)
```

## Migration Checklist

### Pre-Migration
- [ ] SQLite database backed up locally
- [ ] Alembic migrations tested
- [ ] PostgreSQL connection tested
- [ ] Data export script tested

### Migration
- [ ] Railway PostgreSQL service created
- [ ] DATABASE_URL environment variable set
- [ ] Backend deployed to Railway
- [ ] Alembic migrations ran successfully
- [ ] Tables created correctly

### Post-Migration
- [ ] All tables exist in PostgreSQL
- [ ] Indexes created correctly
- [ ] Constraints applied
- [ ] Test data imported (if needed)
- [ ] Application connects successfully

### Verification
- [ ] User registration works
- [ ] User login works
- [ ] Poses list displays
- [ ] Sequences load correctly
- [ ] Practice sessions save
- [ ] Data persists between requests
- [ ] No database errors in logs

### Production
- [ ] Automatic backups verified
- [ ] Connection pooling active
- [ ] Performance monitoring active
- [ ] Query optimization applied
- [ ] Documentation updated

---

**Migration Status:** ✅ Automatic (handled by Railway deployment)
**Manual Migration:** Only needed if migrating existing data
**Last Updated:** December 6, 2025
