---
name: HTTPException not wrapped in envelope
description: FastAPI HTTPException responses bypass ResponseEnvelopeMiddleware and AppException handler - test for raw detail field not envelope format
type: gotcha
---

When OAuth2 or other FastAPI dependencies raise HTTPException, the response is NOT wrapped in the standard envelope format (`{success, data/error}`). The response is raw FastAPI format: `{"detail": "..."}`.

**Why:** AppException handler in main.py only catches AppException subclasses. HTTPException is a FastAPI built-in and goes through FastAPI's default exception handler.

**How to apply:** In integration tests, check for HTTPException responses differently:
- AppException: `envelope["success"]`, `envelope["error"]["code"]`
- HTTPException: `data["detail"]` directly

Affected areas: OAuth2 token validation (401), permission checks (403), any dependency using FastAPI's HTTPException.
