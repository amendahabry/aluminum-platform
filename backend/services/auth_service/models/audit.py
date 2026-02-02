from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime

from shared.db.session import Base
from shared.db.base import TenantMixin


class AuditLog(Base, TenantMixin):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    action = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(36), nullable=True, index=True)
    details = Column(Text, nullable=True)  # JSON string for DBs without JSONB
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
