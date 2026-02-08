"""Machines management CRUD."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Machine
from ..schemas import MachineCreate, MachineUpdate, MachineResponse

router = APIRouter()


@router.get("", response_model=list[MachineResponse])
def list_machines(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:machines:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(Machine).filter(Machine.tenant_id == tid).offset(skip).limit(limit).all()
    return [MachineResponse.model_validate(i) for i in items]


@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine(
    machine_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:machines:read"))],
):
    tid = tenant_user["tenant_id"]
    machine = db.query(Machine).filter(Machine.id == machine_id, Machine.tenant_id == tid).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return MachineResponse.model_validate(machine)


@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def create_machine(
    db: DbSession,
    body: MachineCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:machines:write"))],
):
    tid = tenant_user["tenant_id"]
    machine_id = str(uuid.uuid4())
    machine = Machine(
        id=machine_id,
        tenant_id=tid,
        name=body.name,
        capacity_per_hour=body.capacity_per_hour,
        constraints=body.constraints,
        is_active=body.is_active if body.is_active is not None else True,
    )
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return MachineResponse.model_validate(machine)


@router.patch("/{machine_id}", response_model=MachineResponse)
def update_machine(
    machine_id: str,
    db: DbSession,
    body: MachineUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:machines:write"))],
):
    tid = tenant_user["tenant_id"]
    machine = db.query(Machine).filter(Machine.id == machine_id, Machine.tenant_id == tid).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(machine, field, value)
    db.commit()
    db.refresh(machine)
    return MachineResponse.model_validate(machine)


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(
    machine_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("production:machines:write"))],
):
    tid = tenant_user["tenant_id"]
    machine = db.query(Machine).filter(Machine.id == machine_id, Machine.tenant_id == tid).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(machine)
    db.commit()
