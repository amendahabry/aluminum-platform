from sqlalchemy import Column, String, Numeric, DateTime, Text, Integer
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class Quote(Base, TenantMixin, TimestampMixin):
    __tablename__ = "quotes"

    id = Column(String(36), primary_key=True)
    rfq_id = Column(String(36), nullable=True, index=True)
    reference = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft, sent, approved, rejected
    version = Column(Integer, nullable=False, default=1)
    customer_id = Column(String(36), nullable=True, index=True)
    valid_until = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class QuoteLine(Base, TenantMixin, TimestampMixin):
    __tablename__ = "quote_lines"

    id = Column(String(36), primary_key=True)
    quote_id = Column(String(36), nullable=False, index=True)
    material_id = Column(String(36), nullable=True, index=True)
    description = Column(String(512), nullable=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=1)
    unit = Column(String(32), nullable=False, default="pcs")
    unit_price = Column(Numeric(18, 4), nullable=True)
    total = Column(Numeric(18, 4), nullable=True)
