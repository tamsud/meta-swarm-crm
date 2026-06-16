# Meta Swarm CRM

A multi-tenant-ready CRM SaaS platform covering the full sales workflow — lead capture through qualification, conversion, pipeline management, and engagement history.

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy 2.x (async) / Pydantic v2
- **Frontend**: React 18 + Vite + TypeScript + TailwindCSS
- **Database**: SQLite (dev) / PostgreSQL (prod)

## Quick Start (Docker)

```bash
# Start all services
docker compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

## Quick Start (Native)

### Prerequisites

- Python 3.11+
- Node.js v22.17.1 (npm 10.9.2)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Verify: `GET http://localhost:8000/health` returns `{"status":"ok","database":"connected"}`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173

## Project Structure

```
├── backend/           # FastAPI backend (see backend/README.md)
├── frontend/          # React frontend (see frontend/README.md)
├── specs/             # Module specifications and UI mocks
│   ├── mocks/         # Exported HTML/CSS UI reference
│   └── <module>/      # Spec, plan, and tasks per module
└── docker-compose.yml # Development orchestration
```

## API Response Format

All API endpoints return a standardized envelope:

```json
// Success (single item)
{"success": true, "data": {...}}

// Success (list with pagination)
{"success": true, "data": [...], "meta": {"count": 10, "total": 100, "offset": 0, "limit": 10}}

// Error
{"success": false, "error": {"code": "ERROR_CODE", "message": "Human-readable message"}}
```

## Development

Run tests:
```bash
cd backend && pytest
```

Run lints:
```bash
cd backend && ruff check .
cd frontend && npm run lint
```

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Module Specifications](specs/)
