from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class AccessoryCreate(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    unit: str = "pcs"
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class AccessoryUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    cost: Optional[Decimal] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class AccessoryResponse(BaseModel):
    id: str
    tenant_id: str
    sku: str
    name: str
    category: Optional[str]
    unit: str
    cost: Optional[Decimal]
    notes: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
