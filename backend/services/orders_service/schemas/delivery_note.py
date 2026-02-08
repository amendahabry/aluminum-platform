from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DeliveryNoteLineCreate(BaseModel):
    sales_order_line_id: Optional[str] = None
    material_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal


class DeliveryNoteLineResponse(BaseModel):
    id: str
    delivery_note_id: str
    sales_order_line_id: Optional[str]
    material_id: Optional[str]
    description: Optional[str]
    quantity: Decimal

    class Config:
        from_attributes = True


class DeliveryNoteCreate(BaseModel):
    sales_order_id: Optional[str] = None
    reference: Optional[str] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None
    lines: list[DeliveryNoteLineCreate] = []


class DeliveryNoteUpdate(BaseModel):
    reference: Optional[str] = None
    status: Optional[str] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None


class DeliveryNoteResponse(BaseModel):
    id: str
    tenant_id: str
    sales_order_id: Optional[str]
    reference: Optional[str]
    status: str
    delivered_at: Optional[datetime]
    notes: Optional[str]
    lines: list[DeliveryNoteLineResponse] = []

    class Config:
        from_attributes = True
