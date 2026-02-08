from sqlalchemy import Column, String, Numeric, DateTime, Text
from datetime import datetime
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class ScrapRecord(Base, TenantMixin, TimestampMixin):
    __tablename__ = "scrap_records"

    id = Column(String(36), primary_key=True)
    material_id = Column(String(36), nullable=True, index=True)
    warehouse_id = Column(String(36), nullable=True, index=True)
    weight_kg = Column(Numeric(12, 4), nullable=False, default=0)
    reason = Column(String(255), nullable=True)
    cost_recovery = Column(Numeric(12, 4), nullable=True)
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
