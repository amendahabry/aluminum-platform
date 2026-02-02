"""RFQ CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import RFQ, RFQLine
from ..schemas.rfq import RFQCreate, RFQUpdate, RFQResponse, RFQLineCreate, RFQLineResponse

router = APIRouter()


def _rfq_to_response(rfq: RFQ, lines: list[RFQLine]) -> RFQResponse:
    return RFQResponse(
        id=rfq.id,
        tenant_id=rfq.tenant_id,
        reference=rfq.reference,
        status=rfq.status,
        customer_id=rfq.customer_id,
        due_date=rfq.due_date,
        notes=rfq.notes,
        lines=[RFQLineResponse.model_validate(l) for l in lines],
    )


@router.get("", response_model=list[RFQResponse])
def list_rfqs(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:rfq:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(RFQ).filter(RFQ.tenant_id == tid).offset(skip).limit(limit).all()
    result = []
    for rfq in items:
        lines = db.query(RFQLine).filter(RFQLine.tenant_id == tid, RFQLine.rfq_id == rfq.id).all()
        result.append(_rfq_to_response(rfq, lines))
    return result


@router.get("/{rfq_id}", response_model=RFQResponse)
def get_rfq(
    rfq_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:rfq:read"))],
):
    tid = tenant_user["tenant_id"]
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id, RFQ.tenant_id == tid).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    lines = db.query(RFQLine).filter(RFQLine.tenant_id == tid, RFQLine.rfq_id == rfq_id).all()
    return _rfq_to_response(rfq, lines)


@router.post("", response_model=RFQResponse, status_code=status.HTTP_201_CREATED)
def create_rfq(
    db: DbSession,
    body: RFQCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:rfq:write"))],
):
    tid = tenant_user["tenant_id"]
    rfq_id = str(uuid.uuid4())
    rfq = RFQ(
        id=rfq_id,
        tenant_id=tid,
        reference=body.reference,
        status="draft",
        customer_id=body.customer_id,
        due_date=body.due_date,
        notes=body.notes,
    )
    db.add(rfq)
    for line in body.lines:
        line_id = str(uuid.uuid4())
        db.add(RFQLine(
            id=line_id,
            tenant_id=tid,
            rfq_id=rfq_id,
            material_id=line.material_id,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit,
        ))
    db.commit()
    db.refresh(rfq)
    lines = db.query(RFQLine).filter(RFQLine.tenant_id == tid, RFQLine.rfq_id == rfq_id).all()
    return _rfq_to_response(rfq, lines)


@router.patch("/{rfq_id}", response_model=RFQResponse)
def update_rfq(
    rfq_id: str,
    db: DbSession,
    body: RFQUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:rfq:write"))],
):
    tid = tenant_user["tenant_id"]
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id, RFQ.tenant_id == tid).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    if body.reference is not None:
        rfq.reference = body.reference
    if body.status is not None:
        rfq.status = body.status
    if body.customer_id is not None:
        rfq.customer_id = body.customer_id
    if body.due_date is not None:
        rfq.due_date = body.due_date
    if body.notes is not None:
        rfq.notes = body.notes
    db.commit()
    db.refresh(rfq)
    lines = db.query(RFQLine).filter(RFQLine.tenant_id == tid, RFQLine.rfq_id == rfq_id).all()
    return _rfq_to_response(rfq, lines)


@router.delete("/{rfq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rfq(
    rfq_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:rfq:write"))],
):
    tid = tenant_user["tenant_id"]
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id, RFQ.tenant_id == tid).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    db.query(RFQLine).filter(RFQLine.rfq_id == rfq_id, RFQLine.tenant_id == tid).delete()
    db.delete(rfq)
    db.commit()
