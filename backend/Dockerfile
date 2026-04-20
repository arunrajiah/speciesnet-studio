FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies before copying source for better layer caching
COPY pyproject.toml ./
RUN uv pip install --system fastapi "uvicorn[standard]" "pydantic>=2"

# Copy source
COPY src/ ./src/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
