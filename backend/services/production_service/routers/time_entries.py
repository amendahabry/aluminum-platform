"""Work order time tracking."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import TenantUser, DbSession
from datetime import datetime

from ..models import WorkOrderTimeEntry
from ..schemas import TimeEntryCreate, TimeEntryResponse

router = APIRouter()


@router.get("", response_model=list[TimeEntryResponse])
def list_time_entries(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:time:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(WorkOrderTimeEntry).filter(WorkOrderTimeEntry.tenant_id == tid).offset(skip).limit(limit).all()
    return [TimeEntryResponse.model_validate(i) for i in items]


@router.post("", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    db: DbSession,
    body: TimeEntryCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:time:write"))],
):
    tid = tenant_user["tenant_id"]
    entry_id = str(uuid.uuid4())
    entry = WorkOrderTimeEntry(
        id=entry_id,
        tenant_id=tid,
        work_order_id=body.work_order_id,
        machine_id=body.machine_id,
        started_at=body.started_at or datetime.utcnow(),
        ended_at=body.ended_at,
        notes=body.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return TimeEntryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_entry(
    entry_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:time:write"))],
):
    tid = tenant_user["tenant_id"]
    entry = db.query(WorkOrderTimeEntry).filter(WorkOrderTimeEntry.id == entry_id, WorkOrderTimeEntry.tenant_id == tid).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    db.delete(entry)
    db.commit()
