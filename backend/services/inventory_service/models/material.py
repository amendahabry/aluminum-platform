from sqlalchemy import Column, String, Numeric, Text, Boolean
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class Material(Base, TenantMixin, TimestampMixin):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True)
    sku = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(32), nullable=False, default="pcs")
    weight_kg = Column(Numeric(12, 4), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    category = Column(String(64), nullable=True)
    cost_per_unit = Column(Numeric(12, 4), nullable=True)
