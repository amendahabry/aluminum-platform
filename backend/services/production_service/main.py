"""Production service: BOM, cut list, work orders (stubs with realistic responses)."""
import os
import uuid
from typing import Annotated

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.logging_utils import setup_logging, bind_request_id, get_logger
from shared.tenants.middleware import TenantContextMiddleware
from .routers import boms, cutlists, work_orders

SERVICE_NAME = "production_service"
setup_logging(SERVICE_NAME, os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aluminum Production Service",
        version="1.0.0",
        openapi_tags=[
            {"name": "boms", "description": "Bill of Materials"},
            {"name": "cutlists", "description": "Cut list generation (stub)"},
            {"name": "work-orders", "description": "Work orders"},
        ],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or bind_request_id()
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response

    async def auth_middleware(request: Request, call_next):
        from fastapi.security import HTTPBearer
        security = HTTPBearer(auto_error=False)
        creds = await security(request)
        if creds:
            from shared.auth.jwt import verify_token
            payload = verify_token(creds.credentials)
            if payload and payload.get("type") == "access":
                request.state.user = payload
        if not hasattr(request.state, "user"):
            request.state.user = None
        return await call_next(request)

    app.middleware("http")(auth_middleware)
    app.add_middleware(TenantContextMiddleware)

    app.include_router(boms.router, prefix="/boms", tags=["boms"])
    app.include_router(cutlists.router, prefix="/cutlists", tags=["cutlists"])
    app.include_router(work_orders.router, prefix="/work-orders", tags=["work-orders"])

    @app.get("/health")
    def health():
        return {"status": "ok", "service": SERVICE_NAME, "version": "1.0.0"}

    @app.get("/ready")
    def ready():
        return {"status": "ready", "service": SERVICE_NAME}

    return app


app = create_app()
