"""Auth service: tenants, users, roles, JWT, refresh tokens."""
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.logging_utils import setup_logging, bind_request_id, get_logger
from shared.tenants.middleware import TenantContextMiddleware
from shared.auth.deps import get_current_user, get_optional_user
from .routers import auth, users, roles, tenants

SERVICE_NAME = "auth_service"
setup_logging(SERVICE_NAME, os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB migrations are run elsewhere
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aluminum Auth Service",
        version="1.0.0",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "auth", "description": "Login, refresh, register tenant"},
            {"name": "users", "description": "User CRUD"},
            {"name": "roles", "description": "Roles and permissions"},
            {"name": "tenants", "description": "Tenant management"},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID + tenant context (tenant set after auth in router deps)
    @app.middleware("http")
    async def request_id_and_tenant(request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or bind_request_id()
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response

    # Auth middleware: parse JWT and set request.state.user for protected routes
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

    # Rate limiting via slowapi (optional, add if desired)
    # from slowapi import Limiter; limiter = Limiter(key_func=get_remote_address)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(roles.router, prefix="/roles", tags=["roles"])
    app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok", "service": SERVICE_NAME, "version": "1.0.0"}

    @app.get("/ready", tags=["health"])
    def ready():
        from sqlalchemy import text
        from shared.db.session import engine
        try:
            with engine.connect() as c:
                c.execute(text("SELECT 1"))
        except Exception as e:
            return JSONResponse({"status": "unhealthy", "error": str(e)}, status_code=503)
        return {"status": "ready", "service": SERVICE_NAME}

    return app


app = create_app()
