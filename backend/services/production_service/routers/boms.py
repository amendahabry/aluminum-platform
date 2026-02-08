"""BOM CRUD (stub) with tenant isolation."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from shared.auth.deps import require_permission
from ..deps import TenantUser

router = APIRouter()

# Stub storage (replace with DB + tenant_id)
_boms: dict[str, dict] = {}


class BOMCreate(BaseModel):
    name: str
    reference: str | None = None
    product_id: str | None = None


class BOMUpdate(BaseModel):
    name: str | None = None
    reference: str | None = None
    product_id: str | None = None


class BOMResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    reference: str | None
    product_id: str | None


@router.get("", response_model=list[BOMResponse])
def list_boms(
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:boms:read"))],
):
    tid = tenant_user["tenant_id"]
    return [BOMResponse(**b) for b in _boms.values() if b.get("tenant_id") == tid]


@router.get("/{bom_id}", response_model=BOMResponse)
def get_bom(
    bom_id: str,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:boms:read"))],
):
    tid = tenant_user["tenant_id"]
    if bom_id not in _boms or _boms[bom_id].get("tenant_id") != tid:
        raise HTTPException(status_code=404, detail="BOM not found")
    return BOMResponse(**_boms[bom_id])


@router.post("", response_model=BOMResponse, status_code=status.HTTP_201_CREATED)
def create_bom(
    body: BOMCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:boms:write"))],
):
    import uuid
    tid = tenant_user["tenant_id"]
    bom_id = str(uuid.uuid4())
    _boms[bom_id] = {
        "id": bom_id,
        "tenant_id": tid,
        "name": body.name,
        "reference": body.reference,
        "product_id": body.product_id,
    }
    return BOMResponse(**_boms[bom_id])


@router.patch("/{bom_id}", response_model=BOMResponse)
def update_bom(
    bom_id: str,
    body: BOMUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:boms:write"))],
):
    tid = tenant_user["tenant_id"]
    if bom_id not in _boms or _boms[bom_id].get("tenant_id") != tid:
        raise HTTPException(status_code=404, detail="BOM not found")
    if body.name is not None:
        _boms[bom_id]["name"] = body.name
    if body.reference is not None:
        _boms[bom_id]["reference"] = body.reference
    if body.product_id is not None:
        _boms[bom_id]["product_id"] = body.product_id
    return BOMResponse(**_boms[bom_id])


@router.delete("/{bom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bom(
    bom_id: str,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:boms:write"))],
):
    tid = tenant_user["tenant_id"]
    if bom_id not in _boms or _boms[bom_id].get("tenant_id") != tid:
        raise HTTPException(status_code=404, detail="BOM not found")
    del _boms[bom_id]
