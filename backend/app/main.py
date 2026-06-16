"""FastAPI application factory and core routes."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import engine
from app.exceptions import AppException
from app.middleware import ResponseEnvelopeMiddleware
from app.routers import accounts, auth, permissions, roles, users


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan handler."""
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="CRM API",
        description="Multi-tenant CRM SaaS platform API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle AppException with envelope format."""
        error_body = {"code": exc.error_code, "message": exc.detail}
        if exc.extra:
            error_body.update(exc.extra)
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": error_body},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with envelope format."""
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
            },
        )

    # Response envelope middleware (wraps all responses in standard format)
    # Added first so it runs after CORS middleware in request chain
    app.add_middleware(ResponseEnvelopeMiddleware)

    # CORS middleware - added last so it runs first (handles preflight OPTIONS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(accounts.router)
    app.include_router(auth.router)
    app.include_router(permissions.router)
    app.include_router(roles.router)
    app.include_router(users.router)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint confirming database connectivity."""
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}
        except Exception as e:
            return {"status": "error", "database": str(e)}

    return app


app = create_app()
