"""Tenant list/get (admin only)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Tenant
from ..schemas.tenants import TenantResponse

router = APIRouter()


@router.get("", response_model=list[TenantResponse])
def list_tenants(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("auth:users:read"))],
):
    """List tenant(s) the current user belongs to (tenant isolation)."""
    tid = tenant_user["tenant_id"]
    tenants = db.query(Tenant).filter(Tenant.id == tid).all()
    return [TenantResponse(id=t.id, name=t.name, slug=t.slug, is_active=t.is_active) for t in tenants]


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("auth:users:read"))],
):
    """Get tenant by ID (only own tenant)."""
    if tenant_id != tenant_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantResponse(id=t.id, name=t.name, slug=t.slug, is_active=t.is_active)
