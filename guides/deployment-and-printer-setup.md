---
title: "sphotel — Deployment & Printer Setup Guide"
date: "2026-03-19"
---

# sphotel Deployment & Printer Setup Guide

## Part 1: Hetzner VPS + Dokploy Setup

### 1.1 Create Hetzner VPS

1. Go to Hetzner Cloud Console → **New Server**
2. Recommended: **CX22** (2 vCPU, 4 GB RAM) or **CX32** for comfort
3. OS: **Ubuntu 24.04**
4. Add your SSH key
5. Note the server's public IP

### 1.2 Point DNS to Your Server

In your DNS provider, add an A record:

```
A    sphotel.yourdomain.com    →    <hetzner-ip>
```

Wait for propagation before SSL works. Verify with:

```bash
dig sphotel.yourdomain.com
```

### 1.3 Install Dokploy on the VPS

SSH in and run the official installer:

```bash
ssh root@<hetzner-ip>
curl -sSL https://dokploy.com/install.sh | sh
```

Dokploy installs Docker, Docker Compose, and its own management stack.
Access the dashboard at `http://<hetzner-ip>:3000` and complete the admin account setup.

### 1.4 Create the App in Dokploy

1. Dokploy dashboard → **Projects** → **New Project** → name it `sphotel`
2. Inside the project → **New Service** → **Docker Compose**
3. **Source**: Connect your GitHub repo
4. Set:
   - **Compose file**: `docker-compose.yml`
   - **Compose override file**: `docker-compose.prod.yml`
   - **Branch**: `main`

### 1.5 Set Environment Variables

In Dokploy → your service → **Environment** tab, add all of the following (fill in real values):

```env
# Infrastructure
DOMAIN=sphotel.yourdomain.com
ACME_EMAIL=you@yourdomain.com

# Database
DATABASE_URL=postgresql+asyncpg://postgres:STRONG_PASSWORD@db:5432/sphotel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=STRONG_PASSWORD

# Valkey (Redis)
VALKEY_URL=redis://valkey:6379/0

# Application
SECRET_KEY=<generate with: openssl rand -hex 32>
ENVIRONMENT=production
CORS_ORIGINS=https://sphotel.yourdomain.com

# Frontend (build-time)
VITE_API_URL=https://sphotel.yourdomain.com
VITE_WS_URL=wss://sphotel.yourdomain.com

# Optional — leave blank to disable
SENTRY_DSN=
VITE_SENTRY_DSN=
TELEGRAM_BOT_TOKEN=
R2_BUCKET_NAME=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_ENDPOINT_URL=
```

Generate a secure secret key locally:

```bash
openssl rand -hex 32
```

### 1.6 First Deploy

1. Dokploy → service → **Deploy** (triggers first Docker build)
2. Watch logs — wait for all containers to report healthy
3. **Run migrations** — one time only after first deploy:

```bash
ssh root@<hetzner-ip>
docker ps | grep backend          # find the container name
docker exec <backend-container> alembic upgrade head
```

### 1.7 Set Up GitHub Auto-Deploy Webhook

1. Dokploy → your service → **Deployments** → **Webhook** → copy the URL
2. GitHub → repo → **Settings** → **Secrets and variables** → **Actions** → add:
   - Name: `DOKPLOY_WEBHOOK_URL`
   - Value: webhook URL from Dokploy

Every push to `main` now triggers CI (tests + build) and, on success, auto-deploys to Hetzner.

### 1.8 Verify Deployment

```bash
curl https://sphotel.yourdomain.com/api/v1/health
# Expected: {"status": "ok"}
```

Open `https://sphotel.yourdomain.com` — the padlock should be green.
Traefik + Let's Encrypt handle SSL automatically.

---

## Part 2: Windows Restaurant Machine — Printer Setup

### 2.1 Prerequisites

- Windows 10 or 11 on the restaurant counter/POS machine
- Thermal printer connected via USB or LAN/WiFi
- Network access to `https://sphotel.yourdomain.com`

### 2.2 Get the Print Agent Executable

Copy `agent.exe` (built from `print-agent/`) to the Windows machine:

```
C:\sphotel-agent\agent.exe
```

### 2.3 Configure the Agent

