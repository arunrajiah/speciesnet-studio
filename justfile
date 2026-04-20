default:
    @just --list

# Start all services via Docker Compose
dev:
    docker compose up

# Build and restart all services
build:
    docker compose up --build

# Stop all services
down:
    docker compose down

# Install all dependencies
install:
    cd backend && uv sync --group dev
    cd frontend && pnpm install

# Run all tests
test: test-backend

# Run backend tests
test-backend:
    cd backend && uv run pytest -v

# Run all linters
lint: lint-backend lint-frontend

# Lint backend (ruff + mypy)
lint-backend:
    cd backend && uv run ruff check .
    cd backend && uv run ruff format --check .
    cd backend && uv run mypy src/

# Lint frontend (eslint + tsc)
lint-frontend:
    cd frontend && pnpm lint
    cd frontend && pnpm exec tsc --noEmit

# Format all code
format: format-backend format-frontend

# Format backend
format-backend:
    cd backend && uv run ruff format .
    cd backend && uv run ruff check --fix .

# Format frontend
format-frontend:
    cd frontend && pnpm exec prettier --write src/

# Build frontend for production
build-frontend:
    cd frontend && pnpm build

# Start backend dev server with hot reload
dev-backend:
    cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend dev server
dev-frontend:
    cd frontend && pnpm dev
