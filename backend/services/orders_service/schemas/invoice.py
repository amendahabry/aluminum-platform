from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class InvoiceCreate(BaseModel):
    sales_order_id: Optional[str] = None
    reference: Optional[str] = None
    customer_id: Optional[str] = None
    total_amount: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    sales_order_id: Optional[str]
    reference: Optional[str]
    status: str
    customer_id: Optional[str]
    total_amount: Optional[Decimal]
    due_date: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True
