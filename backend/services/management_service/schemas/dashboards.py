from decimal import Decimal
from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    profit: Decimal
    scrap_pct: Decimal
    utilization: Decimal
    work_orders: int
