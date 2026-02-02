# ERD (Text-Based)

## Auth (auth_service)

- **tenants**: id (PK), name, slug (unique), is_active, settings, created_at, updated_at
- **users**: id (PK), tenant_id (FK), email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at. Unique (tenant_id, email)
- **permissions**: id (PK), tenant_id, code, name, created_at, updated_at
- **roles**: id (PK), tenant_id, name, description, created_at, updated_at
- **role_permissions**: role_id (PK,FK), permission_id (PK,FK)
- **user_roles**: id (PK), tenant_id, user_id (FK), role_id (FK). Unique (tenant_id, user_id, role_id)
- **audit_logs**: id (PK), tenant_id, user_id, action, resource_type, resource_id, details, created_at
- **refresh_tokens**: id (PK), tenant_id, jti (unique), user_id, expires_at, revoked, created_at

## Inventory (inventory_service)

- **materials**: id (PK), tenant_id, sku, name, description, unit, weight_kg, is_active, created_at, updated_at
- **warehouses**: id (PK), tenant_id, name, code, address, created_at, updated_at
- **locations**: id (PK), tenant_id, warehouse_id, name, code, created_at, updated_at
- **stock_lots**: id (PK), tenant_id, material_id, warehouse_id, location_id, quantity, batch_ref, reserved_quantity, created_at, updated_at
- **stock_movements**: id (PK), tenant_id, material_id, warehouse_id, location_id, quantity_delta, movement_type, reference_type, reference_id, created_at
- **reservations**: id (PK), tenant_id, stock_lot_id, quantity, reference_type, reference_id, expires_at, created_at

## Orders (orders_service)

- **rfqs**: id (PK), tenant_id, reference, status, customer_id, due_date, notes, created_at, updated_at
- **rfq_lines**: id (PK), tenant_id, rfq_id, material_id, description, quantity, unit, created_at, updated_at
- **quotes**: id (PK), tenant_id, rfq_id, reference, status, customer_id, valid_until, notes, created_at, updated_at
- **quote_lines**: id (PK), tenant_id, quote_id, material_id, description, quantity, unit, unit_price, total, created_at, updated_at
- **sales_orders**: id (PK), tenant_id, quote_id, reference, status, customer_id, order_date, notes, created_at, updated_at
- **sales_order_lines**: id (PK), tenant_id, sales_order_id, material_id, description, quantity, unit, unit_price, total, created_at, updated_at
- **invoices**: id (PK), tenant_id, sales_order_id, reference, status, customer_id, total_amount, due_date, notes, created_at, updated_at
- **payments**: id (PK), tenant_id, invoice_id, amount, payment_date, method, reference, created_at, updated_at

## Production (stubs; schema can be extended)

- **boms**: id (PK), tenant_id, name, reference, product_id (conceptual)
- **bom_items**: id (PK), tenant_id, bom_id, material_id, quantity, unit
- **work_orders**: id (PK), tenant_id, bom_id, reference, status, quantity, due_date
- **cut_lists**, **cut_plans**: stub entities for cut optimization

## Documents

- **attachments**: id (PK), tenant_id, s3_path, entity_type, entity_id, metadata, created_at (conceptual; implement in a service when needed)

## Indexing

- All tenant-scoped tables: index on (tenant_id).
- Common lookups: email, slug, sku, reference, status, material_id, warehouse_id, etc., as defined in migrations.
