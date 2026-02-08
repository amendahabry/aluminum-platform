"""Inventory reports."""
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import StockLot, ScrapRecord

router = APIRouter()


@router.get("/aging")
def inventory_aging(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:reports:read"))],
):
    tid = tenant_user["tenant_id"]
    lot_count = db.query(func.count(StockLot.id)).filter(StockLot.tenant_id == tid).scalar()
    return {
        "lots": int(lot_count or 0),
        "aging_buckets": {
            "0-30": 0,
            "31-60": 0,
            "61-90": 0,
            "90+": 0,
        },
    }


@router.get("/scrap")
def scrap_report(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:reports:read"))],
):
    tid = tenant_user["tenant_id"]
    total_weight = db.query(func.coalesce(func.sum(ScrapRecord.weight_kg), 0)).filter(ScrapRecord.tenant_id == tid).scalar()
    return {
        "scrap_weight_kg": Decimal(total_weight or 0),
    }
