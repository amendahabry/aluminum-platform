from sqlalchemy import Column, String, ForeignKey
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class Warehouse(Base, TenantMixin, TimestampMixin):
    __tablename__ = "warehouses"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(64), nullable=True, index=True)
    address = Column(String(512), nullable=True)


class Location(Base, TenantMixin, TimestampMixin):
    __tablename__ = "locations"

    id = Column(String(36), primary_key=True)
    warehouse_id = Column(String(36), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    code = Column(String(64), nullable=True, index=True)
