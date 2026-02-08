"""Scrap and waste tracking with reporting."""
import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import ScrapRecord
from ..schemas.scrap import ScrapRecordCreate, ScrapRecordUpdate, ScrapRecordResponse, ScrapSummaryResponse

router = APIRouter()


@router.get("", response_model=list[ScrapRecordResponse])
def list_scrap_records(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:scrap:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(ScrapRecord).filter(ScrapRecord.tenant_id == tid).offset(skip).limit(limit).all()
    return [ScrapRecordResponse.model_validate(i) for i in items]


@router.get("/summary", response_model=ScrapSummaryResponse)
def scrap_summary(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:reports:read"))],
):
    tid = tenant_user["tenant_id"]
    totals = db.query(
        func.coalesce(func.sum(ScrapRecord.weight_kg), 0),
        func.coalesce(func.sum(ScrapRecord.cost_recovery), 0),
        func.count(ScrapRecord.id),
    ).filter(ScrapRecord.tenant_id == tid).one()
    return ScrapSummaryResponse(
        total_weight_kg=Decimal(totals[0]),
        total_recovery=Decimal(totals[1]),
        record_count=int(totals[2]),
    )


@router.get("/{record_id}", response_model=ScrapRecordResponse)
def get_scrap_record(
    record_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:scrap:read"))],
):
    tid = tenant_user["tenant_id"]
    record = db.query(ScrapRecord).filter(ScrapRecord.id == record_id, ScrapRecord.tenant_id == tid).first()
    if not record:
        raise HTTPException(status_code=404, detail="Scrap record not found")
    return ScrapRecordResponse.model_validate(record)


@router.post("", response_model=ScrapRecordResponse, status_code=status.HTTP_201_CREATED)
def create_scrap_record(
    db: DbSession,
    body: ScrapRecordCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:scrap:write"))],
):
    tid = tenant_user["tenant_id"]
    record_id = str(uuid.uuid4())
    record = ScrapRecord(
        id=record_id,
        tenant_id=tid,
        material_id=body.material_id,
        warehouse_id=body.warehouse_id,
        weight_kg=body.weight_kg,
        reason=body.reason,
        cost_recovery=body.cost_recovery,
        reported_at=body.reported_at,
        notes=body.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ScrapRecordResponse.model_validate(record)


@router.patch("/{record_id}", response_model=ScrapRecordResponse)
def update_scrap_record(
    record_id: str,
    db: DbSession,
    body: ScrapRecordUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:scrap:write"))],
):
    tid = tenant_user["tenant_id"]
    record = db.query(ScrapRecord).filter(ScrapRecord.id == record_id, ScrapRecord.tenant_id == tid).first()
    if not record:
        raise HTTPException(status_code=404, detail="Scrap record not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return ScrapRecordResponse.model_validate(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scrap_record(
    record_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:scrap:write"))],
):
    tid = tenant_user["tenant_id"]
    record = db.query(ScrapRecord).filter(ScrapRecord.id == record_id, ScrapRecord.tenant_id == tid).first()
    if not record:
        raise HTTPException(status_code=404, detail="Scrap record not found")
    db.delete(record)
    db.commit()
