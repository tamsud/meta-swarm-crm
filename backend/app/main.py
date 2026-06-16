"""FastAPI application factory and core routes."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine
from app.middleware import ResponseEnvelopeMiddleware
from app.routers import permissions, roles


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Response envelope middleware (wraps all responses in standard format)
    app.add_middleware(ResponseEnvelopeMiddleware)

    # Register routers
    app.include_router(permissions.router)
    app.include_router(roles.router)

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
