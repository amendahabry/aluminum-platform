from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ScrapRecordCreate(BaseModel):
    material_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    weight_kg: Decimal = 0
    reason: Optional[str] = None
    cost_recovery: Optional[Decimal] = None
    reported_at: Optional[datetime] = None
    notes: Optional[str] = None


class ScrapRecordUpdate(BaseModel):
    material_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    weight_kg: Optional[Decimal] = None
    reason: Optional[str] = None
    cost_recovery: Optional[Decimal] = None
    reported_at: Optional[datetime] = None
    notes: Optional[str] = None


class ScrapRecordResponse(BaseModel):
    id: str
    tenant_id: str
    material_id: Optional[str]
    warehouse_id: Optional[str]
    weight_kg: Decimal
    reason: Optional[str]
    cost_recovery: Optional[Decimal]
    reported_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class ScrapSummaryResponse(BaseModel):
    total_weight_kg: Decimal
    total_recovery: Decimal
    record_count: int
