# CRM Application

Multi-tenant CRM SaaS platform covering the full sales workflow.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js v22.17.1 (npm 10.9.2)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Verify: `GET http://localhost:8000/health` returns `{"status":"ok","database":"connected"}`

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Settings
│   ├── database.py      # SQLAlchemy setup
│   ├── models/          # ORM models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── routers/         # API endpoints
│   └── core/security/   # Auth (populated by Authentication module)
├── alembic/             # Migrations
└── tests/

frontend/
├── src/
│   ├── components/      # Shared components
│   ├── features/        # Feature modules
│   ├── lib/             # Utilities (api, queryClient)
│   ├── routes/          # Routing
│   └── context/         # React contexts
└── ...
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
