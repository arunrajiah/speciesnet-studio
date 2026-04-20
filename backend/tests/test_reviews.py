from sqlmodel import Session, select

from app.models.collection import Collection
from app.models.item import Item
from app.models.review import ReviewRecord, ReviewStatus
from app.repositories.reviews import upsert_review


def _make_item(session: Session) -> int:
    col = Collection(name="test", source_folder="/tmp")
    session.add(col)
    session.commit()
    session.refresh(col)

    item = Item(collection_id=col.id, filename="img.jpg", path="/tmp/img.jpg")
    session.add(item)
    session.commit()
    session.refresh(item)
    assert item.id is not None
    return item.id


def test_upsert_creates_review(session: Session) -> None:
    item_id = _make_item(session)
    record = upsert_review(session, item_id, ReviewStatus.confirmed)
    assert record.status == ReviewStatus.confirmed
    assert record.item_id == item_id


def test_upsert_updates_existing_review(session: Session) -> None:
    item_id = _make_item(session)
    upsert_review(session, item_id, ReviewStatus.confirmed)
    updated = upsert_review(
        session, item_id, ReviewStatus.overridden, override_label="fox"
    )
    rows = list(session.exec(select(ReviewRecord).where(ReviewRecord.item_id == item_id)).all())
    assert len(rows) == 1
    assert updated.status == ReviewStatus.overridden
    assert updated.override_label == "fox"


def test_upsert_stores_reviewer_note(session: Session) -> None:
    item_id = _make_item(session)
    record = upsert_review(session, item_id, ReviewStatus.flagged, reviewer_note="check blur")
    assert record.reviewer_note == "check blur"
