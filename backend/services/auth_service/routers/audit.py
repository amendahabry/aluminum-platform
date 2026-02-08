"""Audit log read-only endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import AuditLog

router = APIRouter()


@router.get("", response_model=list[dict])
def list_audit_logs(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("audit:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(AuditLog).filter(AuditLog.tenant_id == tid).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": i.id,
            "user_id": i.user_id,
            "action": i.action,
            "resource_type": i.resource_type,
            "resource_id": i.resource_id,
            "details": i.details,
            "created_at": i.created_at,
        }
        for i in items
    ]
