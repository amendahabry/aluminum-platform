"""Invoices CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Invoice
from ..schemas.invoice import InvoiceCreate, InvoiceResponse

router = APIRouter()


@router.get("", response_model=list[InvoiceResponse])
def list_invoices(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:invoices:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(Invoice).filter(Invoice.tenant_id == tid).offset(skip).limit(limit).all()
    return [InvoiceResponse.model_validate(i) for i in items]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:invoices:read"))],
):
    tid = tenant_user["tenant_id"]
    inv = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.tenant_id == tid).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceResponse.model_validate(inv)


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    db: DbSession,
    body: InvoiceCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:invoices:write"))],
):
    tid = tenant_user["tenant_id"]
    inv_id = str(uuid.uuid4())
    inv = Invoice(
        id=inv_id,
        tenant_id=tid,
        sales_order_id=body.sales_order_id,
        reference=body.reference,
        status="draft",
        customer_id=body.customer_id,
        total_amount=body.total_amount,
        due_date=body.due_date,
        notes=body.notes,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return InvoiceResponse.model_validate(inv)


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: str,
    db: DbSession,
    body: InvoiceCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:invoices:write"))],
):
    tid = tenant_user["tenant_id"]
    inv = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.tenant_id == tid).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if body.reference is not None:
        inv.reference = body.reference
    if body.customer_id is not None:
        inv.customer_id = body.customer_id
    if body.total_amount is not None:
        inv.total_amount = body.total_amount
    if body.due_date is not None:
        inv.due_date = body.due_date
    if body.notes is not None:
        inv.notes = body.notes
    db.commit()
    db.refresh(inv)
    return InvoiceResponse.model_validate(inv)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:invoices:write"))],
):
    tid = tenant_user["tenant_id"]
    inv = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.tenant_id == tid).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(inv)
    db.commit()
