# Uptime Kuma Setup Guide

Uptime Kuma is deployed via `infra/docker-compose.monitoring.yml` and provides health monitoring with Telegram alerts.

## Start the monitoring stack

```bash
docker compose -f docker-compose.yml -f infra/docker-compose.monitoring.yml up -d
```

Access Uptime Kuma at `http://localhost:3001` (dev) or `https://your-domain:3001` (prod, behind Traefik).

## Initial setup (one-time)

1. **Create admin account** — set username and password on first visit.

2. **Add Telegram notification:**
   - Go to Settings → Notifications → Add Notification
   - Type: Telegram
   - Friendly Name: `sphotel-alerts`
   - Bot Token: value from `TELEGRAM_BOT_TOKEN` env var
   - Chat ID: your Telegram group chat ID
   - Click Save and Test

3. **Add health monitor:**
   - Click "Add New Monitor"
   - Monitor Type: HTTP(S)
   - Friendly Name: `sphotel-api`
   - URL: `https://yourdomain.com/api/v1/health` (or `http://backend:8000/api/v1/health` inside Docker network)
   - Heartbeat Interval: 60 seconds
   - Retries: 2
   - Notification: select `sphotel-alerts`
   - Click Save

4. **Verify the monitor** shows green within 60 seconds.

## Expected health response

`GET /api/v1/health` returns HTTP 200:
```json
{ "data": { "status": "ok", "version": "0.1.0" }, "error": null }
```

## Alerts triggered on

- Monitor goes down (HTTP non-200 or timeout)
- Monitor recovers (back online)
