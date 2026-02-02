# RBAC – Permission Matrix

## Roles

| Role     | Description                |
|----------|----------------------------|
| admin    | Full access within tenant |
| supplier | Inventory + orders + production + AI + notifications |
| factory  | Read inventory/orders; approve quotes; production + AI + notifications |
| customer | Read inventory; RFQ/quotes/sales/invoices read; notifications |
| viewer   | Read-only on inventory, orders, production, notifications |

## Permissions (code)

- `admin:*` – all actions (admin role only).
- `auth:users:read`, `auth:users:write` – user CRUD.
- `auth:roles:read`, `auth:roles:write` – roles and permissions.
- `inventory:materials:read`, `inventory:materials:write` – materials CRUD.
- `inventory:warehouses:read`, `inventory:warehouses:write` – warehouses CRUD.
- `inventory:stock:read`, `inventory:stock:write` – stock and movements.
- `orders:rfq:read`, `orders:rfq:write` – RFQ CRUD.
- `orders:quotes:read`, `orders:quotes:write`, `orders:quotes:approve` – quotes and approval.
- `orders:sales:read`, `orders:sales:write` – sales orders.
- `orders:invoices:read`, `orders:invoices:write` – invoices.
- `production:boms:read`, `production:boms:write` – BOM.
- `production:work-orders:read`, `production:work-orders:write` – work orders.
- `production:cutlists:read`, `production:cutlists:write` – cut list generation.
- `ai:use` – AI endpoints (cut-optimize, quote-assistant, OCR, NLQ).
- `notifications:read`, `notifications:write` – notification logs and send.

## Role → Permissions (default)

- **admin**: `admin:*`
- **supplier**: inventory (all), orders (all), production (all), ai:use, notifications (all).
- **factory**: inventory read + stock write; orders read + quotes:approve; production (all); ai:use; notifications (all).
- **customer**: inventory:materials:read; orders rfq/quotes/sales/invoices read + rfq write; notifications (all).
- **viewer**: read-only for inventory, orders, production, notifications (no write, no approve).

## Enforcement

- JWT payload includes `permissions: string[]` and `roles: string[]`.
- FastAPI dependency `require_permission("code")` checks permission (or `admin:*`).
- Tenant is always taken from JWT; no cross-tenant access.
