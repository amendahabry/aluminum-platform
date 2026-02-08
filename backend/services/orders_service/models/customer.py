from sqlalchemy import Column, String, Numeric, Boolean, Text
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class Customer(Base, TenantMixin, TimestampMixin):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(64), nullable=True)
    payment_terms = Column(String(64), nullable=True)
    credit_limit = Column(Numeric(14, 2), nullable=True)
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
