"""Response envelope middleware for standardized API responses."""

import json
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.exceptions import AppException

logger = logging.getLogger(__name__)

SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Middleware that wraps all responses in a standardized envelope."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and wrap response in envelope."""
        # Skip OPTIONS requests (CORS preflight) and certain paths
        if request.method == "OPTIONS" or self._should_skip(request.url.path):
            return await call_next(request)

        try:
            response = await call_next(request)
            return await self._wrap_success_response(response)
        except AppException as exc:
            return self._create_error_response(exc)
        except RequestValidationError as exc:
            return self._create_validation_error_response(exc)
        except Exception as exc:
            logger.exception("Unhandled exception in request")
            return self._create_internal_error_response(exc)

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

    def _create_error_response(self, exc: AppException) -> JSONResponse:
        """Create error response from AppException."""
        error_body = {
            "code": exc.error_code,
            "message": exc.detail,
        }
        if exc.extra:
            error_body.update(exc.extra)

        return JSONResponse(
            content={"success": False, "error": error_body},
            status_code=exc.status_code,
        )

    def _create_validation_error_response(
        self, exc: RequestValidationError
    ) -> JSONResponse:
        """Create error response from validation error."""
        return JSONResponse(
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
            },
            status_code=422,
        )

    def _create_internal_error_response(self, exc: Exception) -> JSONResponse:
        """Create error response for unhandled exceptions."""
        return JSONResponse(
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred",
                },
            },
            status_code=500,
        )