Create `C:\sphotel-agent\.env` with your printer settings.

**Network / WiFi thermal printer (most common):**

```env
SPHOTEL_API_URL=https://sphotel.yourdomain.com
PRINTER_TYPE=network
PRINTER_HOST=192.168.1.100       # LAN IP of your printer
PRINTER_PORT=9100
RECEIPT_WIDTH=42                  # 42 = 80mm paper | 32 = 58mm paper
POLL_INTERVAL_SECONDS=3
```

**USB thermal printer:**

```env
SPHOTEL_API_URL=https://sphotel.yourdomain.com
PRINTER_TYPE=usb
USB_VENDOR_ID=0x04b8              # Epson TM-T20 default
USB_PRODUCT_ID=0x0202             # change for your model
RECEIPT_WIDTH=42
POLL_INTERVAL_SECONDS=3
```

> **Finding USB IDs on Windows:** Device Manager → your printer →
> Properties → Details → Hardware IDs → look for `VID_XXXX&PID_XXXX`.

### 2.4 Register the Agent

1. sphotel Admin UI → **Settings** → **Print Agents** → **Generate Token** — copy the one-time token
2. Open **Command Prompt as Administrator** in `C:\sphotel-agent\`:

```cmd
agent.exe --register --token <PASTE_TOKEN_HERE> --name "Counter Printer"
```

Expected output:

```
Agent activated. Key saved to C:\Users\<user>\.sphotel-agent\.agent_key
```

### 2.5 Start the Agent

```cmd
agent.exe
```

Expected output:

```
INFO  WebSocket connected to wss://sphotel.yourdomain.com/ws/print-agent
INFO  Listening for print jobs...
```

### 2.6 Run as a Windows Service (Auto-start on Boot)

Use `launcher.exe` (also in the dist folder), run as Administrator:

```cmd
launcher.exe install
launcher.exe start
```

The agent will now start automatically on every boot without needing a logged-in user.

---

## Part 3: Quick Feature Test Checklist

Run through these in order immediately after deployment.

### Backend Health

```bash
curl https://sphotel.yourdomain.com/api/v1/health
```

- [ ] Returns `{"status": "ok"}` or similar

### Authentication

- [ ] Login page loads at `https://sphotel.yourdomain.com`
- [ ] Login with admin credentials → redirected to dashboard
- [ ] Wrong password → error shown (no crash or blank screen)

### Menu & Orders

- [ ] Menu items load correctly on the POS screen
- [ ] Add items to cart → quantities update
- [ ] Place an order → order appears in kitchen/order view
- [ ] Order status transitions work (pending → in progress → done)

### Printer Connectivity

In Admin UI → **Print Agents**:

- [ ] Agent shows as **Online** (green dot)
- [ ] Agent name matches what you registered (`Counter Printer`)

Send a test receipt:

- [ ] Admin UI → Print Agents → **Send Test Print** → receipt prints
- [ ] Business name, item names, and totals print correctly
- [ ] Paper cuts cleanly (if printer has auto-cutter)

### WebSocket / Real-time

- [ ] Open two browser tabs — place an order in one, see it appear in the other without refreshing
- [ ] Print agent logs show job received within 1–2 seconds of order placement

### HTTPS & SSL

- [ ] `https://` loads with green padlock
- [ ] `http://` auto-redirects to `https://`
- [ ] WebSocket uses `wss://` — confirm in browser DevTools → Network → WS tab

### Auto-Deploy Pipeline

- [ ] Push a small change to `main`
- [ ] GitHub Actions CI runs (tests pass, build succeeds)
- [ ] Dokploy webhook fires → new containers deploy
- [ ] Site is back up within ~2 minutes

---

## Quick Reference

| Item | Details |
|---|---|
| Dokploy dashboard | `http://<hetzner-ip>:3000` |
| App URL | `https://sphotel.yourdomain.com` |
| API docs (Swagger) | `https://sphotel.yourdomain.com/api/docs` |
| Run DB migrations | `docker exec <backend> alembic upgrade head` |
| View backend logs | Dokploy → service → Logs tab |
| Print agent key | `C:\Users\<user>\.sphotel-agent\.agent_key` |
| Regenerate agent token | Admin UI → Settings → Print Agents |
