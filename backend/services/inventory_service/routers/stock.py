"""Stock movements and summary with tenant isolation and RBAC."""
import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Material, Warehouse, StockLot, StockMovement
from ..schemas.stock import StockMoveRequest, StockSummaryResponse, StockSummaryItem

router = APIRouter()


@router.post("/move", status_code=status.HTTP_201_CREATED)
def stock_move(
    db: DbSession,
    body: StockMoveRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:stock:write"))],
):
    """Record stock movement (in/out/transfer/adjust)."""
    tid = tenant_user["tenant_id"]
    # Ensure material and warehouse belong to tenant
    m = db.query(Material).filter(Material.id == body.material_id, Material.tenant_id == tid).first()
    if not m:
        raise HTTPException(status_code=404, detail="Material not found")
    w = db.query(Warehouse).filter(Warehouse.id == body.warehouse_id, Warehouse.tenant_id == tid).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    # Find or create stock lot
    lot = db.query(StockLot).filter(
        StockLot.tenant_id == tid,
        StockLot.material_id == body.material_id,
        StockLot.warehouse_id == body.warehouse_id,
    ).first()
    if not lot:
        lot = StockLot(
            id=str(uuid.uuid4()),
            tenant_id=tid,
            material_id=body.material_id,
            warehouse_id=body.warehouse_id,
            location_id=body.location_id,
            quantity=Decimal("0"),
            reserved_quantity=Decimal("0"),
        )
        db.add(lot)
        db.flush()

    new_qty = (lot.quantity or Decimal("0")) + body.quantity_delta
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    lot.quantity = new_qty

    movement = StockMovement(
        id=str(uuid.uuid4()),
        tenant_id=tid,
        material_id=body.material_id,
        warehouse_id=body.warehouse_id,
        location_id=body.location_id,
        quantity_delta=body.quantity_delta,
        movement_type=body.movement_type,
        reference_type=body.reference_type,
        reference_id=body.reference_id,
    )
    db.add(movement)
    db.commit()
    return {"id": movement.id, "material_id": body.material_id, "quantity_delta": str(body.quantity_delta), "movement_type": body.movement_type}


@router.get("/summary", response_model=StockSummaryResponse)
def stock_summary(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:stock:read"))],
    warehouse_id: str | None = None,
    material_id: str | None = None,
):
    """Get stock summary (optionally filtered by warehouse/material)."""
    tid = tenant_user["tenant_id"]
    q = db.query(
        StockLot.material_id,
        StockLot.warehouse_id,
        func.coalesce(StockLot.quantity, 0).label("quantity"),
        func.coalesce(StockLot.reserved_quantity, 0).label("reserved_quantity"),
    ).filter(StockLot.tenant_id == tid)
    if warehouse_id:
        q = q.filter(StockLot.warehouse_id == warehouse_id)
    if material_id:
        q = q.filter(StockLot.material_id == material_id)
    rows = q.all()
    materials = {m.id: m for m in db.query(Material).filter(Material.tenant_id == tid, Material.id.in_([r.material_id for r in rows])).all()}
    warehouses = {w.id: w for w in db.query(Warehouse).filter(Warehouse.tenant_id == tid, Warehouse.id.in_([r.warehouse_id for r in rows])).all()}
    items = []
    for r in rows:
        m = materials.get(r.material_id)
        w = warehouses.get(r.warehouse_id)
        items.append(StockSummaryItem(
            material_id=r.material_id,
            material_sku=m.sku if m else None,
            material_name=m.name if m else None,
            warehouse_id=r.warehouse_id,
            warehouse_name=w.name if w else None,
            quantity=r.quantity,
            reserved_quantity=r.reserved_quantity or Decimal("0"),
        ))
    return StockSummaryResponse(items=items, total_count=len(items))
