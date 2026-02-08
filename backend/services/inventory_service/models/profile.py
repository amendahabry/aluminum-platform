from sqlalchemy import Column, String, Numeric, Text, Boolean
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class AluminumProfile(Base, TenantMixin, TimestampMixin):
    __tablename__ = "aluminum_profiles"

    id = Column(String(36), primary_key=True)
    series = Column(String(64), nullable=False, index=True)
    alloy = Column(String(64), nullable=False, index=True)
    temper = Column(String(64), nullable=True, index=True)
    weight_per_meter = Column(Numeric(12, 4), nullable=False, default=0)
    cost_per_meter = Column(Numeric(12, 4), nullable=False, default=0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
