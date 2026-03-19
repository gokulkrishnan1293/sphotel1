# sphotel

Restaurant POS system — monorepo with FastAPI backend, React+Vite frontend, PostgreSQL, and Valkey.

## Prerequisites

| Tool | Version |
|---|---|
| Docker | 24+ |
| pnpm | 9+ |
| GNU Make | any |
| Python | 3.12+ (for local print-agent work only) |

## Quick Start

```sh
cp .env.example .env.local
make dev
```

## Make Commands

| Command | Description |
|---|---|
| `make dev` | Start all services with hot reload (Docker Compose) |
| `make test-backend` | Run mypy + ruff + pytest in backend |
| `make test-frontend` | Run tsc + eslint + vitest in frontend |
| `make migrate` | Run Alembic migrations against the DB |
| `make build-agent` | Build print-agent Windows executable |

## Service URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/v1/docs |
| PostgreSQL | localhost:5432 |
| Valkey | localhost:6379 |

## Project Structure

```
sphotel/
├── backend/          FastAPI + SQLAlchemy + Alembic
├── frontend/         React 18 + Vite + Tailwind CSS v4
├── print-agent/      Python Windows print agent
├── infra/            Docker, CI, deployment configs
└── Makefile          All developer commands
```

## Environment

Copy `.env.example` to `.env.local` and fill in values for your environment.
Never commit `.env` or `.env.local` — they are gitignored.

## Production Deployment

Production runs on Hetzner VPS via [Dokploy](https://dokploy.com) (self-hosted PaaS). Traefik handles SSL (Let's Encrypt) and reverse proxying.

### First-time setup

1. Provision a Hetzner VPS (CX31 recommended) and install Dokploy
2. In Dokploy dashboard, create a "Docker Compose" application pointing to this repo
3. Set `composeFile: docker-compose.prod.yml` (no override file needed)
4. Configure all environment variables from `.env.example` in the Dokploy env panel — set `ENVIRONMENT=production`, `CORS_ORIGINS=https://<DOMAIN>`, `VITE_API_URL=https://<DOMAIN>`, `VITE_WS_URL=wss://<DOMAIN>`
5. Generate a Dokploy webhook URL and save it as GitHub repository secret `DOKPLOY_WEBHOOK_URL`
6. Deploy once manually from Dokploy, then run migrations: `docker compose exec backend alembic upgrade head`

### CI/CD

Every push to `main` triggers `.github/workflows/deploy.yml`:
- Runs `make test-backend` and `make test-frontend` in parallel
- Verifies backend and frontend Docker images build successfully
- On all checks passing, calls the Dokploy webhook to redeploy

PRs run `.github/workflows/ci-backend.yml` and `.github/workflows/ci-frontend.yml` for fast feedback without deploying.

### Required GitHub secrets

| Secret | Description |
|---|---|
| `DOKPLOY_WEBHOOK_URL` | Webhook URL from Dokploy dashboard to trigger redeploy |
