# Production single-image build.
# FastAPI serves both the API and the compiled Vite frontend from one container.
# Use docker-compose.prod.yml or run directly:
#   docker build -t speciesnet-studio .
#   docker run -p 8000:8000 -v $(pwd)/data:/app/data speciesnet-studio

# ── stage 1: build frontend ───────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app
RUN npm install -g pnpm

COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./
RUN pnpm build
# Output: /app/dist

# ── stage 2: backend + bundled frontend ───────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies from the lockfile into system Python (no virtualenv in Docker)
ENV UV_SYSTEM_PYTHON=1
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source, alembic migrations, and default config
COPY backend/src/ ./src/
COPY backend/alembic/ ./alembic/
COPY backend/alembic.ini ./alembic.ini
COPY config/ ./config/

# Compiled frontend served by FastAPI StaticFiles
COPY --from=frontend-builder /app/dist ./frontend/dist

ENV PYTHONPATH=/app/src
ENV STATIC_DIR=/app/frontend/dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
