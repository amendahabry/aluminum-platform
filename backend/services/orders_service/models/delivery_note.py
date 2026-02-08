from sqlalchemy import Column, String, DateTime, Text, Numeric
from datetime import datetime

from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class DeliveryNote(Base, TenantMixin, TimestampMixin):
    __tablename__ = "delivery_notes"

    id = Column(String(36), primary_key=True)
    sales_order_id = Column(String(36), nullable=True, index=True)
    reference = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="draft", index=True)
    delivered_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class DeliveryNoteLine(Base, TenantMixin, TimestampMixin):
    __tablename__ = "delivery_note_lines"

    id = Column(String(36), primary_key=True)
    delivery_note_id = Column(String(36), nullable=False, index=True)
    sales_order_line_id = Column(String(36), nullable=True, index=True)
    material_id = Column(String(36), nullable=True, index=True)
    description = Column(String(512), nullable=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=0)
