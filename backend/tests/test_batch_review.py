"""Tests for POST /api/items/batch-review."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, select

from app.models.collection import Collection
from app.models.item import Item
from app.models.review import ReviewRecord, ReviewStatus

# ── helpers ───────────────────────────────────────────────────────────────────


def _make_items(session: Session, count: int = 3) -> tuple[int, list[int]]:
    """Create a collection with *count* items; return (collection_id, [item_ids])."""
    col = Collection(name="batch-test", source_folder="/tmp")
    session.add(col)
    session.commit()
    session.refresh(col)
    assert col.id is not None

    item_ids: list[int] = []
    for i in range(count):
        item = Item(collection_id=col.id, filename=f"img{i}.jpg", path=f"/tmp/img{i}.jpg")
        session.add(item)
        session.commit()
        session.refresh(item)
        assert item.id is not None
        item_ids.append(item.id)

    return col.id, item_ids


# ── unit tests ────────────────────────────────────────────────────────────────


def test_batch_review_creates_records(session: Session) -> None:
    """batch_review creates a ReviewRecord for every item."""
    from app.routers.items import batch_review

    _, item_ids = _make_items(session, count=3)
    body: dict[str, object] = {"item_ids": item_ids, "status": "confirmed"}
    result = batch_review(body=body, session=session)

    assert result == {"updated": 3}

    records = list(session.exec(select(ReviewRecord)).all())
    assert len(records) == 3
    assert all(r.status == ReviewStatus.confirmed for r in records)


def test_batch_review_updates_existing(session: Session) -> None:
    """batch_review overwrites an existing review record rather than inserting a duplicate."""
    from app.routers.items import batch_review

    _, item_ids = _make_items(session, count=2)

    # First pass: confirm
    batch_review(body={"item_ids": item_ids, "status": "confirmed"}, session=session)

    # Second pass: flag
    result = batch_review(body={"item_ids": item_ids, "status": "flagged"}, session=session)
    assert result == {"updated": 2}

    records = list(session.exec(select(ReviewRecord)).all())
    assert len(records) == 2, "upsert must not create duplicates"
    assert all(r.status == ReviewStatus.flagged for r in records)


def test_batch_review_invalid_status(session: Session) -> None:
    """batch_review raises 422 for an unrecognised status value."""
    from fastapi import HTTPException

    from app.routers.items import batch_review

    _, item_ids = _make_items(session, count=1)
    with pytest.raises(HTTPException) as exc_info:
        batch_review(body={"item_ids": item_ids, "status": "nonsense"}, session=session)
    assert exc_info.value.status_code == 422


def test_batch_review_unknown_item(session: Session) -> None:
    """batch_review returns 404 when any item_id does not exist."""
    from fastapi import HTTPException

    from app.routers.items import batch_review

    _, item_ids = _make_items(session, count=1)
    with pytest.raises(HTTPException) as exc_info:
        batch_review(body={"item_ids": [99999], "status": "confirmed"}, session=session)
    assert exc_info.value.status_code == 404


def test_batch_review_empty_list(session: Session) -> None:
    """Passing an empty item_ids list updates zero items."""
    from app.routers.items import batch_review

    result = batch_review(body={"item_ids": [], "status": "confirmed"}, session=session)
    assert result == {"updated": 0}


def test_batch_review_with_override_label(session: Session) -> None:
    """override_label is stored correctly for all items."""
    from app.routers.items import batch_review

    _, item_ids = _make_items(session, count=2)
    batch_review(
        body={"item_ids": item_ids, "status": "overridden", "override_label": "zebra"},
        session=session,
    )
    records = list(session.exec(select(ReviewRecord)).all())
    assert all(r.override_label == "zebra" for r in records)


# ── HTTP integration tests ────────────────────────────────────────────────────
# Only tests that do NOT require DB access (no lifespan init_db dependency).


@pytest.mark.asyncio
async def test_batch_review_http_422_bad_status() -> None:
    """POST /api/items/batch-review returns 422 for an invalid status."""
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/items/batch-review",
            json={"item_ids": [], "status": "invalid_status"},
        )
        assert resp.status_code == 422
