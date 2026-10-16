#!/usr/bin/env bash
# Builds the React app and copies it to /var/www, where Caddy serves it from.
# (Caddy can't read inside /home/ubuntu, which is private on Ubuntu.)
set -euo pipefail
cd "$(dirname "$0")/../frontend"
npm ci --no-audit --no-fund
npm run build
sudo mkdir -p /var/www/interview-bot
sudo rm -rf /var/www/interview-bot/*
sudo cp -r dist/. /var/www/interview-bot/
