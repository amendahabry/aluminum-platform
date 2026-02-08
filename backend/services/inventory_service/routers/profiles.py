"""Aluminum profiles catalog CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import AluminumProfile
from ..schemas.profiles import AluminumProfileCreate, AluminumProfileUpdate, AluminumProfileResponse

router = APIRouter()


@router.get("", response_model=list[AluminumProfileResponse])
def list_profiles(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:profiles:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(AluminumProfile).filter(AluminumProfile.tenant_id == tid).offset(skip).limit(limit).all()
    return [AluminumProfileResponse.model_validate(i) for i in items]


@router.get("/{profile_id}", response_model=AluminumProfileResponse)
def get_profile(
    profile_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:profiles:read"))],
):
    tid = tenant_user["tenant_id"]
    profile = db.query(AluminumProfile).filter(AluminumProfile.id == profile_id, AluminumProfile.tenant_id == tid).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return AluminumProfileResponse.model_validate(profile)


@router.post("", response_model=AluminumProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    db: DbSession,
    body: AluminumProfileCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:profiles:write"))],
):
    tid = tenant_user["tenant_id"]
    profile_id = str(uuid.uuid4())
    profile = AluminumProfile(
        id=profile_id,
        tenant_id=tid,
        series=body.series,
        alloy=body.alloy,
        temper=body.temper,
        weight_per_meter=body.weight_per_meter,
        cost_per_meter=body.cost_per_meter,
        description=body.description,
        is_active=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return AluminumProfileResponse.model_validate(profile)


@router.patch("/{profile_id}", response_model=AluminumProfileResponse)
def update_profile(
    profile_id: str,
    db: DbSession,
    body: AluminumProfileUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:profiles:write"))],
):
    tid = tenant_user["tenant_id"]
    profile = db.query(AluminumProfile).filter(AluminumProfile.id == profile_id, AluminumProfile.tenant_id == tid).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return AluminumProfileResponse.model_validate(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    profile_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("inventory:profiles:write"))],
):
    tid = tenant_user["tenant_id"]
    profile = db.query(AluminumProfile).filter(AluminumProfile.id == profile_id, AluminumProfile.tenant_id == tid).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
