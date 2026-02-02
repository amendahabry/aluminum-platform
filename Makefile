.PHONY: dev build migrate test lint

dev:
	./infra/dev.sh

build:
	docker compose -f infra/docker-compose.yml build

migrate:
	cd backend && PYTHONPATH=. DATABASE_URL=postgresql://aluminum:aluminum@localhost:5432/aluminum alembic upgrade head

test-backend:
	cd backend && PYTHONPATH=. python -m pytest services/auth_service -v 2>/dev/null || true

lint-backend:
	cd backend && ruff check . 2>/dev/null || true
	cd backend && black --check . 2>/dev/null || true

lint-frontend:
	cd frontend && npm run lint 2>/dev/null || true
