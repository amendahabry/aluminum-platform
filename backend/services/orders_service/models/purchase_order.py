from sqlalchemy import Column, String, Numeric, DateTime, Text
from datetime import datetime

from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class PurchaseOrder(Base, TenantMixin, TimestampMixin):
    __tablename__ = "purchase_orders"

    id = Column(String(36), primary_key=True)
    supplier_name = Column(String(255), nullable=False, index=True)
    reference = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="draft", index=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class PurchaseOrderLine(Base, TenantMixin, TimestampMixin):
    __tablename__ = "purchase_order_lines"

    id = Column(String(36), primary_key=True)
    purchase_order_id = Column(String(36), nullable=False, index=True)
    material_id = Column(String(36), nullable=True, index=True)
    description = Column(String(512), nullable=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=0)
    unit = Column(String(32), nullable=False, default="pcs")
    unit_price = Column(Numeric(18, 4), nullable=True)
    total = Column(Numeric(18, 4), nullable=True)
