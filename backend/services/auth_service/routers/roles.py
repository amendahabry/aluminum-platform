"""Roles and permissions CRUD with tenant isolation."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Role, Permission
from ..models.role import role_permissions
from ..schemas.roles import RoleCreate, RoleUpdate, RoleResponse, PermissionResponse, AssignPermissionsRequest

router = APIRouter()


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    db: DbSession,
    user: Annotated[dict, Depends(require_permission("auth:roles:read"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    perms = db.query(Permission).filter(Permission.tenant_id == tid).all()
    return [PermissionResponse(id=p.id, code=p.code, name=p.name) for p in perms]


@router.get("", response_model=list[RoleResponse])
def list_roles(
    db: DbSession,
    user: Annotated[dict, Depends(require_permission("auth:roles:read"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    roles = db.query(Role).filter(Role.tenant_id == tid).all()
    result = []
    for r in roles:
        stmt = select(role_permissions.c.permission_id).where(role_permissions.c.role_id == r.id)
        perm_ids = [row[0] for row in db.execute(stmt).fetchall()]
        perms = db.query(Permission).filter(Permission.id.in_(perm_ids)).all() if perm_ids else []
        result.append(RoleResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            tenant_id=r.tenant_id,
            permissions=[PermissionResponse(id=p.id, code=p.code, name=p.name) for p in perms],
        ))
    return result


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: str,
    db: DbSession,
    user: Annotated[dict, Depends(require_permission("auth:roles:read"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    r = db.query(Role).filter(Role.id == role_id, Role.tenant_id == tid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    stmt = select(role_permissions.c.permission_id).where(role_permissions.c.role_id == r.id)
    perm_ids = [row[0] for row in db.execute(stmt).fetchall()]
    perms = db.query(Permission).filter(Permission.id.in_(perm_ids)).all() if perm_ids else []
    return RoleResponse(
        id=r.id,
        name=r.name,
        description=r.description,
        tenant_id=r.tenant_id,
        permissions=[PermissionResponse(id=p.id, code=p.code, name=p.name) for p in perms],
    )


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    db: DbSession,
    body: RoleCreate,
    user: Annotated[dict, Depends(require_permission("auth:roles:write"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    if db.query(Role).filter(Role.tenant_id == tid, Role.name == body.name).first():
        raise HTTPException(status_code=400, detail="Role name already exists")
    from sqlalchemy import insert
    rid = str(uuid.uuid4())
    r = Role(id=rid, tenant_id=tid, name=body.name, description=body.description)
    db.add(r)
    db.commit()
    db.refresh(r)
    return get_role(rid, db, user, tenant_user)


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: str,
    db: DbSession,
    body: RoleUpdate,
    user: Annotated[dict, Depends(require_permission("auth:roles:write"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    r = db.query(Role).filter(Role.id == role_id, Role.tenant_id == tid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    if body.name is not None:
        r.name = body.name
    if body.description is not None:
        r.description = body.description
    db.commit()
    db.refresh(r)
    return get_role(role_id, db, user, tenant_user)


@router.post("/{role_id}/permissions", response_model=RoleResponse)
def assign_permissions(
    role_id: str,
    db: DbSession,
    body: AssignPermissionsRequest,
    user: Annotated[dict, Depends(require_permission("auth:roles:write"))],
    tenant_user: TenantUser,
):
    from sqlalchemy import insert
    tid = tenant_user["tenant_id"]
    r = db.query(Role).filter(Role.id == role_id, Role.tenant_id == tid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    # Remove existing and add new
    db.execute(delete(role_permissions).where(role_permissions.c.role_id == role_id))
    for pid in body.permission_ids:
        perm = db.query(Permission).filter(Permission.id == pid, Permission.tenant_id == tid).first()
        if perm:
            db.execute(insert(role_permissions).values(role_id=role_id, permission_id=pid))
    db.commit()
    return get_role(role_id, db, user, tenant_user)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: str,
    db: DbSession,
    user: Annotated[dict, Depends(require_permission("auth:roles:write"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    r = db.query(Role).filter(Role.id == role_id, Role.tenant_id == tid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    db.execute(delete(role_permissions).where(role_permissions.c.role_id == role_id))
    db.delete(r)
    db.commit()
