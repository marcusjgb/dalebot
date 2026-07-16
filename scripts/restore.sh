#!/bin/bash
set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 ./backups/dalebot_backup_20260716_120000.tar.gz"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

BACKUP_DIR=$(mktemp -d)
trap "rm -rf $BACKUP_DIR" EXIT

echo "Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$BACKUP_DIR"

DUMP_FILE=$(ls ${BACKUP_DIR}/*.psql.dump 2>/dev/null | head -1)
REDIS_FILE=$(ls ${BACKUP_DIR}/*.redis.aof 2>/dev/null | head -1)

echo "Stopping services..."
docker compose stop worker beat

echo "Restoring PostgreSQL..."
pg_restore -h "${POSTGRES_HOST:-localhost}" \
           -U "${POSTGRES_USER:-appointments}" \
           -d "${POSTGRES_DB:-appointments}" \
           --clean \
           --if-exists \
           "$DUMP_FILE"

if [ -n "$REDIS_FILE" ]; then
    echo "Restoring Redis..."
    redis-cli -h "${REDIS_HOST:-localhost}" FLUSHALL
    cat "$REDIS_FILE" | redis-cli -h "${REDIS_HOST:-localhost}" --pipe
fi

echo "Starting services..."
docker compose start worker beat

echo "Restore complete!"
