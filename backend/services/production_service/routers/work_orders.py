"""Work orders CRUD (stub)."""
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from shared.auth.deps import require_permission
from ..deps import TenantUser

router = APIRouter()
_work_orders: dict[str, dict] = {}


class WorkOrderCreate(BaseModel):
    bom_id: str
    reference: str | None = None
    quantity: int = 1
    due_date: datetime | None = None


class WorkOrderUpdate(BaseModel):
    reference: str | None = None
    status: str | None = None
    quantity: int | None = None
    due_date: datetime | None = None


class WorkOrderResponse(BaseModel):
    id: str
    tenant_id: str
    bom_id: str
    reference: str | None
    status: str
    quantity: int
    due_date: str | None
    created_at: str


@router.get("", response_model=list[WorkOrderResponse])
def list_work_orders(
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:read"))],
):
    tid = tenant_user["tenant_id"]
    return [WorkOrderResponse(**wo) for wo in _work_orders.values() if wo.get("tenant_id") == tid]


@router.get("/{wo_id}", response_model=WorkOrderResponse)
def get_work_order(
    wo_id: str,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:read"))],
):
    tid = tenant_user["tenant_id"]
    if wo_id not in _work_orders or _work_orders[wo_id].get("tenant_id") != tid:
        raise HTTPException(status_code=404, detail="Work order not found")
    return WorkOrderResponse(**_work_orders[wo_id])


@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order(
    body: WorkOrderCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    wo_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    _work_orders[wo_id] = {
        "id": wo_id,
        "tenant_id": tid,
        "bom_id": body.bom_id,
        "reference": body.reference,
        "status": "draft",
        "quantity": body.quantity,
        "due_date": body.due_date.isoformat() if body.due_date else None,
        "created_at": now,
    }
    return WorkOrderResponse(**_work_orders[wo_id])


@router.patch("/{wo_id}", response_model=WorkOrderResponse)
def update_work_order(
    wo_id: str,
    body: WorkOrderUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    if wo_id not in _work_orders or _work_orders[wo_id].get("tenant_id") != tid:
        raise HTTPException(status_code=404, detail="Work order not found")
    if body.reference is not None:
        _work_orders[wo_id]["reference"] = body.reference
    if body.status is not None:
        _work_orders[wo_id]["status"] = body.status
    if body.quantity is not None:
        _work_orders[wo_id]["quantity"] = body.quantity
    if body.due_date is not None:
        _work_orders[wo_id]["due_date"] = body.due_date.isoformat()
    return WorkOrderResponse(**_work_orders[wo_id])


@router.delete("/{wo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_order(
    wo_id: str,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    if wo_id not in _work_orders or _work_orders[wo_id].get("tenant_id") != tid:
        raise HTTPException(status_code=404, detail="Work order not found")
    del _work_orders[wo_id]
