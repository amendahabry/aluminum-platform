"""Base model mixins for tenant isolation and timestamps."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declared_attr


class TenantMixin:
    """Mixin that adds tenant_id to models for multi-tenant isolation."""

    @declared_attr
    def tenant_id(cls):
        return Column(String(36), nullable=False, index=True)


class TimestampMixin:
    """Mixin that adds created_at and updated_at."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
