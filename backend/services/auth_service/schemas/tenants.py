from pydantic import BaseModel


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    is_active: bool

    class Config:
        from_attributes = True
