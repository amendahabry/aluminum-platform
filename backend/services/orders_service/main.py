"""Orders service: RFQ, quotes, sales orders, invoices."""
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from shared.logging_utils import setup_logging, bind_request_id, get_logger
from shared.tenants.middleware import TenantContextMiddleware
from .routers import rfqs, quotes, sales_orders, invoices

SERVICE_NAME = "orders_service"
setup_logging(SERVICE_NAME, os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aluminum Orders Service",
        version="1.0.0",
        openapi_tags=[
            {"name": "rfqs", "description": "Request for Quote"},
            {"name": "quotes", "description": "Quotes and approval"},
            {"name": "sales-orders", "description": "Sales orders"},
            {"name": "invoices", "description": "Invoices"},
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

    app.include_router(rfqs.router, prefix="/rfqs", tags=["rfqs"])
    app.include_router(quotes.router, prefix="/quotes", tags=["quotes"])
    app.include_router(sales_orders.router, prefix="/sales-orders", tags=["sales-orders"])
    app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])

    @app.get("/health")
    def health():
        return {"status": "ok", "service": SERVICE_NAME, "version": "1.0.0"}

    @app.get("/ready")
    def ready():
        from sqlalchemy import text
        from shared.db.session import engine
        try:
            with engine.connect() as c:
                c.execute(text("SELECT 1"))
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
        return {"status": "ready", "service": SERVICE_NAME}

    return app


app = create_app()
