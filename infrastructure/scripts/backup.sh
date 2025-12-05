#!/bin/sh
# Database Backup Script for YogaFlow
# Runs automated PostgreSQL backups

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/yogaflow_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup at $(date)"

# Perform backup
pg_dump -Fc -v -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "Backup completed: ${BACKUP_FILE}.gz"

# Remove old backups (older than RETENTION_DAYS)
find "$BACKUP_DIR" -name "yogaflow_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

echo "Old backups cleaned up (retention: ${RETENTION_DAYS} days)"
echo "Backup process completed at $(date)"

# List current backups
echo "Current backups:"
ls -lh "$BACKUP_DIR"/yogaflow_backup_*.sql.gz 2>/dev/null || echo "No backups found"
