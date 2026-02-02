from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SalesOrderLineResponse(BaseModel):
    id: str
    sales_order_id: str
    material_id: Optional[str]
    description: Optional[str]
    quantity: Decimal
    unit: str
    unit_price: Optional[Decimal]
    total: Optional[Decimal]

    class Config:
        from_attributes = True


class SalesOrderCreate(BaseModel):
    quote_id: Optional[str] = None
    reference: Optional[str] = None
    customer_id: Optional[str] = None
    order_date: Optional[datetime] = None
    notes: Optional[str] = None


class SalesOrderUpdate(BaseModel):
    reference: Optional[str] = None
    status: Optional[str] = None
    customer_id: Optional[str] = None
    order_date: Optional[datetime] = None
    notes: Optional[str] = None


class SalesOrderResponse(BaseModel):
    id: str
    tenant_id: str
    quote_id: Optional[str]
    reference: Optional[str]
    status: str
    customer_id: Optional[str]
    order_date: Optional[datetime]
    notes: Optional[str]
    lines: list[SalesOrderLineResponse] = []

    class Config:
        from_attributes = True
