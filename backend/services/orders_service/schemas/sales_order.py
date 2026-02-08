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


class SalesOrderLineCreate(BaseModel):
    material_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal = 1
    unit: str = "pcs"
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None


class SalesOrderCreate(BaseModel):
    quote_id: Optional[str] = None
    reference: Optional[str] = None
    customer_id: Optional[str] = None
    order_date: Optional[datetime] = None
    source_quote_id: Optional[str] = None
    notes: Optional[str] = None
    lines: list[SalesOrderLineCreate] = []


class SalesOrderUpdate(BaseModel):
    reference: Optional[str] = None
    status: Optional[str] = None
    customer_id: Optional[str] = None
    order_date: Optional[datetime] = None
    source_quote_id: Optional[str] = None
    notes: Optional[str] = None


class SalesOrderResponse(BaseModel):
    id: str
    tenant_id: str
    quote_id: Optional[str]
    reference: Optional[str]
    status: str
    customer_id: Optional[str]
    order_date: Optional[datetime]
    source_quote_id: Optional[str]
    notes: Optional[str]
    lines: list[SalesOrderLineResponse] = []

    class Config:
        from_attributes = True
