#!/usr/bin/env bash
# One-time setup for a fresh Ubuntu server (e.g. AWS EC2).
# Run from the project folder:   bash deploy/setup.sh yourname.duckdns.org
set -euo pipefail

DOMAIN="${1:?Usage: bash deploy/setup.sh your-domain (e.g. interviewbot.duckdns.org)}"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_AS="$(whoami)"
cd "$APP_DIR"

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }

step "1/8  Adding 2 GB of swap (extra memory for small servers)"
if ! sudo swapon --show | grep -q /swapfile; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile >/dev/null
  sudo swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

step "2/8  Installing Python, SQLite and tools"
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip sqlite3 curl gnupg debian-keyring debian-archive-keyring apt-transport-https

step "3/8  Installing Node.js 22 (Tailwind v4 needs Node 20+)"
if ! command -v node >/dev/null || [ "$(node -v | cut -d. -f1 | tr -d v)" -lt 20 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

step "4/8  Installing Caddy (web server with automatic HTTPS)"
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y caddy
fi

step "5/8  Creating backend/.env (secrets stay on this server only)"
if [ ! -f backend/.env ]; then
  read -rsp "Paste your Groq API key and press Enter (it won't be shown): " GROQ_KEY
  echo
  SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
  umask 077
  cat > backend/.env <<ENV
SECRET_KEY=$SECRET
COOKIE_SECURE=true
FRONTEND_ORIGINS=["https://$DOMAIN"]
GROQ_API_KEY=$GROQ_KEY
ENV
  umask 022
  echo "Created backend/.env with a new random SECRET_KEY."
else
  echo "backend/.env already exists, keeping it."
fi

step "6/8  Backend: virtual environment, packages, tests"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r backend/requirements.txt
(cd backend && ../.venv/bin/python -m pytest -q -p no:cacheprovider | tail -1)

step "7/8  Frontend: building the React app"
bash deploy/build_frontend.sh

step "8/8  Starting the backend service and Caddy"
sed -e "s|__USER__|$RUN_AS|g" -e "s|__APP_DIR__|$APP_DIR|g" deploy/interview-bot.service.template \
  | sudo tee /etc/systemd/system/interview-bot.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now interview-bot
sudo systemctl restart interview-bot

sed -e "s|__DOMAIN__|$DOMAIN|g" deploy/Caddyfile.template | sudo tee /etc/caddy/Caddyfile >/dev/null
sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
sudo systemctl enable caddy
sudo systemctl reload caddy || sudo systemctl restart caddy

# Daily database backup at 2:30 am (server time), keeping the last 14 days
CRON="30 2 * * * bash $APP_DIR/deploy/backup.sh >> $HOME/backup.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'deploy/backup.sh' ; echo "$CRON" ) | crontab -

sleep 2
if curl -fsS http://127.0.0.1:8000/api/health >/dev/null; then
  printf '\n\033[1;32mDone! Open https://%s\033[0m\n' "$DOMAIN"
  echo "The first visit can take a few seconds while Caddy gets the HTTPS certificate."
else
  echo "The backend didn't respond. See what went wrong with:  sudo journalctl -u interview-bot -n 50"
  exit 1
fi
