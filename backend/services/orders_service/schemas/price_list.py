from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PriceListItemCreate(BaseModel):
    material_id: Optional[str] = None
    profile_id: Optional[str] = None
    accessory_id: Optional[str] = None
    unit_price: Decimal
    currency: str = "USD"


class PriceListItemResponse(BaseModel):
    id: str
    price_list_id: str
    material_id: Optional[str]
    profile_id: Optional[str]
    accessory_id: Optional[str]
    unit_price: Decimal
    currency: str

    class Config:
        from_attributes = True


class PriceListCreate(BaseModel):
    name: str
    customer_id: Optional[str] = None
    customer_group: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    notes: Optional[str] = None
    items: list[PriceListItemCreate] = []


class PriceListUpdate(BaseModel):
    name: Optional[str] = None
    customer_id: Optional[str] = None
    customer_group: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    notes: Optional[str] = None


class PriceListResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    customer_id: Optional[str]
    customer_group: Optional[str]
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    notes: Optional[str]
    items: list[PriceListItemResponse] = []

    class Config:
        from_attributes = True
