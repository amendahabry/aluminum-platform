from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: str
    code: str
    name: str | None


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    tenant_id: str
    permissions: list[PermissionResponse] | list[str]

    class Config:
        from_attributes = True


class AssignPermissionsRequest(BaseModel):
    permission_ids: list[str]
