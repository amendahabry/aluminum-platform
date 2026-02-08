"""Price lists per customer or group with line items."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import PriceList, PriceListItem
from ..schemas.price_list import PriceListCreate, PriceListUpdate, PriceListResponse, PriceListItemResponse

router = APIRouter()


def _to_response(price_list: PriceList, items: list[PriceListItem]) -> PriceListResponse:
    return PriceListResponse(
        id=price_list.id,
        tenant_id=price_list.tenant_id,
        name=price_list.name,
        customer_id=price_list.customer_id,
        customer_group=price_list.customer_group,
        valid_from=price_list.valid_from,
        valid_to=price_list.valid_to,
        notes=price_list.notes,
        items=[PriceListItemResponse.model_validate(i) for i in items],
    )


@router.get("", response_model=list[PriceListResponse])
def list_price_lists(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:pricelists:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(PriceList).filter(PriceList.tenant_id == tid).offset(skip).limit(limit).all()
    result = []
    for pl in items:
        lines = db.query(PriceListItem).filter(PriceListItem.tenant_id == tid, PriceListItem.price_list_id == pl.id).all()
        result.append(_to_response(pl, lines))
    return result


@router.get("/{price_list_id}", response_model=PriceListResponse)
def get_price_list(
    price_list_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:pricelists:read"))],
):
    tid = tenant_user["tenant_id"]
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id, PriceList.tenant_id == tid).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")
    lines = db.query(PriceListItem).filter(PriceListItem.tenant_id == tid, PriceListItem.price_list_id == price_list_id).all()
    return _to_response(price_list, lines)


@router.post("", response_model=PriceListResponse, status_code=status.HTTP_201_CREATED)
def create_price_list(
    db: DbSession,
    body: PriceListCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:pricelists:write"))],
):
    tid = tenant_user["tenant_id"]
    price_list_id = str(uuid.uuid4())
    price_list = PriceList(
        id=price_list_id,
        tenant_id=tid,
        name=body.name,
        customer_id=body.customer_id,
        customer_group=body.customer_group,
        valid_from=body.valid_from,
        valid_to=body.valid_to,
        notes=body.notes,
    )
    db.add(price_list)
    for item in body.items:
        item_id = str(uuid.uuid4())
        db.add(PriceListItem(
            id=item_id,
            tenant_id=tid,
            price_list_id=price_list_id,
            material_id=item.material_id,
            profile_id=item.profile_id,
            accessory_id=item.accessory_id,
            unit_price=item.unit_price,
            currency=item.currency,
        ))
    db.commit()
    db.refresh(price_list)
    lines = db.query(PriceListItem).filter(PriceListItem.tenant_id == tid, PriceListItem.price_list_id == price_list_id).all()
    return _to_response(price_list, lines)


@router.patch("/{price_list_id}", response_model=PriceListResponse)
def update_price_list(
    price_list_id: str,
    db: DbSession,
    body: PriceListUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:pricelists:write"))],
):
    tid = tenant_user["tenant_id"]
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id, PriceList.tenant_id == tid).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(price_list, field, value)
    db.commit()
    db.refresh(price_list)
    lines = db.query(PriceListItem).filter(PriceListItem.tenant_id == tid, PriceListItem.price_list_id == price_list_id).all()
    return _to_response(price_list, lines)


@router.delete("/{price_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price_list(
    price_list_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:pricelists:write"))],
):
    tid = tenant_user["tenant_id"]
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id, PriceList.tenant_id == tid).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")
    db.query(PriceListItem).filter(PriceListItem.tenant_id == tid, PriceListItem.price_list_id == price_list_id).delete()
    db.delete(price_list)
    db.commit()
