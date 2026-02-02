"""AI service: cut optimization, quote assistant, OCR, NLQ (stubs with interfaces)."""
import os
import uuid
from typing import Annotated

from fastapi import FastAPI, Request, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.logging_utils import setup_logging, bind_request_id, get_logger
from shared.tenants.middleware import TenantContextMiddleware

SERVICE_NAME = "ai_service"
setup_logging(SERVICE_NAME, os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aluminum AI Service",
        version="1.0.0",
        openapi_tags=[
            {"name": "ai", "description": "Cut optimize, quote assistant, OCR, NLQ stubs"},
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

    from .routers import ai
    app.include_router(ai.router, prefix="/ai", tags=["ai"])

    @app.get("/health")
    def health():
        return {"status": "ok", "service": SERVICE_NAME, "version": "1.0.0"}

    @app.get("/ready")
    def ready():
        return {"status": "ready", "service": SERVICE_NAME}

    return app


app = create_app()
