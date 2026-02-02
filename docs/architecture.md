# Aluminum Management System – Architecture

## Overview

Multi-tenant SaaS for suppliers, factories, and customers in the aluminum supply chain. Built as microservices with shared PostgreSQL (tenant_id isolation), Redis, MinIO, and an API Gateway.

## High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────────────────────────────────────────────┐
│   Angular   │────▶│ API Gateway │────▶│ Auth │ Inventory │ Orders │ Production │ AI │ Notify     │
│   Frontend  │     │  (FastAPI)  │     │ 8000 │    8001    │  8002  │    8003     │8004│   8005     │
└─────────────┘     └──────┬───────┘     └──────┴─────┬─────┴────┬───┴─────┬───────┴────┴─────┬──────┘
                          │                           │         │         │                  │
                          ▼                           ▼         ▼         ▼                  ▼
                    ┌──────────┐               ┌──────────┐  Redis   MinIO (S3)
                    │ Postgres │               │  Redis   │  (queue/cache)
                    │ (shared) │               └──────────┘
                    └──────────┘
```

## Multi-Tenancy

- **Strategy**: Row-level isolation via `tenant_id` on all tenant-scoped tables.
- **Enforcement**: JWT carries `tenant_id`; middleware sets tenant context; all queries filter by `tenant_id`.
- **Shared schema**: Single database, one schema; no schema-per-tenant.

## Services

| Service              | Port | Responsibility                                      |
|---------------------|------|-----------------------------------------------------|
| **auth_service**    | 8000 | Tenants, users, roles, permissions, JWT, refresh   |
| **inventory_service** | 8001 | Materials, warehouses, stock, movements            |
| **orders_service** | 8002 | RFQ, quotes, sales orders, invoices                |
| **production_service** | 8003 | BOM, cut list (stub), work orders (stub)       |
| **ai_service**      | 8004 | Cut optimize, quote assistant, OCR, NLQ (stubs)    |
| **notification_service** | 8005 | Email/WhatsApp queue (stub), delivery logs   |
| **gateway**         | 8080 | Reverse proxy to services, single entry for frontend |

## Cross-Cutting

- **Auth**: JWT access + refresh; Bearer on requests; RBAC via permissions in token.
- **Logging**: Structured logs with request ID; optional JSON.
- **Health**: `/health` and `/ready` per service; gateway forwards or aggregates as needed.
- **Security**: Input validation (Pydantic), rate limiting (optional), audit logs (auth_service AuditLog).

## Data Flow

1. User logs in via gateway → `/auth/login` → auth_service returns access + refresh tokens.
2. Frontend stores tokens; attaches access token to all API requests (interceptor).
3. Gateway forwards request to appropriate service with same headers.
4. Each service validates JWT, sets tenant from token, and enforces RBAC on routes.

## Deployment (Local)

- **Docker Compose**: Postgres, Redis, MinIO, all backend services, gateway.
- **Frontend**: `ng serve` with proxy to gateway, or built and served via nginx (optional in compose).
- **Migrations**: Run once after Postgres is up: `cd backend && PYTHONPATH=. DATABASE_URL=... alembic upgrade head`.
