"""Delivery notes with partial deliveries."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import DeliveryNote, DeliveryNoteLine
from ..schemas.delivery_note import DeliveryNoteCreate, DeliveryNoteUpdate, DeliveryNoteResponse, DeliveryNoteLineResponse

router = APIRouter()


def _to_response(note: DeliveryNote, lines: list[DeliveryNoteLine]) -> DeliveryNoteResponse:
    return DeliveryNoteResponse(
        id=note.id,
        tenant_id=note.tenant_id,
        sales_order_id=note.sales_order_id,
        reference=note.reference,
        status=note.status,
        delivered_at=note.delivered_at,
        notes=note.notes,
        lines=[DeliveryNoteLineResponse.model_validate(l) for l in lines],
    )


@router.get("", response_model=list[DeliveryNoteResponse])
def list_delivery_notes(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:delivery-notes:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(DeliveryNote).filter(DeliveryNote.tenant_id == tid).offset(skip).limit(limit).all()
    result = []
    for note in items:
        lines = db.query(DeliveryNoteLine).filter(DeliveryNoteLine.tenant_id == tid, DeliveryNoteLine.delivery_note_id == note.id).all()
        result.append(_to_response(note, lines))
    return result


@router.get("/{note_id}", response_model=DeliveryNoteResponse)
def get_delivery_note(
    note_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:delivery-notes:read"))],
):
    tid = tenant_user["tenant_id"]
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id, DeliveryNote.tenant_id == tid).first()
    if not note:
        raise HTTPException(status_code=404, detail="Delivery note not found")
    lines = db.query(DeliveryNoteLine).filter(DeliveryNoteLine.tenant_id == tid, DeliveryNoteLine.delivery_note_id == note_id).all()
    return _to_response(note, lines)


@router.post("", response_model=DeliveryNoteResponse, status_code=status.HTTP_201_CREATED)
def create_delivery_note(
    db: DbSession,
    body: DeliveryNoteCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:delivery-notes:write"))],
):
    tid = tenant_user["tenant_id"]
    note_id = str(uuid.uuid4())
    note = DeliveryNote(
        id=note_id,
        tenant_id=tid,
        sales_order_id=body.sales_order_id,
        reference=body.reference,
        status="draft",
        delivered_at=body.delivered_at,
        notes=body.notes,
    )
    db.add(note)
    for line in body.lines:
        line_id = str(uuid.uuid4())
        db.add(DeliveryNoteLine(
            id=line_id,
            tenant_id=tid,
            delivery_note_id=note_id,
            sales_order_line_id=line.sales_order_line_id,
            material_id=line.material_id,
            description=line.description,
            quantity=line.quantity,
        ))
    db.commit()
    db.refresh(note)
    lines = db.query(DeliveryNoteLine).filter(DeliveryNoteLine.tenant_id == tid, DeliveryNoteLine.delivery_note_id == note_id).all()
    return _to_response(note, lines)


@router.patch("/{note_id}", response_model=DeliveryNoteResponse)
def update_delivery_note(
    note_id: str,
    db: DbSession,
    body: DeliveryNoteUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:delivery-notes:write"))],
):
    tid = tenant_user["tenant_id"]
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id, DeliveryNote.tenant_id == tid).first()
    if not note:
        raise HTTPException(status_code=404, detail="Delivery note not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    lines = db.query(DeliveryNoteLine).filter(DeliveryNoteLine.tenant_id == tid, DeliveryNoteLine.delivery_note_id == note_id).all()
    return _to_response(note, lines)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery_note(
    note_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:delivery-notes:write"))],
):
    tid = tenant_user["tenant_id"]
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id, DeliveryNote.tenant_id == tid).first()
    if not note:
        raise HTTPException(status_code=404, detail="Delivery note not found")
    db.query(DeliveryNoteLine).filter(DeliveryNoteLine.tenant_id == tid, DeliveryNoteLine.delivery_note_id == note_id).delete()
    db.delete(note)
    db.commit()
