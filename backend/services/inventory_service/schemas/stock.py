from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class StockMoveRequest(BaseModel):
    material_id: str
    warehouse_id: str
    location_id: Optional[str] = None
    quantity_delta: Decimal  # positive = in, negative = out
    movement_type: str  # in, out, transfer, adjust
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None


class StockSummaryItem(BaseModel):
    material_id: str
    material_sku: Optional[str] = None
    material_name: Optional[str] = None
    warehouse_id: str
    warehouse_name: Optional[str] = None
    quantity: Decimal
    reserved_quantity: Decimal


class StockSummaryResponse(BaseModel):
    items: list[StockSummaryItem]
    total_count: int
