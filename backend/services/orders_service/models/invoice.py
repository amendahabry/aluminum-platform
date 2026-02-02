from sqlalchemy import Column, String, Numeric, DateTime, Text
from datetime import datetime
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class Invoice(Base, TenantMixin, TimestampMixin):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True)
    sales_order_id = Column(String(36), nullable=True, index=True)
    reference = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft, sent, paid, overdue
    customer_id = Column(String(36), nullable=True, index=True)
    total_amount = Column(Numeric(18, 4), nullable=True)
    due_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class Payment(Base, TenantMixin, TimestampMixin):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True)
    invoice_id = Column(String(36), nullable=False, index=True)
    amount = Column(Numeric(18, 4), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    method = Column(String(32), nullable=True)  # bank, card, cash
    reference = Column(String(64), nullable=True)
