from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PurchaseOrderLineCreate(BaseModel):
    material_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal
    unit: str = "pcs"
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None


class PurchaseOrderLineResponse(BaseModel):
    id: str
    purchase_order_id: str
    material_id: Optional[str]
    description: Optional[str]
    quantity: Decimal
    unit: str
    unit_price: Optional[Decimal]
    total: Optional[Decimal]

    class Config:
        from_attributes = True


class PurchaseOrderCreate(BaseModel):
    supplier_name: str
    reference: Optional[str] = None
    order_date: Optional[datetime] = None
    expected_date: Optional[datetime] = None
    notes: Optional[str] = None
    lines: list[PurchaseOrderLineCreate] = []


class PurchaseOrderUpdate(BaseModel):
    supplier_name: Optional[str] = None
    reference: Optional[str] = None
    status: Optional[str] = None
    order_date: Optional[datetime] = None
    expected_date: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    id: str
    tenant_id: str
    supplier_name: str
    reference: Optional[str]
    status: str
    order_date: datetime
    expected_date: Optional[datetime]
    notes: Optional[str]
    lines: list[PurchaseOrderLineResponse] = []

    class Config:
        from_attributes = True
