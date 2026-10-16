#!/usr/bin/env bash
# Put new code live: push from your Mac first, then on the server run:  bash deploy/update.sh
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only
.venv/bin/pip install --quiet -r backend/requirements.txt
bash deploy/build_frontend.sh
sudo systemctl restart interview-bot
sleep 2
curl -fsS http://127.0.0.1:8000/api/health >/dev/null && echo "Updated and running ✅" \
  || { echo "Backend not responding. Check:  sudo journalctl -u interview-bot -n 50"; exit 1; }
