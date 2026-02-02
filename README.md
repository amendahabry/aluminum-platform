# Aluminum Management System

Multi-tenant SaaS for Suppliers, Factories, and Customers. Built with Angular (i18n en/he/ar, RTL), FastAPI microservices, Postgres, Redis, MinIO, JWT + RBAC, and Docker Compose.

## Repo structure

- **frontend/** – Angular app (i18n, auth, inventory, RFQ/Quotes, sales orders)
- **backend/** – Python monorepo: shared libs + auth, inventory, orders, production, ai, notification services
- **infra/** – Docker Compose, Dockerfiles, gateway, scripts
- **.github/workflows/** – CI (backend lint/test, frontend build, Docker build)
- **docs/** – architecture, RBAC, ERD, API, local-dev

## Exact commands to run

### 1. Start infrastructure and backend (Docker Compose)

```bash
cd aluminum-platform
docker compose -f infra/docker-compose.yml up -d postgres redis minio
```

Wait for Postgres (e.g. 10 seconds), then run migrations:

```bash
set DATABASE_URL=postgresql://aluminum:aluminum@localhost:5432/aluminum
set PYTHONPATH=backend
cd backend
alembic upgrade head
cd ..
```

Start all backend services and gateway:

```bash
docker compose -f infra/docker-compose.yml up -d auth_service inventory_service orders_service production_service ai_service notification_service gateway
```

(On Linux/macOS use `export` instead of `set` for DATABASE_URL and PYTHONPATH.)

### 2. Run frontend

```bash
cd frontend
npm install
npm start
```

Open **http://localhost:4200**. The dev server proxies `/api` to the gateway at http://localhost:8080.

### Alternative: use dev script (after first migration)

```bash
./infra/dev.sh
# or: make dev
```

Then run frontend separately: `cd frontend && npm install && npm start`.

## Default dev credentials

| Resource   | Credentials                          |
|-----------|--------------------------------------|
| Postgres  | User: `aluminum`, Password: `aluminum`, DB: `aluminum`, Port: 5432 |
| Redis     | Port 6379, no auth                   |
| MinIO     | User: `minioadmin`, Password: `minioadmin`, Port: 9000 (console 9001) |
| JWT secret| Default: `change-me-in-production-use-long-secret` (set `JWT_SECRET_KEY` in production) |

## How to create a tenant and first admin user

1. Open **http://localhost:4200/register-tenant** (or call `POST http://localhost:8080/auth/register-tenant` with JSON body).
2. Fill the form:
   - **Organization name**: e.g. `Acme Aluminum`
   - **Tenant slug**: e.g. `acme` (used later in login)
   - **Admin email**: e.g. `admin@acme.com`
   - **Admin password**: choose a password
   - **Full name**: optional
3. Submit. On success you’ll see a message; go to **http://localhost:4200/login**.
4. Log in with:
   - **Tenant slug**: `acme`
   - **Email**: `admin@acme.com`
   - **Password**: the one you set

The first user has the **admin** role and full permissions (`admin:*`).

## Ports

| Service     | Port |
|------------|------|
| Gateway    | 8080 |
| Auth       | 8000 |
| Inventory  | 8001 |
| Orders     | 8002 |
| Production | 8003 |
| AI         | 8004 |
| Notification | 8005 |
| Frontend   | 4200 |
| Postgres   | 5432 |
| Redis      | 6379 |
| MinIO      | 9000, 9001 |

## Docs

- **docs/architecture.md** – High-level architecture and multi-tenancy
- **docs/rbac.md** – Permission matrix and roles
- **docs/erd.md** – Text-based ERD
- **docs/api.md** – Service endpoints and auth flow
- **docs/local-dev.md** – Local development and env setup

## License

Proprietary / internal use.
