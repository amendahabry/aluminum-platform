"""Quote conversion helpers."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Quote, QuoteLine, SalesOrder, SalesOrderLine
from ..schemas.sales_order import SalesOrderResponse, SalesOrderLineResponse

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


@router.post("/{quote_id}/convert", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
def convert_quote_to_order(
    quote_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:sales:write"))],
):
    tid = tenant_user["tenant_id"]
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == tid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if quote.status != "approved":
        raise HTTPException(status_code=400, detail="Quote must be approved before conversion")

    order_id = str(uuid.uuid4())
    order = SalesOrder(
        id=order_id,
        tenant_id=tid,
        quote_id=quote.id,
        reference=quote.reference,
        status="draft",
        customer_id=quote.customer_id,
        order_date=quote.updated_at,
        source_quote_id=quote.id,
        notes=quote.notes,
    )
    db.add(order)

    lines = db.query(QuoteLine).filter(QuoteLine.tenant_id == tid, QuoteLine.quote_id == quote_id).all()
    for line in lines:
        line_id = str(uuid.uuid4())
        db.add(SalesOrderLine(
            id=line_id,
            tenant_id=tid,
            sales_order_id=order_id,
            material_id=line.material_id,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit,
            unit_price=line.unit_price,
            total=line.total,
        ))
    db.commit()
    db.refresh(order)
    order_lines = db.query(SalesOrderLine).filter(SalesOrderLine.tenant_id == tid, SalesOrderLine.sales_order_id == order_id).all()
    return _order_to_response(order, order_lines)
