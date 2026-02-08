"""Orders service: RFQ, quotes, sales orders, invoices."""
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from shared.logging_utils import setup_logging, bind_request_id, get_logger
from shared.tenants.middleware import TenantContextMiddleware
from .routers import rfqs, quotes, sales_orders, invoices, customers, price_lists, delivery_notes, purchase_orders, reports, quotes_conversion, invoices_pdf

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
            {"name": "customers", "description": "Customers and payment terms"},
            {"name": "price-lists", "description": "Customer price lists"},
            {"name": "sales-orders", "description": "Sales orders"},
            {"name": "delivery-notes", "description": "Delivery notes"},
            {"name": "invoices", "description": "Invoices"},
            {"name": "purchase-orders", "description": "Supplier purchase orders"},
            {"name": "reports", "description": "Orders reports"},
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
    app.include_router(quotes_conversion.router, prefix="/quotes", tags=["quotes"])
    app.include_router(sales_orders.router, prefix="/sales-orders", tags=["sales-orders"])
    app.include_router(customers.router, prefix="/customers", tags=["customers"])
    app.include_router(price_lists.router, prefix="/price-lists", tags=["price-lists"])
    app.include_router(delivery_notes.router, prefix="/delivery-notes", tags=["delivery-notes"])
    app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
    app.include_router(invoices_pdf.router, prefix="/invoices", tags=["invoices"])
    app.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["purchase-orders"])
    app.include_router(reports.router, prefix="/reports", tags=["reports"])

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
