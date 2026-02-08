from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    is_active: Optional[bool] = True


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    payment_terms: Optional[str]
    credit_limit: Optional[Decimal]
    billing_address: Optional[str]
    shipping_address: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
