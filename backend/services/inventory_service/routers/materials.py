"""Materials CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Material
from ..schemas.materials import MaterialCreate, MaterialUpdate, MaterialResponse

router = APIRouter()


@router.get("", response_model=list[MaterialResponse])
def list_materials(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:materials:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(Material).filter(Material.tenant_id == tid).offset(skip).limit(limit).all()
    return [MaterialResponse.model_validate(m) for m in items]


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:materials:read"))],
):
    tid = tenant_user["tenant_id"]
    m = db.query(Material).filter(Material.id == material_id, Material.tenant_id == tid).first()
    if not m:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialResponse.model_validate(m)


@router.post("", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(
    db: DbSession,
    body: MaterialCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:materials:write"))],
):
    tid = tenant_user["tenant_id"]
    if db.query(Material).filter(Material.tenant_id == tid, Material.sku == body.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists in tenant")
    mid = str(uuid.uuid4())
    m = Material(
        id=mid,
        tenant_id=tid,
        sku=body.sku,
        name=body.name,
        description=body.description,
        unit=body.unit,
        weight_kg=body.weight_kg,
        category=body.category,
        cost_per_unit=body.cost_per_unit,
        is_active=True,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return MaterialResponse.model_validate(m)


@router.patch("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: str,
    db: DbSession,
    body: MaterialUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:materials:write"))],
):
    tid = tenant_user["tenant_id"]
    m = db.query(Material).filter(Material.id == material_id, Material.tenant_id == tid).first()
    if not m:
        raise HTTPException(status_code=404, detail="Material not found")
    if body.name is not None:
        m.name = body.name
    if body.description is not None:
        m.description = body.description
    if body.unit is not None:
        m.unit = body.unit
    if body.weight_kg is not None:
        m.weight_kg = body.weight_kg
    if body.category is not None:
        m.category = body.category
    if body.cost_per_unit is not None:
        m.cost_per_unit = body.cost_per_unit
    db.commit()
    db.refresh(m)
    return MaterialResponse.model_validate(m)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:materials:write"))],
):
    tid = tenant_user["tenant_id"]
    m = db.query(Material).filter(Material.id == material_id, Material.tenant_id == tid).first()
    if not m:
        raise HTTPException(status_code=404, detail="Material not found")
    db.delete(m)
    db.commit()
