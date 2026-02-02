"""Database session factory with tenant-scoped queries."""
import os
from contextvars import ContextVar
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

Base = declarative_base()

# Context var for current tenant (set by middleware)
current_tenant_id: ContextVar[str | None] = ContextVar("current_tenant_id", default=None)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aluminum:aluminum@localhost:5432/aluminum",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a DB session with tenant filter applied."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (for services that own their schema)."""
    Base.metadata.create_all(bind=engine)


def get_current_tenant_id() -> str | None:
    """Return the tenant ID from request context."""
    return current_tenant_id.get()
