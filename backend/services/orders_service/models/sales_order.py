from sqlalchemy import Column, String, Numeric, DateTime, Text
from datetime import datetime
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class SalesOrder(Base, TenantMixin, TimestampMixin):
    __tablename__ = "sales_orders"

    id = Column(String(36), primary_key=True)
    quote_id = Column(String(36), nullable=True, index=True)
    reference = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft, confirmed, shipped, closed
    customer_id = Column(String(36), nullable=True, index=True)
    order_date = Column(DateTime, nullable=True)
    source_quote_id = Column(String(36), nullable=True, index=True)
    notes = Column(Text, nullable=True)


class SalesOrderLine(Base, TenantMixin, TimestampMixin):
    __tablename__ = "sales_order_lines"

    id = Column(String(36), primary_key=True)
    sales_order_id = Column(String(36), nullable=False, index=True)
    material_id = Column(String(36), nullable=True, index=True)
    description = Column(String(512), nullable=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=1)
    unit = Column(String(32), nullable=False, default="pcs")
    unit_price = Column(Numeric(18, 4), nullable=True)
    total = Column(Numeric(18, 4), nullable=True)
