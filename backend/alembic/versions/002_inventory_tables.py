"""Inventory tables: materials, warehouses, locations, stock_lots, stock_movements, reservations

Revision ID: 002
Revises: 001
Create Date: 2025-02-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "materials",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("sku", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("unit", sa.String(32), nullable=False, server_default="pcs"),
        sa.Column("weight_kg", sa.Numeric(12, 4)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_materials_tenant_id", "materials", ["tenant_id"])
    op.create_index("ix_materials_sku", "materials", ["sku"])

    op.create_table(
        "warehouses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(64)),
        sa.Column("address", sa.String(512)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_warehouses_tenant_id", "warehouses", ["tenant_id"])

    op.create_table(
        "locations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("warehouse_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("code", sa.String(64)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_locations_tenant_id", "locations", ["tenant_id"])
    op.create_index("ix_locations_warehouse_id", "locations", ["warehouse_id"])

    op.create_table(
        "stock_lots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("material_id", sa.String(36), nullable=False),
        sa.Column("warehouse_id", sa.String(36), nullable=False),
        sa.Column("location_id", sa.String(36)),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("batch_ref", sa.String(64)),
        sa.Column("reserved_quantity", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_stock_lots_tenant_id", "stock_lots", ["tenant_id"])
    op.create_index("ix_stock_lots_material_id", "stock_lots", ["material_id"])
    op.create_index("ix_stock_lots_warehouse_id", "stock_lots", ["warehouse_id"])

    op.create_table(
        "stock_movements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("material_id", sa.String(36), nullable=False),
        sa.Column("warehouse_id", sa.String(36), nullable=False),
        sa.Column("location_id", sa.String(36)),
        sa.Column("quantity_delta", sa.Numeric(18, 4), nullable=False),
        sa.Column("movement_type", sa.String(32), nullable=False),
        sa.Column("reference_type", sa.String(64)),
        sa.Column("reference_id", sa.String(36)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_stock_movements_tenant_id", "stock_movements", ["tenant_id"])
    op.create_index("ix_stock_movements_material_id", "stock_movements", ["material_id"])

    op.create_table(
        "reservations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("stock_lot_id", sa.String(36), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("reference_type", sa.String(64)),
        sa.Column("reference_id", sa.String(36)),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_reservations_tenant_id", "reservations", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("reservations")
    op.drop_table("stock_movements")
    op.drop_table("stock_lots")
    op.drop_table("locations")
    op.drop_table("warehouses")
    op.drop_table("materials")
