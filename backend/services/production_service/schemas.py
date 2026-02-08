from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class MachineCreate(BaseModel):
    name: str
    capacity_per_hour: Optional[Decimal] = None
    constraints: Optional[str] = None
    is_active: Optional[bool] = True


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    capacity_per_hour: Optional[Decimal] = None
    constraints: Optional[str] = None
    is_active: Optional[bool] = None


class MachineResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    capacity_per_hour: Optional[Decimal]
    constraints: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class WorkOrderCreate(BaseModel):
    bom_id: Optional[str] = None
    reference: Optional[str] = None
    quantity: Decimal = 1
    due_date: Optional[datetime] = None


class WorkOrderUpdate(BaseModel):
    reference: Optional[str] = None
    status: Optional[str] = None
    quantity: Optional[Decimal] = None
    due_date: Optional[datetime] = None


class WorkOrderResponse(BaseModel):
    id: str
    tenant_id: str
    bom_id: Optional[str]
    reference: Optional[str]
    status: str
    quantity: Decimal
    due_date: Optional[datetime]

    class Config:
        from_attributes = True


class TimeEntryCreate(BaseModel):
    work_order_id: str
    machine_id: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    notes: Optional[str] = None


class TimeEntryResponse(BaseModel):
    id: str
    tenant_id: str
    work_order_id: str
    machine_id: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True
