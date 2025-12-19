#!/bin/bash
# =============================================================================
# Belle House Backend - Database Restore Script
# =============================================================================
# Usage: ./scripts/restore_db.sh backup_file.sql.gz

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo "Available backups:"
    ls -lh backups/bellehouse_backup_*.sql.gz 2>/dev/null || echo "No backups found in backups/"
    exit 1
fi

BACKUP_FILE="$1"

# Check if file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_NAME="${POSTGRES_DB:-bellehouse_db}"
DB_USER="${POSTGRES_USER:-bellehouse}"

echo "WARNING: This will replace all data in database '${DB_NAME}'!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "[$(date)] Starting database restore from ${BACKUP_FILE}..."

# Stop web container to prevent writes during restore
echo "[$(date)] Stopping web container..."
docker-compose stop web

# Drop and recreate database
echo "[$(date)] Recreating database..."
docker exec bellehouse_db psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${DB_NAME};"
docker exec bellehouse_db psql -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};"

# Restore from backup
echo "[$(date)] Restoring data..."
gunzip -c "${BACKUP_FILE}" | docker exec -i bellehouse_db psql -U "${DB_USER}" "${DB_NAME}"

# Start web container
echo "[$(date)] Starting web container..."
docker-compose start web

# Run migrations (in case there are new ones)
echo "[$(date)] Running migrations..."
docker-compose exec web python manage.py migrate --noinput

echo "[$(date)] Restore completed successfully!"
