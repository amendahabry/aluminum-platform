import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Add backend root and services to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from env
database_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
config.set_main_option("sqlalchemy.url", database_url)

# Import all models so Alembic can autogenerate (run with PYTHONPATH=backend or from backend/)
from shared.db.session import Base
from services.auth_service.models import Tenant, User, Role, Permission, UserRole, AuditLog, RefreshToken
from services.auth_service.models.role import role_permissions
from services.inventory_service.models import Material, AluminumProfile, Accessory, ScrapRecord, Warehouse, Location, StockLot, StockMovement, Reservation
from services.orders_service.models import (
    RFQ,
    RFQLine,
    Quote,
    QuoteLine,
    SalesOrder,
    SalesOrderLine,
    Invoice,
    Payment,
    Customer,
    PriceList,
    PriceListItem,
    DeliveryNote,
    DeliveryNoteLine,
    PurchaseOrder,
    PurchaseOrderLine,
)
from services.production_service.models import Machine, WorkOrder, WorkOrderTimeEntry

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
