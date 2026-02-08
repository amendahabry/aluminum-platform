from sqlalchemy import Column, String, Numeric, DateTime, Text, Boolean
from datetime import datetime

from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class Machine(Base, TenantMixin, TimestampMixin):
    __tablename__ = "machines"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    capacity_per_hour = Column(Numeric(12, 2), nullable=True)
    constraints = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)


class WorkOrder(Base, TenantMixin, TimestampMixin):
    __tablename__ = "work_orders"

    id = Column(String(36), primary_key=True)
    bom_id = Column(String(36), nullable=True, index=True)
    reference = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="draft", index=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=1)
    due_date = Column(DateTime, nullable=True)


class WorkOrderTimeEntry(Base, TenantMixin, TimestampMixin):
    __tablename__ = "work_order_time_entries"

    id = Column(String(36), primary_key=True)
    work_order_id = Column(String(36), nullable=False, index=True)
    machine_id = Column(String(36), nullable=True, index=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
