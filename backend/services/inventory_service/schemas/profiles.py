from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class AluminumProfileCreate(BaseModel):
    series: str
    alloy: str
    temper: Optional[str] = None
    weight_per_meter: Decimal = 0
    cost_per_meter: Decimal = 0
    description: Optional[str] = None


class AluminumProfileUpdate(BaseModel):
    series: Optional[str] = None
    alloy: Optional[str] = None
    temper: Optional[str] = None
    weight_per_meter: Optional[Decimal] = None
    cost_per_meter: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AluminumProfileResponse(BaseModel):
    id: str
    tenant_id: str
    series: str
    alloy: str
    temper: Optional[str]
    weight_per_meter: Decimal
    cost_per_meter: Decimal
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
