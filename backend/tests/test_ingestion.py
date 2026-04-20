import os
import tempfile
from pathlib import Path

from sqlmodel import select

from app.models.collection import Collection
from app.models.item import Item
from app.services.ingestion import walk_folder

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_walk_folder_creates_items(session) -> None:  # type: ignore[no-untyped-def]
    """walk_folder creates one Item row per supported image file."""
    collection = Collection(name="test", source_folder=str(FIXTURES_DIR))
    session.add(collection)
    session.commit()
    session.refresh(collection)

    # Patch the module-level engine used inside walk_folder to use the test engine

    import app.services.ingestion as ingestion_module

    original_engine = ingestion_module.engine
    ingestion_module.engine = session.get_bind()  # type: ignore[attr-defined]

    try:
        with tempfile.TemporaryDirectory() as thumb_dir:
            walk_folder(collection.id, str(FIXTURES_DIR), thumb_dir)
    finally:
        ingestion_module.engine = original_engine

    items = list(session.exec(select(Item).where(Item.collection_id == collection.id)).all())
    assert len(items) == 3, f"expected 3 items, got {len(items)}"


def test_walk_folder_records_dimensions(session) -> None:  # type: ignore[no-untyped-def]
    """Each ingested item has non-null width and height."""
    collection = Collection(name="dims", source_folder=str(FIXTURES_DIR))
    session.add(collection)
    session.commit()
    session.refresh(collection)

    import app.services.ingestion as ingestion_module

    original_engine = ingestion_module.engine
    ingestion_module.engine = session.get_bind()  # type: ignore[attr-defined]

    try:
        with tempfile.TemporaryDirectory() as thumb_dir:
            walk_folder(collection.id, str(FIXTURES_DIR), thumb_dir)
    finally:
        ingestion_module.engine = original_engine

    items = list(session.exec(select(Item).where(Item.collection_id == collection.id)).all())
    assert all(item.width is not None and item.height is not None for item in items)
    first = items[0]
    assert first.width == 100
    assert first.height == 80


def test_walk_folder_generates_thumbnails(session) -> None:  # type: ignore[no-untyped-def]
    """walk_folder writes thumbnail files to thumb_dir."""
    collection = Collection(name="thumbs", source_folder=str(FIXTURES_DIR))
    session.add(collection)
    session.commit()
    session.refresh(collection)

    import app.services.ingestion as ingestion_module

    original_engine = ingestion_module.engine
    ingestion_module.engine = session.get_bind()  # type: ignore[attr-defined]

    try:
        with tempfile.TemporaryDirectory() as thumb_dir:
            walk_folder(collection.id, str(FIXTURES_DIR), thumb_dir)
            thumb_files = os.listdir(thumb_dir)

    finally:
        ingestion_module.engine = original_engine

    assert len(thumb_files) == 3
