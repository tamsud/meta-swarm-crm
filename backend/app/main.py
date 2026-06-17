"""FastAPI application factory and core routes."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import engine
from app.exceptions import AppException
from app.middleware import ResponseEnvelopeMiddleware
from app.routers import accounts, auth, contacts, mock_email, opportunities, permissions, roles, users


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

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTPException with envelope format."""
        # Map HTTP status codes to error codes
        error_code_map = {
            401: "UNAUTHORIZED",
            403: "INSUFFICIENT_PERMISSIONS",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            500: "INTERNAL_ERROR",
        }
        error_code = error_code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {"code": error_code, "message": exc.detail},
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with envelope format."""
        # Sanitize errors - convert non-serializable ctx values to strings
        sanitized_errors = []
        for error in exc.errors():
            sanitized_error = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": str(error.get("input")) if error.get("input") is not None else None,
            }
            # Convert ctx values to strings for JSON serialization
            if "ctx" in error and error["ctx"]:
                sanitized_error["ctx"] = {
                    k: str(v) if not isinstance(v, (str, int, float, bool, type(None), list, dict)) else v
                    for k, v in error["ctx"].items()
                }
            sanitized_errors.append(sanitized_error)

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": sanitized_errors,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle any unhandled exception with envelope format."""
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Unhandled exception in request")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred",
                },
            },
        )

    # Response envelope middleware (wraps all responses in standard format)
    # Added first so it runs after CORS middleware in request chain
    app.add_middleware(ResponseEnvelopeMiddleware)

    # CORS middleware - added last so it runs first (handles preflight OPTIONS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(accounts.router)
    app.include_router(auth.router)
    app.include_router(contacts.router)
    app.include_router(mock_email.router)
    app.include_router(opportunities.router)
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
