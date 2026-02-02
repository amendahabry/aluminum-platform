"""Cut list generation (stub with realistic response)."""
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from shared.auth.deps import require_permission
from ..deps import TenantUser

router = APIRouter()


class CutListGenerateRequest(BaseModel):
    bom_id: str
    stock_length_mm: float = 6000.0
    kerf_mm: float = 3.0
    optimize: bool = True


class CutPlanItem(BaseModel):
    length_mm: float
    quantity: int
    waste_mm: float
    from_stock_id: str


class CutListGenerateResponse(BaseModel):
    cutlist_id: str
    bom_id: str
    total_stock_used: int
    total_waste_mm: float
    utilization_pct: float
    cuts: list[CutPlanItem]
    status: str = "completed"


@router.post("/generate", response_model=CutListGenerateResponse)
def generate_cutlist(
    body: CutListGenerateRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:cutlists:write"))],
):
    """Stub: returns a realistic cut plan structure."""
    import uuid
    # Realistic stub response
    return CutListGenerateResponse(
        cutlist_id=str(uuid.uuid4()),
        bom_id=body.bom_id,
        total_stock_used=5,
        total_waste_mm=450.0,
        utilization_pct=92.5,
        cuts=[
            CutPlanItem(length_mm=2400.0, quantity=2, waste_mm=120.0, from_stock_id="STK-001"),
            CutPlanItem(length_mm=1800.0, quantity=3, waste_mm=90.0, from_stock_id="STK-002"),
        ],
        status="completed",
    )
