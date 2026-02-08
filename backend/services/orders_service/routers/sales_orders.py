"""Sales orders CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import SalesOrder, SalesOrderLine, Quote
from ..schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderUpdate,
    SalesOrderResponse,
    SalesOrderLineResponse,
)

router = APIRouter()


def _order_to_response(order: SalesOrder, lines: list[SalesOrderLine]) -> SalesOrderResponse:
    return SalesOrderResponse(
        id=order.id,
        tenant_id=order.tenant_id,
        quote_id=order.quote_id,
        reference=order.reference,
        status=order.status,
        customer_id=order.customer_id,
        order_date=order.order_date,
        source_quote_id=order.source_quote_id,
        notes=order.notes,
        lines=[SalesOrderLineResponse.model_validate(l) for l in lines],
    )


def _validate_quote(db: DbSession, tid: str, quote_id: str) -> None:
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == tid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if quote.status != "approved":
        raise HTTPException(status_code=400, detail="Quote must be approved before conversion")


@router.get("", response_model=list[SalesOrderResponse])
def list_sales_orders(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:sales:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(SalesOrder).filter(SalesOrder.tenant_id == tid).offset(skip).limit(limit).all()
    result = []
    for order in items:
        lines = db.query(SalesOrderLine).filter(SalesOrderLine.tenant_id == tid, SalesOrderLine.sales_order_id == order.id).all()
        result.append(_order_to_response(order, lines))
    return result


@router.get("/{order_id}", response_model=SalesOrderResponse)
def get_sales_order(
    order_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:sales:read"))],
):
    tid = tenant_user["tenant_id"]
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id, SalesOrder.tenant_id == tid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    lines = db.query(SalesOrderLine).filter(SalesOrderLine.tenant_id == tid, SalesOrderLine.sales_order_id == order_id).all()
    return _order_to_response(order, lines)


@router.post("", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
def create_sales_order(
    db: DbSession,
    body: SalesOrderCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:sales:write"))],
):
    tid = tenant_user["tenant_id"]
    order_id = str(uuid.uuid4())
    source_quote_id = body.source_quote_id or body.quote_id
    if source_quote_id:
        _validate_quote(db, tid, source_quote_id)
    order = SalesOrder(
        id=order_id,
        tenant_id=tid,
        quote_id=body.quote_id,
        reference=body.reference,
        status="draft",
        customer_id=body.customer_id,
        order_date=body.order_date,
        source_quote_id=source_quote_id,
        notes=body.notes,
    )
    db.add(order)
    for line in body.lines:
        line_id = str(uuid.uuid4())
        total = (line.quantity * line.unit_price) if line.unit_price else None
        db.add(SalesOrderLine(
            id=line_id,
            tenant_id=tid,
            sales_order_id=order_id,
            material_id=line.material_id,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit,
            unit_price=line.unit_price,
            total=total or line.total,
        ))
    db.commit()
    db.refresh(order)
    lines = db.query(SalesOrderLine).filter(SalesOrderLine.tenant_id == tid, SalesOrderLine.sales_order_id == order_id).all()
    return _order_to_response(order, lines)


@router.patch("/{order_id}", response_model=SalesOrderResponse)
def update_sales_order(
    order_id: str,
    db: DbSession,
    body: SalesOrderUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:sales:write"))],
):
    tid = tenant_user["tenant_id"]
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id, SalesOrder.tenant_id == tid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    if body.reference is not None:
        order.reference = body.reference
    if body.status is not None:
        order.status = body.status
    if body.customer_id is not None:
        order.customer_id = body.customer_id
    if body.order_date is not None:
        order.order_date = body.order_date
    if body.source_quote_id is not None:
        _validate_quote(db, tid, body.source_quote_id)
        order.source_quote_id = body.source_quote_id
    if body.notes is not None:
        order.notes = body.notes
    db.commit()
    db.refresh(order)
    lines = db.query(SalesOrderLine).filter(SalesOrderLine.tenant_id == tid, SalesOrderLine.sales_order_id == order_id).all()
    return _order_to_response(order, lines)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sales_order(
    order_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:sales:write"))],
):
    tid = tenant_user["tenant_id"]
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id, SalesOrder.tenant_id == tid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    db.query(SalesOrderLine).filter(SalesOrderLine.sales_order_id == order_id, SalesOrderLine.tenant_id == tid).delete()
    db.delete(order)
    db.commit()
