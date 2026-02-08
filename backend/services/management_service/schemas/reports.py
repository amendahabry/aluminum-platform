from decimal import Decimal
from pydantic import BaseModel


class ManagementOverviewResponse(BaseModel):
    stock_lots: int
    sales_orders: int
    inventory_aging: dict[str, Decimal]
