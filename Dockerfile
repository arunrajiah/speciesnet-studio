# Multi-stage build producing a single image: FastAPI serves the Vite static build.
# The frontend is compiled at build time and served from FastAPI's StaticFiles mount.

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

COPY backend/pyproject.toml ./
RUN uv pip install --system \
    "fastapi>=0.115" "uvicorn[standard]" "pydantic>=2" \
    "sqlmodel>=0.0.21" pillow aiofiles pyyaml

COPY backend/src/ ./src/
COPY config/ ./config/

# Place built frontend under /app/frontend/dist so FastAPI can serve it
COPY --from=frontend-builder /app/dist ./frontend/dist

ENV PYTHONPATH=/app/src
ENV STATIC_DIR=/app/frontend/dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
