from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class RFQLineCreate(BaseModel):
    material_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal = 1
    unit: str = "pcs"


class RFQLineResponse(BaseModel):
    id: str
    rfq_id: str
    material_id: Optional[str]
    description: Optional[str]
    quantity: Decimal
    unit: str

    class Config:
        from_attributes = True


class RFQCreate(BaseModel):
    reference: Optional[str] = None
    customer_id: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    lines: list[RFQLineCreate] = []


class RFQUpdate(BaseModel):
    reference: Optional[str] = None
    status: Optional[str] = None
    customer_id: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class RFQResponse(BaseModel):
    id: str
    tenant_id: str
    reference: Optional[str]
    status: str
    customer_id: Optional[str]
    due_date: Optional[datetime]
    notes: Optional[str]
    lines: list[RFQLineResponse] = []

    class Config:
        from_attributes = True
