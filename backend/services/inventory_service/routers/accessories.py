"""Accessories and hardware inventory CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Accessory
from ..schemas.accessories import AccessoryCreate, AccessoryUpdate, AccessoryResponse

router = APIRouter()


@router.get("", response_model=list[AccessoryResponse])
def list_accessories(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:accessories:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(Accessory).filter(Accessory.tenant_id == tid).offset(skip).limit(limit).all()
    return [AccessoryResponse.model_validate(i) for i in items]


@router.get("/{accessory_id}", response_model=AccessoryResponse)
def get_accessory(
    accessory_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:accessories:read"))],
):
    tid = tenant_user["tenant_id"]
    accessory = db.query(Accessory).filter(Accessory.id == accessory_id, Accessory.tenant_id == tid).first()
    if not accessory:
        raise HTTPException(status_code=404, detail="Accessory not found")
    return AccessoryResponse.model_validate(accessory)


@router.post("", response_model=AccessoryResponse, status_code=status.HTTP_201_CREATED)
def create_accessory(
    db: DbSession,
    body: AccessoryCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:accessories:write"))],
):
    tid = tenant_user["tenant_id"]
    if db.query(Accessory).filter(Accessory.tenant_id == tid, Accessory.sku == body.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists in tenant")
    accessory_id = str(uuid.uuid4())
    accessory = Accessory(
        id=accessory_id,
        tenant_id=tid,
        sku=body.sku,
        name=body.name,
        category=body.category,
        unit=body.unit,
        cost=body.cost,
        notes=body.notes,
        is_active=True,
    )
    db.add(accessory)
    db.commit()
    db.refresh(accessory)
    return AccessoryResponse.model_validate(accessory)


@router.patch("/{accessory_id}", response_model=AccessoryResponse)
def update_accessory(
    accessory_id: str,
    db: DbSession,
    body: AccessoryUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:accessories:write"))],
):
    tid = tenant_user["tenant_id"]
    accessory = db.query(Accessory).filter(Accessory.id == accessory_id, Accessory.tenant_id == tid).first()
    if not accessory:
        raise HTTPException(status_code=404, detail="Accessory not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(accessory, field, value)
    db.commit()
    db.refresh(accessory)
    return AccessoryResponse.model_validate(accessory)


@router.delete("/{accessory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accessory(
    accessory_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:accessories:write"))],
):
    tid = tenant_user["tenant_id"]
    accessory = db.query(Accessory).filter(Accessory.id == accessory_id, Accessory.tenant_id == tid).first()
    if not accessory:
        raise HTTPException(status_code=404, detail="Accessory not found")
    db.delete(accessory)
    db.commit()
