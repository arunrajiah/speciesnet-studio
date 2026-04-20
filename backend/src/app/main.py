import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import collections as collections_router
from .routers import export as export_router
from .routers import inference as inference_router
from .routers import items as items_router
from .routers import sample as sample_router

THUMBS_DIR = os.environ.get("THUMBS_DIR", "./data/thumbs")
IMAGES_DIR = os.environ.get("IMAGES_DIR", "./data/images")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise the database and ensure static directories exist on startup."""
    init_db()
    os.makedirs(THUMBS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="SpeciesNet Studio",
        version="0.1.0",
        description="Self-hostable review UI for SpeciesNet wildlife classifier predictions.",
        lifespan=lifespan,
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        """Return service liveness status."""
        return {"status": "ok"}

    application.include_router(collections_router.router)
    application.include_router(export_router.router)
    application.include_router(inference_router.router)
    application.include_router(items_router.router)
    application.include_router(sample_router.router)

    # Serve thumbnails and full-res images as static files
    application.mount("/thumbs", StaticFiles(directory=THUMBS_DIR, check_dir=False), name="thumbs")
    application.mount("/images", StaticFiles(directory=IMAGES_DIR, check_dir=False), name="images")

    # In combined single-image deployments, serve the compiled frontend from STATIC_DIR
    static_dir = os.environ.get("STATIC_DIR")
    if static_dir and os.path.isdir(static_dir):
        application.mount("/", StaticFiles(directory=static_dir, html=True), name="spa")

    return application


app = create_app()
