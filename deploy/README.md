# Deploying Interview Bot

One Ubuntu server runs everything:

```
https://your-domain
 ├── /        → React app (built files, served by Caddy)
 └── /api/... → FastAPI (uvicorn, run by systemd)
```

| File | What it does |
|---|---|
| `setup.sh` | One-time setup: swap, Python, Node 22, Caddy, `.env`, tests, build, services, daily backup |
| `update.sh` | Puts new code live: `git pull`, install, build, restart |
| `build_frontend.sh` | Builds React and copies it to `/var/www/interview-bot` |
| `backup.sh` | Safe SQLite backup to `~/backups` (runs daily, keeps 14 days) |
| `Caddyfile.template` | Web server config: HTTPS, `/api` → backend, React routes |
| `interview-bot.service.template` | Keeps the backend running and restarts it if it crashes |

## First time
```bash
git clone https://github.com/MohammedSaif29/interview-bot.git
cd interview-bot
bash deploy/setup.sh yourname.duckdns.org
```

## After pushing new code
```bash
cd ~/interview-bot && bash deploy/update.sh
```

## Useful commands
```bash
sudo systemctl status interview-bot        # is the backend running?
sudo journalctl -u interview-bot -n 50     # backend logs
sudo journalctl -u caddy -n 50             # web server / HTTPS logs
nano backend/.env && sudo systemctl restart interview-bot   # change a setting
```
