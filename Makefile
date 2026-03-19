.PHONY: dev test-backend test-frontend migrate build-agent

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

test-backend:
	cd backend && mypy app --strict && ruff check app && pytest

test-frontend:
	cd frontend && pnpm tsc --noEmit && pnpm lint && pnpm test

migrate:
	cd backend && alembic upgrade head

build-agent:
	cd print-agent && python build.py
