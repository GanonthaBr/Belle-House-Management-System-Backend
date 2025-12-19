#!/bin/bash
# =============================================================================
# Belle House Backend - Database Backup Script
# =============================================================================
# Usage: ./scripts/backup_db.sh
# Cron:  0 2 * * * /path/to/backup_db.sh >> /var/log/bellehouse_backup.log 2>&1

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="bellehouse_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Database credentials
DB_NAME="${POSTGRES_DB:-bellehouse_db}"
DB_USER="${POSTGRES_USER:-bellehouse}"
DB_HOST="${DB_HOST:-db}"

echo "[$(date)] Starting database backup..."

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create backup using docker
docker exec bellehouse_db pg_dump -U "${DB_USER}" "${DB_NAME}" | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Verify backup was created
if [ -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    echo "[$(date)] Backup created: ${BACKUP_FILE} (${SIZE})"
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

# Remove old backups
echo "[$(date)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "bellehouse_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# List current backups
echo "[$(date)] Current backups:"
ls -lh "${BACKUP_DIR}"/bellehouse_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo "[$(date)] Backup completed successfully!"
