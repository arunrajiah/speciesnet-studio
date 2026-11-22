FROM python:3.11-slim

WORKDIR /app

# Install uv
# OpenCV (used by SpeciesNet's detector, when SpeciesNet is added to the image) needs these system libraries.
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv

# Install dependencies from lockfile into system Python (no virtualenv in Docker)
# Install into the image's system Python (uv sync otherwise makes /app/.venv, which is not on PATH)
ENV UV_PROJECT_ENVIRONMENT=/usr/local
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source and Alembic migrations
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini

# config/inference.yaml is user-provided and must be mounted as a volume at runtime:
#   -v ./config:/app/config   (docker run)
#   volumes: - ./config:/app/config   (compose)

ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
