"""Warehouses CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Warehouse
from ..schemas.warehouses import WarehouseCreate, WarehouseUpdate, WarehouseResponse

router = APIRouter()


@router.get("", response_model=list[WarehouseResponse])
def list_warehouses(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:warehouses:read"))],
):
    tid = tenant_user["tenant_id"]
    items = db.query(Warehouse).filter(Warehouse.tenant_id == tid).all()
    return [WarehouseResponse.model_validate(w) for w in items]


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(
    warehouse_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:warehouses:read"))],
):
    tid = tenant_user["tenant_id"]
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id, Warehouse.tenant_id == tid).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return WarehouseResponse.model_validate(w)


@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    db: DbSession,
    body: WarehouseCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:warehouses:write"))],
):
    tid = tenant_user["tenant_id"]
    wid = str(uuid.uuid4())
    w = Warehouse(
        id=wid,
        tenant_id=tid,
        name=body.name,
        code=body.code,
        address=body.address,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return WarehouseResponse.model_validate(w)


@router.patch("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: str,
    db: DbSession,
    body: WarehouseUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:warehouses:write"))],
):
    tid = tenant_user["tenant_id"]
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id, Warehouse.tenant_id == tid).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    if body.name is not None:
        w.name = body.name
    if body.code is not None:
        w.code = body.code
    if body.address is not None:
        w.address = body.address
    db.commit()
    db.refresh(w)
    return WarehouseResponse.model_validate(w)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(
    warehouse_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:warehouses:write"))],
):
    tid = tenant_user["tenant_id"]
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id, Warehouse.tenant_id == tid).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    db.delete(w)
    db.commit()
