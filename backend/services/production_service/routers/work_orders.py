"""Work orders CRUD."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import TenantUser, DbSession
from ..models import WorkOrder
from ..schemas import WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse

router = APIRouter()


@router.get("", response_model=list[WorkOrderResponse])
def list_work_orders(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(WorkOrder).filter(WorkOrder.tenant_id == tid).offset(skip).limit(limit).all()
    return [WorkOrderResponse.model_validate(i) for i in items]


@router.get("/{wo_id}", response_model=WorkOrderResponse)
def get_work_order(
    wo_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:read"))],
):
    tid = tenant_user["tenant_id"]
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.tenant_id == tid).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    return WorkOrderResponse.model_validate(wo)


@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order(
    body: WorkOrderCreate,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    wo_id = str(uuid.uuid4())
    wo = WorkOrder(
        id=wo_id,
        tenant_id=tid,
        bom_id=body.bom_id,
        reference=body.reference,
        status="draft",
        quantity=body.quantity,
        due_date=body.due_date,
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return WorkOrderResponse.model_validate(wo)


@router.patch("/{wo_id}", response_model=WorkOrderResponse)
def update_work_order(
    wo_id: str,
    body: WorkOrderUpdate,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.tenant_id == tid).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(wo, field, value)
    db.commit()
    db.refresh(wo)
    return WorkOrderResponse.model_validate(wo)


@router.delete("/{wo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_order(
    wo_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:work-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id, WorkOrder.tenant_id == tid).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    db.delete(wo)
    db.commit()
