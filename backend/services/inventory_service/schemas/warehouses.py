from pydantic import BaseModel
from typing import Optional


class WarehouseCreate(BaseModel):
    name: str
    code: Optional[str] = None
    address: Optional[str] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None


class WarehouseResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    code: Optional[str]
    address: Optional[str]

    class Config:
        from_attributes = True
