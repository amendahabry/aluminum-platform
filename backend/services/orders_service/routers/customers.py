"""Customers management with payment terms and credit limits."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Customer
from ..schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter()


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:customers:read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    tid = tenant_user["tenant_id"]
    items = db.query(Customer).filter(Customer.tenant_id == tid).offset(skip).limit(limit).all()
    return [CustomerResponse.model_validate(i) for i in items]


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:customers:read"))],
):
    tid = tenant_user["tenant_id"]
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.tenant_id == tid).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerResponse.model_validate(customer)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    db: DbSession,
    body: CustomerCreate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:customers:write"))],
):
    tid = tenant_user["tenant_id"]
    customer_id = str(uuid.uuid4())
    customer = Customer(
        id=customer_id,
        tenant_id=tid,
        name=body.name,
        email=body.email,
        phone=body.phone,
        payment_terms=body.payment_terms,
        credit_limit=body.credit_limit,
        billing_address=body.billing_address,
        shipping_address=body.shipping_address,
        is_active=body.is_active if body.is_active is not None else True,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: str,
    db: DbSession,
    body: CustomerUpdate,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:customers:write"))],
):
    tid = tenant_user["tenant_id"]
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.tenant_id == tid).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:customers:write"))],
):
    tid = tenant_user["tenant_id"]
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.tenant_id == tid).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
