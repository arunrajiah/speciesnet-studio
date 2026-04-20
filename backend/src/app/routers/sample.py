from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.collection import Collection
from app.repositories.collections import create_collection
from app.services.ingestion import walk_folder
from app.services.sample_data import ensure_sample_images

router = APIRouter(prefix="/api", tags=["sample"])

SAMPLE_COLLECTION_NAME = "Sample Data"
THUMBS_DIR = "./data/thumbs"


@router.post("/sample")
def load_sample_data(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Download sample images (if needed) and create a sample collection.

    Idempotent — returns the existing collection if one named 'Sample Data' already exists.
    """
    existing = session.exec(
        select(Collection).where(Collection.name == SAMPLE_COLLECTION_NAME)
    ).first()

    if existing:
        return {"collection_id": existing.id, "created": False}

    folder = ensure_sample_images()
    col = create_collection(session, SAMPLE_COLLECTION_NAME, folder)
    if col.id is None:
        raise HTTPException(status_code=500, detail="Sample collection was not assigned an ID")
    background_tasks.add_task(walk_folder, col.id, folder, THUMBS_DIR)

    return {"collection_id": col.id, "created": True}
