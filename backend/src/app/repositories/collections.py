from sqlalchemy import func
from sqlmodel import Session, select

from app.models.collection import Collection
from app.models.item import Item


def list_collections(session: Session) -> list[Collection]:
    """Return all collections ordered by creation date descending."""
    return list(session.exec(select(Collection).order_by(Collection.created_at.desc())).all())  # type: ignore[attr-defined]


def get_collection(session: Session, collection_id: int) -> Collection | None:
    """Return a single collection by id, or None."""
    return session.get(Collection, collection_id)


def create_collection(session: Session, name: str, source_folder: str) -> Collection:
    """Insert and return a new collection row."""
    collection = Collection(name=name, source_folder=source_folder)
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection


def delete_collection(session: Session, collection_id: int) -> bool:
    """Delete a collection and its items. Returns True if deleted, False if not found."""
    collection = session.get(Collection, collection_id)
    if collection is None:
        return False
    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())
    for item in items:
        session.delete(item)
    session.delete(collection)
    session.commit()
    return True


def count_items(session: Session, collection_id: int) -> int:
    """Return the number of items belonging to a collection."""
    result = session.exec(
        select(func.count(Item.id)).where(Item.collection_id == collection_id)  # type: ignore[arg-type]
    ).one()
    return result or 0
