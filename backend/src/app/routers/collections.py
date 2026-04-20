from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.repositories.collections import (
    count_items,
    create_collection,
    delete_collection,
    get_collection,
    list_collections,
)
from app.schemas.collection import CollectionCreate, CollectionRead
from app.services.ingestion import get_progress, walk_folder

router = APIRouter(prefix="/api/collections", tags=["collections"])

DATA_THUMBS_DIR = "./data/thumbs"


def _to_read(session: Session, collection_id: int) -> CollectionRead:
    col = get_collection(session, collection_id)
    if col is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    if col.id is None:
        raise HTTPException(status_code=500, detail="Collection has no ID after creation")
    return CollectionRead(
        id=col.id,
        name=col.name,
        source_folder=col.source_folder,
        created_at=col.created_at,
        item_count=count_items(session, col.id),
    )


@router.get("/", response_model=list[CollectionRead])
def list_collections_route(session: Session = Depends(get_session)) -> list[CollectionRead]:
    """List all collections."""
    cols = list_collections(session)
    return [
        CollectionRead(
            id=c.id,
            name=c.name,
            source_folder=c.source_folder,
            created_at=c.created_at,
            item_count=count_items(session, c.id) if c.id is not None else 0,
        )
        for c in cols
    ]


@router.post("/", response_model=CollectionRead, status_code=201)
def create_collection_route(
    body: CollectionCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> CollectionRead:
    """Create a collection and kick off image ingestion in the background."""
    col = create_collection(session, body.name, body.source_folder)
    if col.id is None:
        raise HTTPException(status_code=500, detail="Collection was not assigned an ID")
    background_tasks.add_task(walk_folder, col.id, body.source_folder, DATA_THUMBS_DIR)
    return CollectionRead(
        id=col.id,
        name=col.name,
        source_folder=col.source_folder,
        created_at=col.created_at,
        item_count=0,
    )


@router.get("/{collection_id}", response_model=CollectionRead)
def get_collection_route(
    collection_id: int,
    session: Session = Depends(get_session),
) -> CollectionRead:
    """Get a single collection by id."""
    return _to_read(session, collection_id)


@router.delete("/{collection_id}", status_code=204)
def delete_collection_route(
    collection_id: int,
    session: Session = Depends(get_session),
) -> None:
    """Delete a collection and all its items."""
    if not delete_collection(session, collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")


@router.get("/{collection_id}/ingestion-status")
def ingestion_status_route(collection_id: int) -> dict[str, object]:
    """Return live ingestion progress for a collection."""
    return get_progress(collection_id)
