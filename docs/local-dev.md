# Local Development

## Prerequisites

- Docker and Docker Compose
- Node 20+ (for frontend)
- Python 3.11+ (for backend migrations and optional local run)

## Quick Start (Docker Compose)

1. **Start infrastructure and backend**

   ```bash
   cd /path/to/aluminum-platform
   docker compose -f infra/docker-compose.yml up -d postgres redis minio
   ```

2. **Run migrations**

   ```bash
   export DATABASE_URL=postgresql://aluminum:aluminum@localhost:5432/aluminum
   export PYTHONPATH=backend
   cd backend
   alembic upgrade head
   cd ..
   ```

3. **Start all backend services and gateway**

   ```bash
   docker compose -f infra/docker-compose.yml up -d auth_service inventory_service orders_service production_service ai_service notification_service gateway
   ```

4. **Frontend (separate terminal)**

   ```bash
   cd frontend
   npm install
   npm start
   ```

   Open http://localhost:4200. The Angular dev server proxies `/api` to the gateway at http://localhost:8080.

## Using `make` or `dev.sh`

- **Make**: From repo root run `make dev` (runs `./infra/dev.sh`).
- **Script**: `./infra/dev.sh` starts Postgres, Redis, MinIO, runs migrations, then starts backend services and gateway. Run frontend separately with `cd frontend && npm install && npm start`.

## Default Dev Credentials

- **Postgres**: `aluminum` / `aluminum`, database `aluminum`, port 5432.
- **Redis**: port 6379, no auth.
- **MinIO**: `minioadmin` / `minioadmin`, port 9000 (console 9001).
- **JWT**: Default secret is `change-me-in-production-use-long-secret`; set `JWT_SECRET_KEY` in production.

## Create Tenant and First Admin User

1. Open http://localhost:4200/register-tenant (or call `POST http://localhost:8080/auth/register-tenant`).
2. Submit:
   - Organization name: e.g. **Acme Aluminum**
   - Tenant slug: e.g. **acme** (used in login)
   - Admin email: e.g. **admin@acme.com**
   - Admin password: (choose a password)
   - Full name: (optional)
3. After success, go to http://localhost:4200/login.
4. Login with:
   - Tenant slug: **acme**
   - Email: **admin@acme.com**
   - Password: (the one you set)

The first user has the **admin** role and `admin:*` permission.

## Ports

| Service              | Port |
|----------------------|------|
| Gateway              | 8080 |
| Auth                 | 8000 |
| Inventory            | 8001 |
| Orders               | 8002 |
| Production           | 8003 |
| AI                   | 8004 |
| Notification         | 8005 |
| Frontend (ng serve)  | 4200 |
| Postgres             | 5432 |
| Redis                | 6379 |
| MinIO API / Console  | 9000 / 9001 |

## Environment

- Copy `.env.example` to `.env` and set `JWT_SECRET_KEY`, `DATABASE_URL`, etc., if needed.
- For Docker, variables can be set in `infra/docker-compose.yml` or via `.env` in the repo root.
