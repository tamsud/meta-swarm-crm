# Module Plan: Foundation Enhancements

**Module**: `foundation-enhancements` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

This module adds cross-cutting infrastructure rather than a new feature layer. It touches multiple existing layers:

```
backend/
├── app/
│   ├── schemas/
│   │   └── response.py       ← NEW: Envelope schemas (ApiResponse, ApiError, PaginatedResponse)
│   ├── middleware/
│   │   └── response_envelope.py  ← NEW: Middleware to wrap all responses
│   ├── routers/
│   │   ├── permissions.py    ← MODIFY: Remove manual envelope wrapping (middleware handles it)
│   │   └── roles.py          ← MODIFY: Remove _map_exception_to_http (middleware handles it)
│   └── seed.py               ← NEW: Basic seed script
├── Dockerfile                ← NEW: Development Dockerfile
└── README.md                 ← NEW: Backend documentation

frontend/
├── Dockerfile                ← NEW: Development Dockerfile
└── README.md                 ← MODIFY: Replace Vite boilerplate

root/
├── docker-compose.yml        ← NEW: Orchestrates both services
├── README.md                 ← NEW: Project overview and quick start
└── specs/
    └── mocks/                ← MOVED from root mocks/
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `schemas/response.py` | Pydantic models for `ApiResponse[T]`, `ApiError`, `PaginatedMeta` — defines the envelope contract |
| `middleware/response_envelope.py` | FastAPI middleware that intercepts all responses and wraps them in the envelope; catches exceptions and formats error responses |
| `routers/*.py` (existing) | Simplified — return raw data; middleware handles envelope wrapping |
| `exceptions.py` (existing) | Unchanged — still defines `AppException` with `status_code`, `error_code`, `extra` |
| `seed.py` | Idempotent script that creates minimal test data for implemented modules |
| `Dockerfile` (backend) | Python 3.11 image, installs deps, runs uvicorn with --reload |
| `Dockerfile` (frontend) | Node 22 image, installs deps, runs npm run dev with proper host binding |
| `docker-compose.yml` | Links backend + frontend, exposes ports, mounts source for live reload |
| `README.md` (root) | Project overview, tech stack, quick start for both Docker and native |
| `README.md` (backend) | Backend-specific setup, env vars, migrations, API docs |
| `README.md` (frontend) | Frontend-specific setup, folder structure, env vars |

## Data Flow: API Response Envelope

### Success Response Flow

```
[Router returns data]
   → Middleware intercepts response
   → Wraps in {"success": true, "data": <original_body>}
   → If list endpoint with pagination, adds "meta": {"count", "offset", "limit"}
   → Returns wrapped response
```

### Error Response Flow

```
[Service raises AppException]
   → Exception propagates to middleware
   → Middleware catches exception
   → Formats as {"success": false, "error": {"code": exc.error_code, "message": exc.detail, ...exc.extra}}
   → Sets status_code from exception
   → Returns error response

[Validation error (Pydantic)]
   → FastAPI's RequestValidationError
   → Middleware catches and formats as {"success": false, "error": {"code": "VALIDATION_ERROR", "message": "...", "details": [...]}}
   → Returns 422 response
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Permissions](../permissions/plan.md) | Router simplified — returns raw `list[PermissionResponse]`; middleware wraps |
| [Roles](../roles/plan.md) | Router simplified — removes `_map_exception_to_http`; middleware handles exceptions |
| All future CRM modules | Must return raw data from routers; middleware handles envelope automatically |
| [Deployment](../deployment/plan.md) | Production Dockerfiles extend/replace dev Dockerfiles; full seed extends basic seed |

---

## Architectural Decisions Specific to This Module

1. **Middleware-based envelope vs. explicit wrapping in each router**: Middleware approach chosen because:
   - Single point of change for envelope format
   - Routers stay focused on business logic
   - Consistent handling of all responses including errors
   - Easier to test envelope logic in isolation

2. **Generic `ApiResponse[T]` with TypeVar**: Enables OpenAPI schema generation to show the actual data type inside the envelope, not just `Any`.

3. **Development Docker separate from production Docker**: Dev Dockerfiles prioritize live reload and fast iteration; production Dockerfiles (Deployment module) will prioritize image size and security.

4. **Basic seed as a Python module, not CLI command initially**: Simpler implementation; can be run with `python -m app.seed`. Deployment module may add a proper CLI.

5. **Pagination meta in envelope, not headers**: Aligns with JSON:API-style responses; frontend can access pagination info from the same response object without parsing headers.

---

## Response Envelope Schema

### Success Response (single resource)

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Admin",
    "is_system": true,
    ...
  }
}
```

### Success Response (list with pagination)

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Admin", ...},
    {"id": 2, "name": "Manager", ...}
  ],
  "meta": {
    "count": 2,
    "total": 3,
    "offset": 0,
    "limit": 100
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "SYSTEM_ROLE_IMMUTABLE",
    "message": "System roles cannot be modified or deleted",
    "role_id": 1
  }
}
```

### Validation Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "loc": ["body", "name"],
        "msg": "Field required",
        "type": "missing"
      }
    ]
  }
}
```
