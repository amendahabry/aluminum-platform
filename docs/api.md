# API – Service Endpoints and Auth Flow

## Base URL

- **Local**: Gateway `http://localhost:8080`. Frontend proxies `/api` → gateway (path rewritten to root).
- **Services direct**: auth 8000, inventory 8001, orders 8002, production 8003, ai 8004, notification 8005.

## Auth Flow

1. **Register tenant**  
   `POST /auth/register-tenant`  
   Body: `{ name, slug, admin_email, admin_password, admin_full_name? }`  
   Response: `{ tenant_id, user_id, message }`

2. **Login**  
   `POST /auth/login`  
   Body: `{ email, password, tenant_slug? }`  
   Response: `{ access_token, refresh_token, token_type: "bearer", expires_in }`

3. **Refresh**  
   `POST /auth/refresh`  
   Body: `{ refresh_token }`  
   Response: same as login.

4. **Me**  
   `GET /auth/me`  
   Headers: `Authorization: Bearer <access_token>`  
   Response: `{ id, email, full_name, tenant_id, tenant_name, roles, permissions, is_active }`

## Auth Service

- `POST /auth/register-tenant`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`
- `GET|POST|PATCH|DELETE /users`, `GET|POST|PATCH|DELETE /users/:id`
- `GET /roles/permissions`, `GET|POST|PATCH|DELETE /roles`, `GET|POST|PATCH|DELETE /roles/:id`, `POST /roles/:id/permissions`
- `GET /tenants`, `GET /tenants/:id` (tenant-scoped: only own tenant)

## Inventory Service

- `GET|POST|PATCH|DELETE /materials`, `GET|PATCH|DELETE /materials/:id`
- `GET|POST|PATCH|DELETE /warehouses`, `GET|PATCH|DELETE /warehouses/:id`
- `POST /stock/move` (body: material_id, warehouse_id, quantity_delta, movement_type, …), `GET /stock/summary`

## Orders Service

- `GET|POST|PATCH|DELETE /rfqs`, `GET|PATCH|DELETE /rfqs/:id`
- `GET|POST|PATCH|DELETE /quotes`, `GET|PATCH|DELETE /quotes/:id`, `POST /quotes/:id/approve`
- `GET|POST|PATCH|DELETE /sales-orders`, `GET|PATCH|DELETE /sales-orders/:id`
- `GET|POST|PATCH|DELETE /invoices`, `GET|PATCH|DELETE /invoices/:id`

## Production Service (stubs)

- `GET|POST|PATCH|DELETE /boms`, `GET|PATCH|DELETE /boms/:id`
- `POST /cutlists/generate` (body: bom_id, stock_length_mm, kerf_mm, optimize)
- `GET|POST|PATCH|DELETE /work-orders`, `GET|PATCH|DELETE /work-orders/:id`

## AI Service (stubs)

- `POST /ai/cut-optimize`
- `POST /ai/quote-assistant`
- `POST /ai/ocr/invoice` (file upload)
- `POST /ai/nlq`

## Notification Service

- `POST /notify/email`, `POST /notify/whatsapp`
- `GET /notify/logs`

## Gateway

All above paths are proxied at the same path (e.g. `GET /auth/me`, `GET /materials`, `POST /quotes`). Frontend uses `/api` prefix; proxy strips `/api` and forwards to gateway.

## Headers

- `Authorization: Bearer <access_token>` for protected routes.
- `X-Request-ID` optional; gateway and services set/forward it.

## Errors

- 401: Missing or invalid token; 403: Forbidden (permission or tenant); 404: Not found; 422: Validation error.
