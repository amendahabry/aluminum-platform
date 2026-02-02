#!/usr/bin/env bash
# Start all services locally via Docker Compose.
# Usage: ./infra/dev.sh   or   make dev

set -e
cd "$(dirname "$0")/.."

echo "Starting Postgres, Redis, MinIO, and all backend services..."
docker compose -f infra/docker-compose.yml up -d postgres redis minio

echo "Waiting for Postgres..."
until docker compose -f infra/docker-compose.yml exec -T postgres pg_isready -U aluminum 2>/dev/null; do
  sleep 2
done

echo "Running migrations..."
export DATABASE_URL=postgresql://aluminum:aluminum@localhost:5432/aluminum
export PYTHONPATH=backend
cd backend
alembic upgrade head
cd ..

echo "Starting backend services and gateway..."
docker compose -f infra/docker-compose.yml up -d auth_service inventory_service orders_service production_service ai_service notification_service gateway

echo "Done. Gateway: http://localhost:8080"
echo "Auth: http://localhost:8000, Inventory: 8001, Orders: 8002, Production: 8003, AI: 8004, Notifications: 8005"
echo "To run frontend: cd frontend && npm install && npm start  (then open http://localhost:4200)"
