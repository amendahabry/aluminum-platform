import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# -------------------------------------------------
# Ensure backend/ is on PYTHONPATH
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# -------------------------------------------------
# Alembic config
# -------------------------------------------------
config = context.config

# Override DB URL from environment (Docker-safe)
config.set_main_option(
    "sqlalchemy.url",
    os.environ["DATABASE_URL"]
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------
# Import ALL model modules so Base.metadata is complete
# -------------------------------------------------
from shared.db import Base  # ← this is where Base SHOULD live

# Import models to register them
from services.auth_service import models as auth_models
from services.inventory_service import models as inventory_models
from services.orders_service import models as orders_models
from services.production_service import models as production_models
from services.management_service import models as management_models
# ai / notification usually don’t have DB models – skip if true

target_metadata = Base.metadata

# -------------------------------------------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
