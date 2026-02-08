"""Expand modules for materials, sales, production, logistics, management.

Revision ID: 20250924_001
Revises:
Create Date: 2025-09-24
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250924_001"
down_revision = None
branch_labels = None
depends_on = None


def _utc_timestamp():
    return sa.func.now()


def upgrade() -> None:
    op.create_table(
        "aluminum_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("series", sa.String(length=64), nullable=False),
        sa.Column("alloy", sa.String(length=64), nullable=False),
        sa.Column("temper", sa.String(length=64), nullable=True),
        sa.Column("weight_per_meter", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("cost_per_meter", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_aluminum_profiles_tenant", "aluminum_profiles", ["tenant_id"])

    op.create_table(
        "accessories",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("unit", sa.String(length=32), nullable=False, server_default="pcs"),
        sa.Column("cost", sa.Numeric(12, 4), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_accessories_tenant", "accessories", ["tenant_id"])
    op.create_index("ix_accessories_sku", "accessories", ["sku"])

    op.create_table(
        "scrap_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("material_id", sa.String(length=36), nullable=True),
        sa.Column("warehouse_id", sa.String(length=36), nullable=True),
        sa.Column("weight_kg", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("cost_recovery", sa.Numeric(12, 4), nullable=True),
        sa.Column("reported_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_scrap_records_tenant", "scrap_records", ["tenant_id"])

    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("payment_terms", sa.String(length=64), nullable=True),
        sa.Column("credit_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("billing_address", sa.Text(), nullable=True),
        sa.Column("shipping_address", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_customers_tenant", "customers", ["tenant_id"])

    op.create_table(
        "price_lists",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=True),
        sa.Column("customer_group", sa.String(length=64), nullable=True),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_price_lists_tenant", "price_lists", ["tenant_id"])

    op.create_table(
        "price_list_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("price_list_id", sa.String(length=36), nullable=False),
        sa.Column("material_id", sa.String(length=36), nullable=True),
        sa.Column("profile_id", sa.String(length=36), nullable=True),
        sa.Column("accessory_id", sa.String(length=36), nullable=True),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=16), nullable=False, server_default="USD"),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_price_list_items_tenant", "price_list_items", ["tenant_id"])
    op.create_index("ix_price_list_items_price_list", "price_list_items", ["price_list_id"])

    op.create_table(
        "delivery_notes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("sales_order_id", sa.String(length=36), nullable=True),
        sa.Column("reference", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_delivery_notes_tenant", "delivery_notes", ["tenant_id"])

    op.create_table(
        "delivery_note_lines",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("delivery_note_id", sa.String(length=36), nullable=False),
        sa.Column("sales_order_line_id", sa.String(length=36), nullable=True),
        sa.Column("material_id", sa.String(length=36), nullable=True),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_delivery_note_lines_tenant", "delivery_note_lines", ["tenant_id"])

    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("reference", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("order_date", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("expected_date", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_purchase_orders_tenant", "purchase_orders", ["tenant_id"])

    op.create_table(
        "purchase_order_lines",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("purchase_order_id", sa.String(length=36), nullable=False),
        sa.Column("material_id", sa.String(length=36), nullable=True),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(length=32), nullable=False, server_default="pcs"),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=True),
        sa.Column("total", sa.Numeric(18, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_purchase_order_lines_tenant", "purchase_order_lines", ["tenant_id"])

    op.add_column("quotes", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("sales_orders", sa.Column("source_quote_id", sa.String(length=36), nullable=True))
    op.add_column("materials", sa.Column("category", sa.String(length=64), nullable=True))
    op.add_column("materials", sa.Column("cost_per_unit", sa.Numeric(12, 4), nullable=True))

    op.create_table(
        "machines",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("capacity_per_hour", sa.Numeric(12, 2), nullable=True),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_machines_tenant", "machines", ["tenant_id"])

    op.create_table(
        "work_orders",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("bom_id", sa.String(length=36), nullable=True),
        sa.Column("reference", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="1"),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_work_orders_tenant", "work_orders", ["tenant_id"])

    op.create_table(
        "work_order_time_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("machine_id", sa.String(length=36), nullable=True),
        sa.Column("started_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_utc_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=_utc_timestamp(), onupdate=_utc_timestamp()),
    )
    op.create_index("ix_work_order_time_entries_tenant", "work_order_time_entries", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("work_order_time_entries")
    op.drop_table("work_orders")
    op.drop_table("machines")
    op.drop_column("sales_orders", "source_quote_id")
    op.drop_column("quotes", "version")
    op.drop_column("materials", "cost_per_unit")
    op.drop_column("materials", "category")
    op.drop_table("purchase_order_lines")
    op.drop_table("purchase_orders")
    op.drop_table("delivery_note_lines")
    op.drop_table("delivery_notes")
    op.drop_table("price_list_items")
    op.drop_table("price_lists")
    op.drop_table("customers")
    op.drop_table("scrap_records")
    op.drop_table("accessories")
    op.drop_table("aluminum_profiles")
