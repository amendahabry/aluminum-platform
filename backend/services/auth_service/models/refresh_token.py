from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime

from shared.db.session import Base
from shared.db.base import TenantMixin


class RefreshToken(Base, TenantMixin):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
