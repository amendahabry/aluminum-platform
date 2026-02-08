"""Orders reporting endpoints."""
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Invoice, SalesOrder

router = APIRouter()


@router.get("/sales-summary")
def sales_summary(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("management:reports:read"))],
):
    tid = tenant_user["tenant_id"]
    total_invoiced = db.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(Invoice.tenant_id == tid).scalar()
    sales_orders = db.query(func.count(SalesOrder.id)).filter(SalesOrder.tenant_id == tid).scalar()
    return {
        "total_invoiced": Decimal(total_invoiced or 0),
        "sales_orders": int(sales_orders or 0),
    }
