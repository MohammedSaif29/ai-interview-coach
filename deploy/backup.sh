#!/usr/bin/env bash
# Safe copy of the SQLite database (works even while the app is running).
# setup.sh schedules this daily. Old backups are deleted after 14 days.
set -euo pipefail
DB="$(cd "$(dirname "$0")/.." && pwd)/backend/interview_bot.db"
DEST="$HOME/backups"
mkdir -p "$DEST"
[ -f "$DB" ] || { echo "No database yet"; exit 0; }
sqlite3 "$DB" ".backup '$DEST/interview_bot-$(date +%F).db'"
find "$DEST" -name 'interview_bot-*.db' -mtime +14 -delete
echo "$(date): backup saved"
