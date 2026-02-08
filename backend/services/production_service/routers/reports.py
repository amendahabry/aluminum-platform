"""Production reports."""
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import WorkOrder, WorkOrderTimeEntry

router = APIRouter()


@router.get("/summary")
def production_summary(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:reports:read"))],
):
    tid = tenant_user["tenant_id"]
    total_orders = db.query(func.count(WorkOrder.id)).filter(WorkOrder.tenant_id == tid).scalar()
    total_time = db.query(func.count(WorkOrderTimeEntry.id)).filter(WorkOrderTimeEntry.tenant_id == tid).scalar()
    return {
        "work_orders": int(total_orders or 0),
        "time_entries": int(total_time or 0),
        "utilization_pct": Decimal("0"),
    }
