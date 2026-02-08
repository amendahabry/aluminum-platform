"""API Gateway: proxy to auth, inventory, orders, production, ai, notification services."""
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest

from shared.logging_utils import setup_logging, bind_request_id, get_logger

SERVICE_NAME = "gateway"
setup_logging(SERVICE_NAME, os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory_service:8001")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://orders_service:8002")
PRODUCTION_SERVICE_URL = os.getenv("PRODUCTION_SERVICE_URL", "http://production_service:8003")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai_service:8004")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification_service:8005")
MANAGEMENT_SERVICE_URL = os.getenv("MANAGEMENT_SERVICE_URL", "http://management_service:8006")


async def proxy_request(service_url: str, path: str, request: StarletteRequest) -> JSONResponse:
    """Forward request to service and return response."""
    method = request.method
    headers = dict(request.headers)
    # Drop hop-by-hop and host
    for h in ("host", "connection", "content-length"):
        headers.pop(h, None)
    rid = getattr(request.state, "request_id", None) or bind_request_id()
    headers["X-Request-ID"] = rid
    url = f"{service_url.rstrip('/')}{path}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                resp = await client.get(url, headers=headers, params=dict(request.query_params))
            elif method == "POST":
                body = await request.body()
                resp = await client.post(url, headers=headers, content=body)
            elif method == "PUT":
                body = await request.body()
                resp = await client.put(url, headers=headers, content=body)
            elif method == "PATCH":
                body = await request.body()
                resp = await client.patch(url, headers=headers, content=body)
            elif method == "DELETE":
                resp = await client.delete(url, headers=headers)
            else:
                return JSONResponse({"detail": "Method not allowed"}, status_code=405)
            # Forward response
            try:
                data = resp.json()
            except Exception:
                data = resp.text
            return JSONResponse(content=data if isinstance(data, dict) else {"content": data}, status_code=resp.status_code)
    except httpx.ConnectError as e:
        logger.warning("gateway connect error: %s", e)
        return JSONResponse({"detail": "Service unavailable"}, status_code=503)
    except Exception as e:
        logger.exception("gateway error: %s", e)
        return JSONResponse({"detail": str(e)}, status_code=502)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aluminum API Gateway",
        version="1.0.0",
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

    # Health
    @app.get("/health")
    def health():
        return {"status": "ok", "service": SERVICE_NAME, "version": "1.0.0"}

    # Auth routes -> auth_service
    @app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def auth_proxy(request: Request, path: str):
        return await proxy_request(AUTH_SERVICE_URL, f"/auth/{path}", request)

    @app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def users_proxy(request: Request, path: str):
        return await proxy_request(AUTH_SERVICE_URL, f"/users/{path}", request)

    @app.api_route("/roles/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def roles_proxy(request: Request, path: str):
        return await proxy_request(AUTH_SERVICE_URL, f"/roles/{path}", request)

    @app.api_route("/audit/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def audit_proxy(request: Request, path: str):
        return await proxy_request(AUTH_SERVICE_URL, f"/audit/{path}", request)

    @app.api_route("/tenants/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def tenants_proxy(request: Request, path: str):
        return await proxy_request(AUTH_SERVICE_URL, f"/tenants/{path}", request)

    # Inventory
    @app.api_route("/materials/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def materials_proxy(request: Request, path: str):
        return await proxy_request(INVENTORY_SERVICE_URL, f"/materials/{path}", request)

    @app.api_route("/warehouses/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def warehouses_proxy(request: Request, path: str):
        return await proxy_request(INVENTORY_SERVICE_URL, f"/warehouses/{path}", request)

    @app.api_route("/profiles/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def profiles_proxy(request: Request, path: str):
        return await proxy_request(INVENTORY_SERVICE_URL, f"/profiles/{path}", request)

    @app.api_route("/accessories/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def accessories_proxy(request: Request, path: str):
        return await proxy_request(INVENTORY_SERVICE_URL, f"/accessories/{path}", request)

    @app.api_route("/scrap/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def scrap_proxy(request: Request, path: str):
        return await proxy_request(INVENTORY_SERVICE_URL, f"/scrap/{path}", request)

    @app.api_route("/inventory-reports/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def inventory_reports_proxy(request: Request, path: str):
        return await proxy_request(INVENTORY_SERVICE_URL, f"/reports/{path}", request)

    @app.api_route("/stock/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def stock_proxy(request: Request, path: str):
        return await proxy_request(INVENTORY_SERVICE_URL, f"/stock/{path}", request)

    # Orders
    @app.api_route("/rfqs/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def rfqs_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/rfqs/{path}", request)

    @app.api_route("/quotes/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def quotes_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/quotes/{path}", request)

    @app.api_route("/customers/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def customers_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/customers/{path}", request)

    @app.api_route("/price-lists/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def price_lists_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/price-lists/{path}", request)

    @app.api_route("/sales-orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def sales_orders_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/sales-orders/{path}", request)

    @app.api_route("/delivery-notes/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def delivery_notes_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/delivery-notes/{path}", request)

    @app.api_route("/invoices/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def invoices_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/invoices/{path}", request)

    @app.api_route("/purchase-orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def purchase_orders_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/purchase-orders/{path}", request)

    @app.api_route("/reports/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def reports_proxy(request: Request, path: str):
        return await proxy_request(ORDERS_SERVICE_URL, f"/reports/{path}", request)

    @app.api_route("/production/reports/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def prod_reports_proxy(request: Request, path: str):
        return await proxy_request(PRODUCTION_SERVICE_URL, f"/reports/{path}", request)

    # Production
    @app.api_route("/boms/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def boms_proxy(request: Request, path: str):
        return await proxy_request(PRODUCTION_SERVICE_URL, f"/boms/{path}", request)

    @app.api_route("/cutlists/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def cutlists_proxy(request: Request, path: str):
        return await proxy_request(PRODUCTION_SERVICE_URL, f"/cutlists/{path}", request)

    @app.api_route("/work-orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def work_orders_proxy(request: Request, path: str):
        return await proxy_request(PRODUCTION_SERVICE_URL, f"/work-orders/{path}", request)

    @app.api_route("/machines/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def machines_proxy(request: Request, path: str):
        return await proxy_request(PRODUCTION_SERVICE_URL, f"/machines/{path}", request)

    @app.api_route("/time-entries/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def time_entries_proxy(request: Request, path: str):
        return await proxy_request(PRODUCTION_SERVICE_URL, f"/time-entries/{path}", request)


    # AI
    @app.api_route("/ai/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def ai_proxy(request: Request, path: str):
        return await proxy_request(AI_SERVICE_URL, f"/ai/{path}", request)

    # Notifications
    @app.api_route("/notify/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def notify_proxy(request: Request, path: str):
        return await proxy_request(NOTIFICATION_SERVICE_URL, f"/notify/{path}", request)

    # Management
    @app.api_route("/dashboards/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def dashboards_proxy(request: Request, path: str):
        return await proxy_request(MANAGEMENT_SERVICE_URL, f"/dashboards/{path}", request)

    @app.api_route("/management-reports/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def management_reports_proxy(request: Request, path: str):
        return await proxy_request(MANAGEMENT_SERVICE_URL, f"/reports/{path}", request)

    # Catch-all for /auth (no path)
    @app.api_route("/auth", methods=["GET", "POST"])
    async def auth_root_proxy(request: Request):
        return await proxy_request(AUTH_SERVICE_URL, "/auth", request)

    return app


app = create_app()
