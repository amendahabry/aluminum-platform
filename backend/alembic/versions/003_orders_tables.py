"""Orders tables: rfqs, rfq_lines, quotes, quote_lines, sales_orders, sales_order_lines, invoices, payments

Revision ID: 003
Revises: 002
Create Date: 2025-02-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rfqs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("reference", sa.String(64)),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("customer_id", sa.String(36)),
        sa.Column("due_date", sa.DateTime()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_rfqs_tenant_id", "rfqs", ["tenant_id"])
    op.create_index("ix_rfqs_status", "rfqs", ["status"])

    op.create_table(
        "rfq_lines",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("rfq_id", sa.String(36), nullable=False),
        sa.Column("material_id", sa.String(36)),
        sa.Column("description", sa.String(512)),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(32), nullable=False, server_default="pcs"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_rfq_lines_tenant_id", "rfq_lines", ["tenant_id"])
    op.create_index("ix_rfq_lines_rfq_id", "rfq_lines", ["rfq_id"])

    op.create_table(
        "quotes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("rfq_id", sa.String(36)),
        sa.Column("reference", sa.String(64)),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("customer_id", sa.String(36)),
        sa.Column("valid_until", sa.DateTime()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_quotes_tenant_id", "quotes", ["tenant_id"])
    op.create_index("ix_quotes_status", "quotes", ["status"])

    op.create_table(
        "quote_lines",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("quote_id", sa.String(36), nullable=False),
        sa.Column("material_id", sa.String(36)),
        sa.Column("description", sa.String(512)),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(32), nullable=False, server_default="pcs"),
        sa.Column("unit_price", sa.Numeric(18, 4)),
        sa.Column("total", sa.Numeric(18, 4)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_quote_lines_tenant_id", "quote_lines", ["tenant_id"])
    op.create_index("ix_quote_lines_quote_id", "quote_lines", ["quote_id"])

    op.create_table(
        "sales_orders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("quote_id", sa.String(36)),
        sa.Column("reference", sa.String(64)),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("customer_id", sa.String(36)),
        sa.Column("order_date", sa.DateTime()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sales_orders_tenant_id", "sales_orders", ["tenant_id"])

    op.create_table(
        "sales_order_lines",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("sales_order_id", sa.String(36), nullable=False),
        sa.Column("material_id", sa.String(36)),
        sa.Column("description", sa.String(512)),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(32), nullable=False, server_default="pcs"),
        sa.Column("unit_price", sa.Numeric(18, 4)),
        sa.Column("total", sa.Numeric(18, 4)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sales_order_lines_tenant_id", "sales_order_lines", ["tenant_id"])
    op.create_index("ix_sales_order_lines_sales_order_id", "sales_order_lines", ["sales_order_id"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("sales_order_id", sa.String(36)),
        sa.Column("reference", sa.String(64)),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("customer_id", sa.String(36)),
        sa.Column("total_amount", sa.Numeric(18, 4)),
        sa.Column("due_date", sa.DateTime()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_invoices_tenant_id", "invoices", ["tenant_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("invoice_id", sa.String(36), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("payment_date", sa.DateTime(), nullable=False),
        sa.Column("method", sa.String(32)),
        sa.Column("reference", sa.String(64)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payments_tenant_id", "payments", ["tenant_id"])
    op.create_index("ix_payments_invoice_id", "payments", ["invoice_id"])


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("invoices")
    op.drop_table("sales_order_lines")
    op.drop_table("sales_orders")
    op.drop_table("quote_lines")
    op.drop_table("quotes")
    op.drop_table("rfq_lines")
    op.drop_table("rfqs")
