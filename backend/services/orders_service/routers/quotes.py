"""Quotes CRUD and approve with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Quote, QuoteLine
from ..schemas.quote import QuoteCreate, QuoteUpdate, QuoteResponse, QuoteLineCreate, QuoteLineResponse, QuoteApproveRequest

router = APIRouter()


def _quote_to_response(quote: Quote, lines: list[QuoteLine]) -> QuoteResponse:
    return QuoteResponse(
        id=quote.id,
        tenant_id=quote.tenant_id,
        rfq_id=quote.rfq_id,
        reference=quote.reference,
        status=quote.status,
        version=quote.version,
        customer_id=quote.customer_id,
        valid_until=quote.valid_until,
        notes=quote.notes,
        lines=[QuoteLineResponse.model_validate(l) for l in lines],
    )


@router.get("", response_model=list[QuoteResponse])
def list_quotes(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:quotes:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(Quote).filter(Quote.tenant_id == tid).offset(skip).limit(limit).all()
    result = []
    for q in items:
        lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == q.id).all()
        result.append(_quote_to_response(q, lines))
    return result


@router.get("/{quote_id}", response_model=QuoteResponse)
def get_quote(
    quote_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:quotes:read"))],
):
    tid = tenant_user["tenant_id"]
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == tid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == quote_id).all()
    return _quote_to_response(quote, lines)


@router.post("", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_quote(
    db: DbSession,
    body: QuoteCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:quotes:write"))],
):
    tid = tenant_user["tenant_id"]
    quote_id = str(uuid.uuid4())
    quote = Quote(
        id=quote_id,
        tenant_id=tid,
        rfq_id=body.rfq_id,
        reference=body.reference,
        status="draft",
        version=1,
        customer_id=body.customer_id,
        valid_until=body.valid_until,
        notes=body.notes,
    )
    db.add(quote)
    for line in body.lines:
        line_id = str(uuid.uuid4())
        total = (line.quantity * line.unit_price) if line.unit_price else None
        db.add(QuoteLine(
            id=line_id,
            tenant_id=tid,
            quote_id=quote_id,
            material_id=line.material_id,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit,
            unit_price=line.unit_price,
            total=total or line.total,
        ))
    db.commit()
    db.refresh(quote)
    lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == quote_id).all()
    return _quote_to_response(quote, lines)


@router.patch("/{quote_id}", response_model=QuoteResponse)
def update_quote(
    quote_id: str,
    db: DbSession,
    body: QuoteUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:quotes:write"))],
):
    tid = tenant_user["tenant_id"]
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == tid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if body.reference is not None:
        quote.reference = body.reference
    if body.status is not None:
        quote.status = body.status
    if body.customer_id is not None:
        quote.customer_id = body.customer_id
    if body.valid_until is not None:
        quote.valid_until = body.valid_until
    if body.notes is not None:
        quote.notes = body.notes
    quote.version += 1
    db.commit()
    db.refresh(quote)
    lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == quote_id).all()
    return _quote_to_response(quote, lines)


@router.post("/{quote_id}/versions", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_quote_version(
    quote_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:quotes:version"))],
):
    tid = tenant_user["tenant_id"]
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == tid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    new_quote_id = str(uuid.uuid4())
    new_quote = Quote(
        id=new_quote_id,
        tenant_id=tid,
        rfq_id=quote.rfq_id,
        reference=quote.reference,
        status="draft",
        version=quote.version + 1,
        customer_id=quote.customer_id,
        valid_until=quote.valid_until,
        notes=quote.notes,
    )
    db.add(new_quote)
    lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == quote_id).all()
    for line in lines:
        line_id = str(uuid.uuid4())
        db.add(QuoteLine(
            id=line_id,
            tenant_id=tid,
            quote_id=new_quote_id,
            material_id=line.material_id,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit,
            unit_price=line.unit_price,
            total=line.total,
        ))
    db.commit()
    db.refresh(new_quote)
    new_lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == new_quote_id).all()
    return _quote_to_response(new_quote, new_lines)


@router.post("/{quote_id}/approve", response_model=QuoteResponse)
def approve_quote(
    quote_id: str,
    db: DbSession,
    body: QuoteApproveRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:quotes:approve"))],
):
    tid = tenant_user["tenant_id"]
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == tid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    quote.status = "approved" if body.approved else "rejected"
    if body.notes:
        quote.notes = (quote.notes or "") + "\n" + body.notes
    db.commit()
    db.refresh(quote)
    lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == quote_id).all()
    return _quote_to_response(quote, lines)


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:quotes:write"))],
):
    tid = tenant_user["tenant_id"]
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == tid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    db.query(QuoteLine).filter(QuoteLine.quote_id == quote_id, QuoteLine.tenant_id == tid).delete()
    db.delete(quote)
    db.commit()
