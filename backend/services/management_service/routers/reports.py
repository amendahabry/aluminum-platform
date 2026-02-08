"""Management reports endpoints."""
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func

from shared.auth.deps import require_permission
from shared.db.session import get_db
from shared.tenants.middleware import set_tenant_context
from services.inventory_service.models import StockLot
from services.orders_service.models import SalesOrder

router = APIRouter()


@router.get("/overview")
def management_overview(
    tenant_user: Annotated[dict, Depends(require_permission("management:reports:read"))],
):
    tid = tenant_user["tenant_id"]
    set_tenant_context(tid)
    db = next(get_db())
    stock_lots = db.query(func.count(StockLot.id)).filter(StockLot.tenant_id == tid).scalar()
    sales_orders = db.query(func.count(SalesOrder.id)).filter(SalesOrder.tenant_id == tid).scalar()
    return {
        "stock_lots": int(stock_lots or 0),
        "sales_orders": int(sales_orders or 0),
        "inventory_aging": {
            "0-30": Decimal("0"),
            "31-60": Decimal("0"),
            "61-90": Decimal("0"),
            "90+": Decimal("0"),
        },
    }
