# CRM Backend

FastAPI backend for the Meta Swarm CRM platform.

## Prerequisites

- Python 3.11+
- SQLite (default) or PostgreSQL

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=sqlite+aiosqlite:///./crm.db
SECRET_KEY=your-secret-key-here
```

## Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Running the Server

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

When running, interactive docs are available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # Database configuration
│   ├── exceptions.py     # Custom exception classes
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic layer
│   ├── routers/          # API route handlers
│   └── middleware/       # Request/response middleware
├── alembic/              # Database migrations
├── tests/                # Pytest test suite
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_roles_integration.py
```

## Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy app
```
