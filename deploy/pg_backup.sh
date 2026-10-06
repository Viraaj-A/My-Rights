#!/bin/bash
# Daily Postgres backup for myrights (keeps last 7 days)
set -euo pipefail
BACKUP_DIR=/root/backups
mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
OUT="$BACKUP_DIR/raw_data_db-$STAMP.dump"
docker exec myrights-db-1 pg_dump -U myrights -d raw_data_db -Fc --no-owner -f /tmp/backup.dump
docker cp myrights-db-1:/tmp/backup.dump "$OUT"
docker exec myrights-db-1 rm -f /tmp/backup.dump
# prune older than 7 days
find "$BACKUP_DIR" -name 'raw_data_db-*.dump' -mtime +7 -delete
echo "$(date -Is) backup ok: $OUT ($(du -h "$OUT" | cut -f1))"
