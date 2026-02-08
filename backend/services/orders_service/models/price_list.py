from sqlalchemy import Column, String, Numeric, DateTime, Text
from datetime import datetime

from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class PriceList(Base, TenantMixin, TimestampMixin):
    __tablename__ = "price_lists"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    customer_id = Column(String(36), nullable=True, index=True)
    customer_group = Column(String(64), nullable=True, index=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class PriceListItem(Base, TenantMixin, TimestampMixin):
    __tablename__ = "price_list_items"

    id = Column(String(36), primary_key=True)
    price_list_id = Column(String(36), nullable=False, index=True)
    material_id = Column(String(36), nullable=True, index=True)
    profile_id = Column(String(36), nullable=True, index=True)
    accessory_id = Column(String(36), nullable=True, index=True)
    unit_price = Column(Numeric(18, 4), nullable=False, default=0)
    currency = Column(String(16), nullable=False, default="USD")
