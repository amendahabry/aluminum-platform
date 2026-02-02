from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from datetime import datetime
from shared.db.session import Base
from shared.db.base import TenantMixin, TimestampMixin


class StockLot(Base, TenantMixin, TimestampMixin):
    __tablename__ = "stock_lots"

    id = Column(String(36), primary_key=True)
    material_id = Column(String(36), nullable=False, index=True)
    warehouse_id = Column(String(36), nullable=False, index=True)
    location_id = Column(String(36), nullable=True, index=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=0)
    batch_ref = Column(String(64), nullable=True, index=True)
    reserved_quantity = Column(Numeric(18, 4), nullable=False, default=0)


class StockMovement(Base, TenantMixin):
    __tablename__ = "stock_movements"

    id = Column(String(36), primary_key=True)
    material_id = Column(String(36), nullable=False, index=True)
    warehouse_id = Column(String(36), nullable=False, index=True)
    location_id = Column(String(36), nullable=True)
    quantity_delta = Column(Numeric(18, 4), nullable=False)  # + in, - out
    movement_type = Column(String(32), nullable=False, index=True)  # in, out, transfer, adjust
    reference_type = Column(String(64), nullable=True)
    reference_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Reservation(Base, TenantMixin):
    __tablename__ = "reservations"

    id = Column(String(36), primary_key=True)
    stock_lot_id = Column(String(36), nullable=False, index=True)
    quantity = Column(Numeric(18, 4), nullable=False)
    reference_type = Column(String(64), nullable=True)
    reference_id = Column(String(36), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
