# Development Dockerfile for backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code (for initial layer, will be overridden by volume mount)
COPY . .

# Expose the API port
EXPOSE 8000

# Run migrations then start uvicorn with auto-reload for development
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
