from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from datetime import datetime
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class RFQ(Base, TenantMixin, TimestampMixin):
    __tablename__ = "rfqs"

    id = Column(String(36), primary_key=True)
    reference = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft, sent, quoted
    customer_id = Column(String(36), nullable=True, index=True)
    due_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class RFQLine(Base, TenantMixin, TimestampMixin):
    __tablename__ = "rfq_lines"

    id = Column(String(36), primary_key=True)
    rfq_id = Column(String(36), nullable=False, index=True)
    material_id = Column(String(36), nullable=True, index=True)
    description = Column(String(512), nullable=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=1)
    unit = Column(String(32), nullable=False, default="pcs")
