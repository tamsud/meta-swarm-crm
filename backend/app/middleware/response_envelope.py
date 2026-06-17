"""Response envelope middleware for standardized API responses.

This middleware wraps successful responses in a standardized envelope format.
Exception handling is delegated to FastAPI's exception handlers (defined in main.py)
to avoid conflicts with Pydantic validation and other error handling.
"""

import json
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Middleware that wraps successful responses in a standardized envelope.

    Exception handling is NOT done here - it's delegated to FastAPI's
    exception handlers to avoid conflicts with Pydantic validation errors.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and wrap successful response in envelope.

        Most exceptions are handled by FastAPI's exception handlers (main.py).
        Only truly unhandled exceptions (generic Exception) are caught here
        to ensure they return the envelope format.
        """
        # Skip OPTIONS requests (CORS preflight) and certain paths
        if request.method == "OPTIONS" or self._should_skip(request.url.path):
            return await call_next(request)

        try:
            response = await call_next(request)
            return await self._wrap_success_response(response)
        except Exception as exc:
            # Catch only truly unhandled exceptions
            # Specific exceptions (HTTPException, AppException, etc.) are handled
            # by FastAPI's exception handlers before reaching here
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

    def _should_skip(self, path: str) -> bool:
        """Check if path should skip envelope wrapping."""
        return path in SKIP_PATHS or path.startswith("/docs") or path.startswith("/redoc")

    async def _wrap_success_response(self, response: Response) -> Response:
        """Wrap a successful response in the standard envelope."""
        if response.status_code >= 400:
            return response

        if not hasattr(response, "body_iterator"):
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        if not body:
            return Response(
                content=json.dumps({"success": True, "data": None}),
                status_code=response.status_code,
                media_type="application/json",
            )

        try:
            original_data = json.loads(body)
        except json.JSONDecodeError:
            return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
            )

        wrapped = self._build_success_envelope(original_data)

        return JSONResponse(
            content=wrapped,
            status_code=response.status_code,
        )

    def _build_success_envelope(self, data: any) -> dict:
        """Build success envelope, detecting paginated responses."""
        if isinstance(data, dict) and "items" in data and "meta" in data:
            return {
                "success": True,
                "data": data["items"],
                "meta": data["meta"],
            }
        return {"success": True, "data": data}
