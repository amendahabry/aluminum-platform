"""Management dashboards endpoints."""
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func

from shared.auth.deps import require_permission
from shared.db.session import get_db
from shared.tenants.middleware import set_tenant_context
from services.orders_service.models import Invoice
from services.inventory_service.models import ScrapRecord
from services.production_service.models import WorkOrder

router = APIRouter()


@router.get("/summary")
def dashboard_summary(
    tenant_user: Annotated[dict, Depends(require_permission("management:dashboard:read"))],
):
    tid = tenant_user["tenant_id"]
    set_tenant_context(tid)
    db = next(get_db())
    total_revenue = db.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(Invoice.tenant_id == tid).scalar()
    total_scrap = db.query(func.coalesce(func.sum(ScrapRecord.weight_kg), 0)).filter(ScrapRecord.tenant_id == tid).scalar()
    total_orders = db.query(func.count(WorkOrder.id)).filter(WorkOrder.tenant_id == tid).scalar()
    return {
        "profit": Decimal(total_revenue or 0),
        "scrap_pct": Decimal("0"),
        "utilization": Decimal("0"),
        "work_orders": int(total_orders or 0),
    }
