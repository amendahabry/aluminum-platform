from sqlalchemy import Column, String, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin
from datetime import datetime
from sqlalchemy import DateTime


class Permission(Base, TenantMixin, TimestampMixin):
    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True)
    code = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=True)


class Role(Base, TenantMixin, TimestampMixin):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    permissions = relationship("Permission", secondary="role_permissions", backref="roles")


# Association table: role <-> permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id"), primary_key=True),
)


class UserRole(Base, TenantMixin, TimestampMixin):
    __tablename__ = "user_roles"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("tenant_id", "user_id", "role_id", name="uq_user_role_tenant"),)
