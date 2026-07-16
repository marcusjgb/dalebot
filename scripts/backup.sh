#!/bin/bash
set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="dalebot_backup_${DATE}"
mkdir -p "$BACKUP_DIR"

echo "Starting backup: $BACKUP_NAME"

echo "Backing up PostgreSQL..."
pg_dump -h "${POSTGRES_HOST:-localhost}" \
        -U "${POSTGRES_USER:-appointments}" \
        -d "${POSTGRES_DB:-appointments}" \
        -F c \
        -f "${BACKUP_DIR}/${BACKUP_NAME}.psql.dump"

echo "Backing up Redis..."
redis-cli -h "${REDIS_HOST:-localhost}" \
          SAVE

cp ${REDIS_DATA_DIR:-/var/lib/redis}/appendonly.aof \
   "${BACKUP_DIR}/${BACKUP_NAME}.redis.aof" 2>/dev/null || true

echo "Creating archive..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}.psql.dump" "${BACKUP_NAME}.redis.aof" 2>/dev/null || true
rm -rf "${BACKUP_NAME}.psql.dump" "${BACKUP_NAME}.redis.aof"

echo "Backup complete: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

echo "Removing backups older than 30 days..."
find "$BACKUP_DIR" -name "dalebot_backup_*" -mtime +30 -delete

echo "Done!"
