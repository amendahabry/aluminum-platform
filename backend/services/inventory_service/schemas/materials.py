from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class MaterialCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    unit: str = "pcs"
    weight_kg: Optional[Decimal] = None


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    weight_kg: Optional[Decimal] = None


class MaterialResponse(BaseModel):
    id: str
    tenant_id: str
    sku: str
    name: str
    description: Optional[str]
    unit: str
    weight_kg: Optional[Decimal]
    is_active: bool

    class Config:
        from_attributes = True
