from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class QuoteLineCreate(BaseModel):
    material_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal = 1
    unit: str = "pcs"
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None


class QuoteLineResponse(BaseModel):
    id: str
    quote_id: str
    material_id: Optional[str]
    description: Optional[str]
    quantity: Decimal
    unit: str
    unit_price: Optional[Decimal]
    total: Optional[Decimal]

    class Config:
        from_attributes = True


class QuoteCreate(BaseModel):
    rfq_id: Optional[str] = None
    reference: Optional[str] = None
    customer_id: Optional[str] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    lines: list[QuoteLineCreate] = []


class QuoteUpdate(BaseModel):
    reference: Optional[str] = None
    status: Optional[str] = None
    customer_id: Optional[str] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None


class QuoteApproveRequest(BaseModel):
    approved: bool = True
    notes: Optional[str] = None


class QuoteResponse(BaseModel):
    id: str
    tenant_id: str
    rfq_id: Optional[str]
    reference: Optional[str]
    status: str
    version: int
    customer_id: Optional[str]
    valid_until: Optional[datetime]
    notes: Optional[str]
    lines: list[QuoteLineResponse] = []

    class Config:
        from_attributes = True
