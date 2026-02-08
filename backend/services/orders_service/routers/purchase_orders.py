"""Supplier purchase orders."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import PurchaseOrder, PurchaseOrderLine
from ..schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse, PurchaseOrderLineResponse

router = APIRouter()


def _to_response(po: PurchaseOrder, lines: list[PurchaseOrderLine]) -> PurchaseOrderResponse:
    return PurchaseOrderResponse(
        id=po.id,
        tenant_id=po.tenant_id,
        supplier_name=po.supplier_name,
        reference=po.reference,
        status=po.status,
        order_date=po.order_date,
        expected_date=po.expected_date,
        notes=po.notes,
        lines=[PurchaseOrderLineResponse.model_validate(l) for l in lines],
    )


@router.get("", response_model=list[PurchaseOrderResponse])
def list_purchase_orders(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:purchase-orders:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(PurchaseOrder).filter(PurchaseOrder.tenant_id == tid).offset(skip).limit(limit).all()
    result = []
    for po in items:
        lines = db.query(PurchaseOrderLine).filter(PurchaseOrderLine.tenant_id == tid, PurchaseOrderLine.purchase_order_id == po.id).all()
        result.append(_to_response(po, lines))
    return result


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(
    po_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:purchase-orders:read"))],
):
    tid = tenant_user["tenant_id"]
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tid).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    lines = db.query(PurchaseOrderLine).filter(PurchaseOrderLine.tenant_id == tid, PurchaseOrderLine.purchase_order_id == po_id).all()
    return _to_response(po, lines)


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    db: DbSession,
    body: PurchaseOrderCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:purchase-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    po_id = str(uuid.uuid4())
    po = PurchaseOrder(
        id=po_id,
        tenant_id=tid,
        supplier_name=body.supplier_name,
        reference=body.reference,
        status="draft",
        order_date=body.order_date,
        expected_date=body.expected_date,
        notes=body.notes,
    )
    db.add(po)
    for line in body.lines:
        line_id = str(uuid.uuid4())
        total = (line.quantity * line.unit_price) if line.unit_price else None
        db.add(PurchaseOrderLine(
            id=line_id,
            tenant_id=tid,
            purchase_order_id=po_id,
            material_id=line.material_id,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit,
            unit_price=line.unit_price,
            total=total or line.total,
        ))
    db.commit()
    db.refresh(po)
    lines = db.query(PurchaseOrderLine).filter(PurchaseOrderLine.tenant_id == tid, PurchaseOrderLine.purchase_order_id == po_id).all()
    return _to_response(po, lines)


@router.patch("/{po_id}", response_model=PurchaseOrderResponse)
def update_purchase_order(
    po_id: str,
    db: DbSession,
    body: PurchaseOrderUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:purchase-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tid).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(po, field, value)
    db.commit()
    db.refresh(po)
    lines = db.query(PurchaseOrderLine).filter(PurchaseOrderLine.tenant_id == tid, PurchaseOrderLine.purchase_order_id == po_id).all()
    return _to_response(po, lines)


@router.delete("/{po_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase_order(
    po_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:purchase-orders:write"))],
):
    tid = tenant_user["tenant_id"]
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tid).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    db.query(PurchaseOrderLine).filter(PurchaseOrderLine.tenant_id == tid, PurchaseOrderLine.purchase_order_id == po_id).delete()
    db.delete(po)
    db.commit()
